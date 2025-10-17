# src/handler.py (entry point for Lambda environment)

import json
import logging
from extractor import fetch_articles
from transformer import format_articles
from publisher import publish_to_kinesis

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    The main entry point for the AWS Lambda function.
    It expects an event with 'search_term' and optional 'date_from'.
    """
    logger.info(f"Lambda function invoked with event: {event}")

    # 1. Get inputs from the Lambda event dictionary
    search_term = event.get("search_term")
    date_from = event.get("date_from")  # <== Will be None if not provided

    if not search_term:
        logger.error("'search_term' not found in the event.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "search_term is a required field."}),
        }

    # 2. Call the ETP pipeline functions
    logger.info(f"--- Starting Pipeline for search term: {search_term} ---")

    # --- Step 1: Extract ---
    raw_articles = fetch_articles(search_term, date_from)
    if not raw_articles:
        logger.warning("Pipeline stopped: Could not retrieve any articles.")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "No articles found."}),
        }

    # --- Step 2: Transform ---
    formatted_articles = format_articles(raw_articles, search_term)
    if not formatted_articles:
        logger.error("Pipeline stopped: Failed to format articles.")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to format articles."}),
        }

    # --- Step 3: Publish ---
    success = publish_to_kinesis(formatted_articles)

    # 3. Return a standard Lambda response
    if success:
        message = f"Pipeline finished successfully! Published {len(formatted_articles)} articles."
        logger.info(message)
        return {"statusCode": 200, "body": json.dumps({"message": message})}
    else:
        message = "Pipeline finished with errors. Check logs for details."
        logger.error(message)
        return {"statusCode": 500, "body": json.dumps({"error": message})}
