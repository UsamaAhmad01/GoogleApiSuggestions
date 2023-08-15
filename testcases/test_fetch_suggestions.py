import unittest
from unittest.mock import Mock, patch
import json
from google_suggestion_api import fetch_suggestions


class TestFetchSuggestions(unittest.TestCase):

    @patch('GoogleSuggestonApi.aiohttp.ClientSession')
    async def test_successful_request(self, mock_session):
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text.return_value = json.dumps(["keyword", ["suggestion1", "suggestion2"]])
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_response

        keyword = "test"
        result = await fetch_suggestions(mock_session, keyword)

        self.assertEqual(result, (keyword, ["suggestion1", "suggestion2"]))

    @patch('GoogleSuggestonApi.aiohttp.ClientSession')
    async def test_failed_request(self, mock_session):
        mock_response = Mock()
        mock_response.status = 404
        mock_session.return_value.get.return_value.__aenter__.return_value = mock_response

        keyword = "test"
        result = await fetch_suggestions(mock_session, keyword)

        self.assertEqual(result, (keyword, None))
