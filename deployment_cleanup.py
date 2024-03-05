import boto3
from semver.version import Version


class DeploymentCleaner():

    def __init__(self, client, dry_run=False):
        self.deployment_list = []
        self.s3_client = client
        self.dry_run = dry_run

    def _sort_deployment_list(self, deployment_list):
        deployment_list.sort(key=Version.parse)
        return deployment_list

    def _get_deployment_list(self):
        paginator = self.s3_client.get_paginator('list_objects')
        result = paginator.paginate(Bucket='deployments', Delimiter='/')

        list_of_deployments=[]
        for prefix in result.search('CommonPrefixes'):
            list_of_deployments.append(prefix.get('Prefix').strip('/'))
        return list_of_deployments

    def clean(self):
        deployments = self._get_deployment_list()
        sorted_deployments = self._sort_deployment_list(deployments)
        print(sorted_deployments)

def main():
    client = boto3.client(
        service_name='s3',
        endpoint_url='http://10.0.0.170:4566'
    )

    deploymentcleaner = DeploymentCleaner(client) 
    deploymentcleaner.clean()


if __name__ == "__main__":
    main()