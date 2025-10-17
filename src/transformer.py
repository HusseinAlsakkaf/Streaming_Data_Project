# src/transformer.py

import logging
import re

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def _clean_html(raw_html: str) -> str:
    """A simple helper function to strip HTML tags from a string."""
    # Compile a regex pattern that matches any HTML tag (e.g. <p>, </div>, <a href="...">)
    tag_pattern = re.compile("<.*?>")
    # Remove all HTML tags by replacing anything that matches the pattern with an empty string
    cleantext = re.sub(tag_pattern, "", raw_html)
    #  Replace newlines with spaces and strip leading/trailing whitespace for a clean, single line result
    return cleantext.replace("\n", " ").strip()


def format_articles(raw_articles: list, search_term: str) -> list[dict]:
    """
    Formats a list of raw articles from the Guardian API into the required JSON structure.
    """
    # if input list is empty, return empty list
    if not raw_articles:
        logging.warning("Received an empty list of articles to format.")
        return []

    logging.info(f"Transforming {len(raw_articles)} articles...")
    formatted_articles = []

    for article in raw_articles:
        # Safely extract the article body HTML from nested fields
        body_html = article.get("fields", {}).get("body", "")
        # use helper function to clean HTML tags
        cleaned_body = _clean_html(body_html)
        # Create a preview by truncating to the first 1000 characters
        content_preview = (
            cleaned_body[:1000] + "..." if len(cleaned_body) > 1000 else cleaned_body
        )

        formatted_article = {
            # format to match the project brief's MVP
            "webPublicationDate": article.get("webPublicationDate", "N/A"),
            "webTitle": article.get("webTitle", "N/A"),
            "webUrl": article.get("webUrl", "N/A"),
            #  fields we are adding
            "search_term": search_term,
            "content_preview": content_preview,
        }
        formatted_articles.append(formatted_article)

    logging.info("Finished transforming articles.")
    return formatted_articles
