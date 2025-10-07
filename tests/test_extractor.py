# tests/test_extractor.py

import pytest
import requests
from src.extractor import fetch_articles

# 1. --- The "All good" Test ---
# We test the case where everything works as expected.
def test_fetch_articles_success(mocker):
    """
    Tests the successful fetching of articles by mocking a successful API response.
    """
    # Arrange: Prepare our fake data and mock object
    mock_api_response = {
        'response': {
            'status': 'ok',
            'results': [
                {'webTitle': 'Test Article 1', 'tags': ['test']},
                {'webTitle': 'Test Article 2', 'tags': ['test']},
                {'webTitle': 'Test Article 3', 'tags': ['test']}
            ]
        }
    }
    
    # We use mocker (from pytest-mock) to replace 'requests.get'
    # The path is 'src.extractor.requests.get' because that's where it's used.
    mock_get = mocker.patch('src.extractor.requests.get')
    
    # Configure the mock to return a fake response object
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_api_response
    mock_response.raise_for_status.return_value = None  # Do nothing when called
    mock_get.return_value = mock_response

    # Act: Call the function we are testing
    articles = fetch_articles(search_query='"test"')

    # Assert: Check if the function behaved as expected
    assert len(articles) == 3
    assert articles[0]['webTitle'] == 'Test Article 1'
    # Verify that requests.get was called once
    mock_get.assert_called_once()


# 2. --- The "HTTP Error" Test ---
# We test what happens if the API returns an error (e.g., 401 Unauthorized)
def test_fetch_articles_http_error(mocker, caplog):
    """
    Tests the function's behavior when an HTTP error occurs.
    It should log the error and return an empty list.
    """
    # Arrange: Configure the mock to simulate an HTTP error
    mock_get = mocker.patch('src.extractor.requests.get')
    
    # Configure the mock's response to raise an error when raise_for_status() is called
    mock_response = mocker.Mock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error")
    mock_get.return_value = mock_response

    # Act: Call the function
    articles = fetch_articles(search_query='"test"')

    # Assert: Check that the function handled the error gracefully
    assert articles == []  # Should return an empty list on failure
    assert "HTTP error occurred" in caplog.text  # Check if our error was logged
    assert "401" in caplog.text


# 3. --- The "Network Error" Test ---
# We test what happens if there's a network problem (e.g., can't connect)
def test_fetch_articles_request_exception(mocker, caplog):
    """
    Tests the function's behavior when a network request fails.
    It should log the error and return an empty list.
    """
    # Arrange: Configure the mock to raise a connection error directly
    mocker.patch(
        'src.extractor.requests.get', 
        side_effect=requests.exceptions.RequestException("Connection failed")
    )

    # Act: Call the function
    articles = fetch_articles(search_query='"test"')

    # Assert: Check that the function handled the error gracefully
    assert articles == []
    assert "A request error occurred" in caplog.text
    assert "Connection failed" in caplog.text