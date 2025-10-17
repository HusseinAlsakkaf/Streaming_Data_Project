# tests/test_publisher.py

import os
import boto3
import json
from moto import mock_aws
from src.publisher import publish_to_kinesis

SAMPLE_ARTICLES = [
    {
        "webTitle": "Test Article 1",
        "webUrl": "http://example.com/1",
        "webPublicationDate": "2025-01-01T00:00:00Z",
        "search_term": '"testing"',
        "content_preview": "This is a test.",
    }
]


# --- "Successful Publish" Test ---
@mock_aws
def test_publish_to_kinesis_success(mocker):
    """
    Tests that articles are successfully published to a Kinesis stream.
    """
    # Arrange: Set up the fake AWS environment and resources
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

    stream_name = "guardian_content"
    # Create the fake stream
    kinesis_client = boto3.client("kinesis", region_name="eu-west-2")
    kinesis_client.create_stream(StreamName=stream_name, ShardCount=1)

    mocker.patch("src.publisher.boto3.client", return_value=kinesis_client)

    # Act: Call the function we want to test
    success = publish_to_kinesis(SAMPLE_ARTICLES)

    # Assert: Check if the function behaved as expected
    assert success is True

    # Assert that the data actually arrived in the fake stream
    response = kinesis_client.describe_stream(StreamName=stream_name)
    shard_id = response["StreamDescription"]["Shards"][0]["ShardId"]

    iterator = kinesis_client.get_shard_iterator(
        StreamName=stream_name, ShardId=shard_id, ShardIteratorType="TRIM_HORIZON"
    )["ShardIterator"]

    records_response = kinesis_client.get_records(ShardIterator=iterator)
    assert len(records_response["Records"]) == 1

    data_in_stream = json.loads(records_response["Records"][0]["Data"])
    assert data_in_stream["webTitle"] == "Test Article 1"


# --- "Stream Not Found" Test ---
@mock_aws
def test_publish_to_kinesis_stream_not_found(mocker, caplog):
    """
    Tests that the function handles a non-existent stream gracefully.
    """
    # Arrange
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

    # We still create a client, but we dont create the stream.
    kinesis_client = boto3.client("kinesis", region_name="eu-west-2")

    # Patch boto3.client
    mocker.patch("src.publisher.boto3.client", return_value=kinesis_client)

    # Act
    success = publish_to_kinesis(SAMPLE_ARTICLES)

    # Assert
    assert success is False
    assert "An AWS client error occurred" in caplog.text
    assert "not found" in caplog.text.lower()


# --- "Empty List" Test ---
def test_publish_to_kinesis_empty_list(caplog):
    """
    Tests that the function handles an empty list of articles correctly.
    """
    # Arrange
    empty_articles = []
    # Act
    success = publish_to_kinesis(empty_articles)
    # Assert
    assert success is True
    assert "Received an empty list of articles to publish. Skipping." in caplog.text
