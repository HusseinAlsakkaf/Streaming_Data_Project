# dashboard.py

import streamlit as st
import boto3
import json
import time
import pandas as pd

# --- AWS Kinesis Configuration ---
STREAM_NAME = "guardian_content"
AWS_REGION = "eu-west-2"
# Streamlit App Setup
st.set_page_config(layout="wide")
st.title("Guardian Articles Kinesis Stream Viewer")


# --- Step 1: A function to fetch ALL data from the stream ---
@st.cache_data(ttl=60)
def get_all_records_from_stream(stream_name, region):
    """
    Connects to Kinesis and reads all available records from all shards.
    It will only re-run if the input arguments change or after a timeout.
    """
    try:
        kinesis_client = boto3.client("kinesis", region_name=region)
        response = kinesis_client.describe_stream(StreamName=stream_name)
        shards = response["StreamDescription"]["Shards"]
    except Exception as e:
        st.error(f"Failed to connect to stream '{stream_name}'. Error: {e}")
        return []

    all_records = []

    for shard in shards:
        shard_id = shard["ShardId"]
        try:
            iterator_response = kinesis_client.get_shard_iterator(
                StreamName=stream_name,
                ShardId=shard_id,
                ShardIteratorType="TRIM_HORIZON",
            )
            shard_iterator = iterator_response["ShardIterator"]
            # Fetch Records Until Done
            while True:
                records_response = kinesis_client.get_records(
                    ShardIterator=shard_iterator, Limit=1000
                )
                records = records_response["Records"]

                if not records:
                    break  # Exit loop if there are no more records

                for record in records:
                    all_records.append(json.loads(record["Data"].decode("utf-8")))

                shard_iterator = records_response["NextShardIterator"]
                time.sleep(0.2)  #  avoid hitting limits

        except Exception as e:
            st.warning(f"Could not read from shard {shard_id}. Error: {e}")

    st.success(f"Fetched {len(all_records)} total records from the stream.")
    return all_records  # list of dicts


# --- Main Dashboard ---

# Fetch the data
all_articles = get_all_records_from_stream(STREAM_NAME, AWS_REGION)

if not all_articles:
    st.warning(
        "No articles found in the stream. Try running the Lambda function first."
    )
else:
    # --- Step 2: Create the filter UI (Sidebar UI) ---

    # Get a list of all unique search terms from the data
    unique_search_terms = sorted(
        list(set(article.get("search_term", "N/A") for article in all_articles))
    )

    # Add an "All" option to the beginning of the list
    filter_options = ["All"] + unique_search_terms

    # Create the dropdown menu in the sidebar
    selected_term = st.sidebar.selectbox(
        "Filter by Search Term:", options=filter_options
    )

    st.sidebar.info(f"Showing results for: **{selected_term}**")

    # --- Step 3: Display the filtered results ---

    if selected_term == "All":
        articles_to_display = all_articles
    else:
        articles_to_display = [
            article
            for article in all_articles
            if article.get("search_term") == selected_term
        ]

    st.header(f"Displaying {len(articles_to_display)} articles")
    st.write("---")

    # Loop through and display the filtered articles
    for article in reversed(articles_to_display):  # Show newest first
        st.subheader(article.get("webTitle", "No Title"))
        st.markdown(f"**URL:** [{article.get('webUrl')}]({article.get('webUrl')})")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Published:** {article.get('webPublicationDate', 'N/A')}")
        with col2:
            st.write(f"**Original Search:** `{article.get('search_term', 'N/A')}`")

        with st.expander("Show Content Preview"):
            st.write(article.get("content_preview", "No preview available."))

        st.write("---")
