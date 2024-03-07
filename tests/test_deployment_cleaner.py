import unittest
import datetime
from deployment_cleaner import DeploymentCleaner


class TestDeploymentCleanup(unittest.TestCase):
    def setUp(self):
        """Setup the deploymentcleaner for testing"""
        self.deploymentcleaner = DeploymentCleaner(
            deployments_to_keep=2, bucket="deployments"
        )

    def test_get_deployment(self):
        """test to ensure that we get the correct deployment name from an s3 key"""
        test_key = "gy76yt5r/images/hey.png"
        test_deployment = "gy76yt5r"
        self.assertEqual(
            self.deploymentcleaner._get_deployment(test_key), test_deployment
        )

    def test_sort_list_of_objects(self):
        """tests to ensure that we sort the list of objects correctly by time, newest deployment is first"""
        unsorted_list = [
            {"s3key": "michael", "time": datetime.datetime(2022, 3, 6, 1, 13, 53)},
            {"s3key": "hi", "time": datetime.datetime(2024, 3, 6, 1, 14, 14)},
            {"s3key": "there", "time": datetime.datetime(2023, 3, 6, 5, 11, 4)},
        ]
        sorted_list = [
            {"s3key": "hi", "time": datetime.datetime(2024, 3, 6, 1, 14, 14)},
            {"s3key": "there", "time": datetime.datetime(2023, 3, 6, 5, 11, 4)},
            {"s3key": "michael", "time": datetime.datetime(2022, 3, 6, 1, 13, 53)},
        ]
        self.assertEqual(
            self.deploymentcleaner._sort_list_of_objects(unsorted_list), sorted_list
        )

    def test_filter_list_of_objects(self):
        """
        test to ensure that we filter the list of sorted objects down to unique deployment keys based
        the time that the first object of that deployment was PUT into the bucket
        """
        unfiltered_list = [
            {
                "s3key": "45tgbvfr/css/font.css",
                "time": datetime.datetime(2023, 3, 6, 1, 12, 52),
                "deployment": "3",
            },
            {
                "s3key": "45tgbvfr/root.html",
                "time": datetime.datetime(2023, 1, 6, 1, 12, 52),
                "deployment": "3",
            },
            {
                "s3key": "mki87ujh/css/font.css",
                "time": datetime.datetime(2022, 1, 6, 1, 13, 13),
                "deployment": "2",
            },
            {
                "s3key": "mki87ujh/root.html",
                "time": datetime.datetime(2022, 3, 6, 1, 13, 13),
                "deployment": "2",
            },
            {
                "s3key": "gy76yt5r/css/font.css",
                "time": datetime.datetime(2021, 1, 6, 1, 13, 33),
                "deployment": "1",
            },
            {
                "s3key": "gy76yt5r/root.html",
                "time": datetime.datetime(2021, 3, 6, 1, 13, 33),
                "deployment": "1",
            },
        ]

        filtered_list = [
            {
                "s3key": "45tgbvfr/root.html",
                "time": datetime.datetime(2023, 1, 6, 1, 12, 52),
                "deployment": "3",
            },
            {
                "s3key": "mki87ujh/css/font.css",
                "time": datetime.datetime(2022, 1, 6, 1, 13, 13),
                "deployment": "2",
            },
            {
                "s3key": "gy76yt5r/css/font.css",
                "time": datetime.datetime(2021, 1, 6, 1, 13, 33),
                "deployment": "1",
            },
        ]

        self.assertEqual(
            self.deploymentcleaner._filter_list_of_objects(unfiltered_list),
            filtered_list,
        )

    def test_trim_list_of_deployments(self):
        """Test to ensure we trim the list of deployments down to the ones we want to delete correctly"""
        untrimmed_list = [
            {
                "time": datetime.datetime(2024, 3, 6, 1, 14, 34),
                "deployment": "hy76tgfd",
            },
            {
                "time": datetime.datetime(2024, 3, 6, 1, 14, 14),
                "deployment": "cde34drf",
            },
            {
                "time": datetime.datetime(2024, 3, 6, 1, 13, 53),
                "deployment": "2wse34dx",
            },
            {
                "time": datetime.datetime(2024, 3, 6, 1, 13, 33),
                "deployment": "gy76yt5r",
            },
            {
                "time": datetime.datetime(2024, 3, 6, 1, 13, 13),
                "deployment": "mki87ujh",
            },
            {
                "time": datetime.datetime(2024, 3, 6, 1, 12, 52),
                "deployment": "45tgbvfr",
            },
        ]

        trimmed_list = [
            {
                "time": datetime.datetime(2024, 3, 6, 1, 13, 53),
                "deployment": "2wse34dx",
            },
            {
                "time": datetime.datetime(2024, 3, 6, 1, 13, 33),
                "deployment": "gy76yt5r",
            },
            {
                "time": datetime.datetime(2024, 3, 6, 1, 13, 13),
                "deployment": "mki87ujh",
            },
            {
                "time": datetime.datetime(2024, 3, 6, 1, 12, 52),
                "deployment": "45tgbvfr",
            },
        ]
        deployments_to_retain = 2
        self.assertEqual(
            self.deploymentcleaner._trim_list_of_deployments(
                untrimmed_list, deployments_to_retain
            ),
            trimmed_list,
        )

        # Test to ensure we exit with an error code of 1 if there's an invalid number of deployments to retain passed
        invalid_deployments_to_retain = 7
        with self.assertRaises(SystemExit) as e:
            self.deploymentcleaner._trim_list_of_deployments(
                untrimmed_list, invalid_deployments_to_retain
            )
        self.assertEqual(e.exception.code, 1)
