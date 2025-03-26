import unittest
from unittest.mock import patch, Mock
import requests
from src.Sector import get_cik_by_name, get_sector  # Update to your filename

class TestCIKFunctions(unittest.TestCase):

    @patch("requests.get")
    def test_get_cik_by_name_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "1": {"title": "Wells Fargo", "cik_str": 72971},
            "2": {"title": "Google Inc.", "cik_str": 1652044}
        }
        mock_get.return_value = mock_response

        result = get_cik_by_name("Wells Fargo")
        self.assertEqual(result, ("Wells Fargo", "0000072971"))

    @patch("requests.get")
    def test_get_cik_by_name_no_match(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "1": {"title": "Google Inc.", "cik_str": 1652044},
            "2": {"title": "Amazon Inc.", "cik_str": 1018724}
        }
        mock_get.return_value = mock_response

        result = get_cik_by_name("Unknown Company")
        self.assertIsNone(result)

    @patch("requests.get")
    def test_get_cik_by_name_api_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = get_cik_by_name("Wells Fargo")
        self.assertIsNone(result)

    @patch("requests.get")
    def test_get_cik_by_name_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        result = get_cik_by_name("Wells Fargo")
        self.assertIsNone(result)

    # ------------------- get_sector() Tests -------------------

    @patch("requests.get")
    def test_get_sector_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sicDescription": "National Commercial Banks"}
        mock_get.return_value = mock_response

        result = get_sector("0000072971")
        self.assertEqual(result, "National Commercial Banks")

    @patch("requests.get")
    def test_get_sector_unknown(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"randomKey": "No SIC"}
        mock_get.return_value = mock_response

        result = get_sector("0000072971")
        self.assertEqual(result, "Unknown")

    @patch("requests.get")
    def test_get_sector_api_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = get_sector("0000072971")
        self.assertIsNone(result)

    @patch("requests.get")
    def test_get_sector_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        result = get_sector("0000072971")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
