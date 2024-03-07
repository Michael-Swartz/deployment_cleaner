import argparse
import datetime
import logging
from logging import StreamHandler, Formatter
from itertools import groupby
import sys

import boto3

# TODO: Make log level an arg that can be passed
# TODO: Setup logging to a file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(
    Formatter(
        fmt="[%(asctime)s -- %(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"
    )
)
logger.addHandler(handler)


class DeploymentCleaner:
    def __init__(
        self,
        deployments_to_keep,
        bucket,
        dry_run=False,
        endpoint_url=None,
    ):

        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.deployment_list = []
        self.deployments_to_keep = deployments_to_keep
        self.dry_run = dry_run

        self._setup_client()

    def _setup_client(self) -> None:
        """sets up the boto3 client"""
        # We setup the S3 client differently depending on if we passed in an a custom
        # endpoint URL to the script
        logger.debug("Setting up S3 client")
        if self.endpoint_url is not None:
            self.s3_client = boto3.client(
                service_name="s3", endpoint_url=self.endpoint_url
            )
        else:
            self.s3_client = boto3.client(service_name="s3")

    def _get_objects(self) -> list:
        """
        calls S3 and retrieves a list of objects from the bucket from which we will filter down to a list
        of deployments descending based on when they were deployed
        """
        paginator = self.s3_client.get_paginator("list_objects")
        response_iterator = paginator.paginate(Bucket=self.bucket)
        list_of_objects = []
        for page in response_iterator:
            for object in page["Contents"]:
                key = object["Key"]
                time = object["LastModified"]
                deployment = self._get_deployment(key)
                obj = {"s3key": key, "time": time, "deployment": deployment}
                list_of_objects.append(obj)
        return list_of_objects

    def _sort_list_of_objects(self, list_of_objects) -> list:
        """returns a sorted list of the objeccts based on the last modified time"""
        return sorted(list_of_objects, key=lambda d: d["time"], reverse=True)

    def _filter_list_of_objects(self, sorted_list_of_objects) -> list:
        """returns a list unique deployments sorted by the oldest object in that deployment based on last modified time"""
        filtered_list = [
            min(b, key=lambda t: t["time"])
            for a, b in groupby(sorted_list_of_objects, key=lambda d: d["deployment"])
        ]
        return filtered_list

    def _get_deployment(self, key) -> str:
        """Takes in an s3 key and will return the deployment (the root of the key when deliniated by /)"""
        split_key = key.split("/")
        return split_key[0]

    def _trim_list_of_deployments(
        self, filtered_deployment_list, deployments_to_retain
    ) -> list:
        """returns a list of deployments to be removed based on the number of deployments to retain"""
        if deployments_to_retain >= len(filtered_deployment_list):
            # TODO: Make it clearer as to why the number of deployments to retain is invalid
            logger.error("Invalid number of deployments to retain")
            sys.exit(1)
        return filtered_deployment_list[deployments_to_retain:]

    def clean(self) -> None:
        # Collect all objects in the bucket
        object_list = self._get_objects()
        # Sort list of objects based on last modified date of the object
        sorted_obj_list = self._sort_list_of_objects(object_list)
        # Filter the list of objects down to a list on unique deployments
        filtered_deployment_list = self._filter_list_of_objects(sorted_obj_list)
        # Build a list of deployments that will be deleted
        deployments_to_delete = self._trim_list_of_deployments(
            filtered_deployment_list, self.deployments_to_keep
        )

        if self.dry_run:
            logger.info(
                "Running as a dry run, these are the deployments that would be deleted:"
            )
            for d in deployments_to_delete:
                logger.info(f"Deployment: {d['deployment']}")
        else:
            for d in deployments_to_delete:
                deployment = d["deployment"]
                logger.info(f"Deleting deployment: {deployment}")
                # We iterate back through the original list of objects to pull out objects that need to be deleted for
                # a specific deployment
                obj_to_del = [
                    o.get("s3key") for o in object_list if o["deployment"] == deployment
                ]
                s3_del_payload = []
                for obj in obj_to_del:
                    s3_del_payload.append({"Key": obj})

                self.s3_client.delete_objects(
                    Bucket=self.bucket, Delete={"Objects": s3_del_payload}
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        help="Run script in dry-run mode to see objects that will be deleted without deleting them.",
        action="store_true",
    )
    parser.add_argument(
        "--deployments",
        help="Number of deployments to retain, this will retain the X number of most recent deployments",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--bucket",
        help="Bucket from which you will delete the objects from",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--endpoint-url",
        help="Optional argument for specifying a different s3 endpoint URL. Useful for local testing with localstack",
        type=str,
    )

    args = parser.parse_args()

    logger.info("Starting deployment cleaner...")
    deploymentcleaner = DeploymentCleaner(
        bucket=args.bucket,
        deployments_to_keep=args.deployments,
        dry_run=args.dry_run,
        endpoint_url=args.endpoint_url,
    )
    deploymentcleaner.clean()
    logger.info("Finished")


if __name__ == "__main__":
    main()
