# src/publisher.py

import json
import logging
import uuid
import boto3
from botocore.exceptions import ClientError
from src import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def publish_to_kinesis(formatted_articles: list[dict]) -> bool:
    """
    Publishes a list of formatted articles to an AWS Kinesis Data Stream.

    Args:
        formatted_articles (list[dict]): The list of articles from the transformer.

    Returns:
        bool: True if publishing was successful (or partially successful), False otherwise.
    """
    if not formatted_articles:
        logging.warning("Received an empty list of articles to publish. Skipping.")
        return True  
    try:
        kinesis_client = boto3.client("kinesis", region_name=config.AWS_REGION)
    except Exception as e:
        logging.error(f"Failed to create Boto3 Kinesis client: {e}")
        return False

    logging.info(
        f"Preparing to publish {len(formatted_articles)} articles to Kinesis stream: {config.KINESIS_STREAM_NAME}"
    )

    
    records = []
    for article in formatted_articles:
        record = {
            # serialize the dict to a JSON string, then encode to UTF-8.
            "Data": json.dumps(article).encode("utf-8"),
            # PartitionKey is used by Kinesis to distribute data among shards.
            "PartitionKey": str(uuid.uuid4()),
        }
        records.append(record)

    try:
        response = kinesis_client.put_records(
            StreamName=config.KINESIS_STREAM_NAME, Records=records
        )

        failed_record_count = response.get("FailedRecordCount", 0)
        if failed_record_count > 0:
            logging.error(
                f"Publishing to Kinesis failed for {failed_record_count} records."
            )
            return False  
        
        logging.info("Successfully published all records to Kinesis.")
        return True

    except ClientError as e:
        logging.error(f"An AWS client error occurred: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during publishing: {e}")
        return False
