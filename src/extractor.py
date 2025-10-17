import requests
import logging
import config
from pprint import pprint

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_articles(search_query: str, date_from: str = None) -> list:
    """
    Fetches articles from The Guardian API based on a search query and optional date.

    Args:
        search_query (str): The term to search for. Should be phrase-searchable (e.g., '"machine learning"').
        date_from (str, optional): The start date in 'YYYY-MM-DD' format. Defaults to None.

    Returns:
        list: A list of article dictionaries from the API response, or an empty list on failure.
    """
    params = {
        "q": search_query,
        "api-key": config.API_KEY,
        "page-size": 10,
        "show-tags": "all",
        "show-fields": "body",
    }

    # Add the from-date to the parameters only if it's provided by user othersise its omitted
    if date_from:
        params["from-date"] = date_from

    logging.info(
        f"Fetching articles for query: '{search_query}' with params: {params.get('from-date', 'N/A')}"
    )

    try:
        response = requests.get(config.BASE_URL, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        results = data.get("response", {}).get("results", [])
        logging.info(f"Successfully found {len(results)} articles.")
        return results

    except requests.exceptions.HTTPError as http_err:
        logging.error(
            f"HTTP error occurred: {http_err} - Status Code: {response.status_code}"
        )
        return []
    except requests.exceptions.RequestException as req_err:
        logging.error(f"A request error occurred: {req_err}")
        return []
