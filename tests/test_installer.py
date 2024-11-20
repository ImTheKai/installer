
import unittest
from unittest.mock import patch
from installer import enable_repository

class TestInstaller(unittest.TestCase):
    @patch("os.system")
    def test_enable_repository_success(self, mock_system):
        mock_system.return_value = 0
        result = enable_repository("pdps", "8.0")
        self.assertTrue(result)
