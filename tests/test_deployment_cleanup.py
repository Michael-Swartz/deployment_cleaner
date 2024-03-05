import unittest
from deployment_cleanup import DeploymentCleaner

class TestDeploymentCleanup(unittest.TestCase):

    def test_sort_deployment_list(self):
        """ test to ensure that we sort the deployment list correctly """
        list_of_deployments = ["3.0.4", "5.1.1", "1.0.1", "2.0.0", "1.4.0"]
        sorted_list = ["1.0.1", "1.4.0", "2.0.0", "3.0.4", "5.1.1"]
        self.assertEqual(DeploymentCleaner._sort_deployment_list(list_of_deployments), sorted_list)

