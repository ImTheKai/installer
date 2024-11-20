
import unittest
from fetch_versions import fetch_latest_versions

class TestFetchVersions(unittest.TestCase):
    def test_fetch_versions(self):
        versions = fetch_latest_versions()
        self.assertIsInstance(versions, dict)
        self.assertIn("Percona Server for MySQL", versions)
