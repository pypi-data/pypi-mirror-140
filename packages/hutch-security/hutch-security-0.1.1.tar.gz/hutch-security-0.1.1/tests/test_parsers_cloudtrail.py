"""Implements CloudTrail parser test cases."""

import os
import unittest

from hutch.security.parsers import cloudtrail


class ParsersCloudtrailTestCase(unittest.TestCase):
    """Implements an example set of tests."""

    def setUp(self):
        """Ensure the application is setup for testing."""
        self.fixtures_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures/parsers/cloudtrail/"
        )

    def tearDown(self):
        """Ensure everything is torn down between tests."""
        pass

    def test_user_identity(self):
        """Ensures a user identity can be extracted from relevant trails."""
        expected = "someservice-5d798fcd-bd00-4a43-9fb8-b820bc96fd7c"
        candidate = open(
            os.path.join(self.fixtures_path, "001-s3-inventory-identity.json"), "r"
        ).read()

        self.assertEqual(cloudtrail.user_identity(candidate), expected)

    def test_asg_name(self):
        """Ensures an auto scaling group name can be extracted from relevant trails."""
        expected = "test-asg"
        candidate = open(
            os.path.join(self.fixtures_path, "002-ec2-asg-run.json"), "r"
        ).read()

        self.assertEqual(cloudtrail.asg_name(candidate), expected)
