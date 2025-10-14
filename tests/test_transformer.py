# tests/test_transformer.py

from src.transformer import format_articles

def test_format_articles_success():
    """
    Tests that the transformer correctly formats a list of raw articles,
    including creating a clean content preview.
    """
    # Arrange: Create a sample of the raw data from the extractor
    raw_articles_sample = [
        {
            'webTitle': 'Article One',
            'webUrl': 'http://example.com/one',
            'webPublicationDate': '2023-01-01T00:00:00Z',
            'fields': {
                'body': '<p>This is the <b>body</b> of the first article.</p>'
            }
        },
        {
            'webTitle': 'Article Two',
            'webUrl': 'http://example.com/two',
            'webPublicationDate': '2023-01-02T00:00:00Z',
            'fields': {
                'body': 'Just plain text. No HTML.'
            }
        }
    ]
    search_term = '"testing"'

    # Act: Call the function we are testing
    formatted = format_articles(raw_articles_sample, search_term)

    # Assert: Check the results
    assert len(formatted) == 2
    # Check the first article in detail
    assert formatted[0]['search_term'] == '"testing"'
    assert formatted[0]['webTitle'] == 'Article One'
    assert formatted[0]['webPublicationDate'] == '2023-01-01T00:00:00Z'
    assert formatted[0]['webUrl'] == 'http://example.com/one' 
    assert formatted[0]['content_preview'] == 'This is the body of the first article.'

def test_format_articles_empty_input():
    """
    Tests that the transformer returns an empty list when given an empty list.
    """
    # Arrange
    empty_list = []
    
    # Act
    formatted = format_articles(empty_list, '"testing"')

    # Assert
    assert formatted == []

def test_format_articles_missing_fields():
    """
    Tests that the transformer handles articles with missing fields gracefully.
    """
    # Arrange: An article missing the 'fields' and 'body'
    raw_articles_sample = [
        {
            'webTitle': 'Article With Missing Body',
            'webUrl': 'http://example.com/missing',
            'webPublicationDate': '2023-01-03T00:00:00Z',
            # 'fields' key is completely missing
        }
    ]

    # Act
    formatted = format_articles(raw_articles_sample, '"testing"')

    # Assert
    assert len(formatted) == 1
    assert formatted[0]['webTitle'] == 'Article With Missing Body'
    assert formatted[0]['content_preview'] == '' 


