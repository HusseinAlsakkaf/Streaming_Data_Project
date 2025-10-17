# src/main.py (entry point for local environment)

import argparse
from extractor import fetch_articles
from transformer import format_articles
from publisher import publish_to_kinesis

# FOR HELP RUN 'python3 src/main.py --help'
def main():
    """The main function to run the full ETP (Extract, Transform, Publish) pipeline."""
    parser = argparse.ArgumentParser(
        description="Fetch, format, and publish articles from The Guardian."
    )
    parser.add_argument(
        "search_term", help="The search phrase (e.g., '\"machine learning\"')."
    )
    parser.add_argument("--date-from", help="Optional start date in YYYY-MM-DD format.")
    args = parser.parse_args()

    print(f"--- Starting Pipeline for search term: {args.search_term} ---")

    # --- Step 1: Extract ---
    raw_articles = fetch_articles(args.search_term, args.date_from)
    if not raw_articles:
        print("Pipeline stopped: Could not retrieve any articles.")
        return

    # --- Step 2: Transform ---
    formatted_articles = format_articles(raw_articles, args.search_term)
    if not formatted_articles:
        print("Pipeline stopped: Failed to format articles.")
        return
    print(f"Successfully transformed {len(formatted_articles)} articles.")

    # --- Step 3: Publish ---
    success = publish_to_kinesis(formatted_articles)
    if success:
        print("--- Pipeline finished successfully! ---")
    else:
        print("--- Pipeline finished with errors. Check logs. ---")


if __name__ == "__main__":
    main()
