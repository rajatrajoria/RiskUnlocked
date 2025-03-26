import pytest
import requests
from unittest.mock import patch, Mock
from src.news_fetch import fetch_news, scrape_full_article

# --- Test Constants ---
MOCK_NEWS_API_RESPONSE = {
    "status": "ok",
    "totalResults": 2,
    "articles": [
        {
            "source": {"name": "Reuters"},
            "author": "John Doe",
            "title": "Morgan Stanley under investigation for fraud",
            "description": "Morgan Stanley is facing allegations of financial fraud.",
            "url": "https://example.com/article1",
        },
        {
            "source": {"name": "BBC"},
            "author": "Jane Smith",
            "title": "Wells Fargo involved in a lawsuit",
            "description": "Wells Fargo is under scrutiny due to legal challenges.",
            "url": "https://example.com/article2",
        },
    ],
}


# --- Test fetch_news() ---

@patch("app.news_scraper.requests.get")
def test_fetch_news_success(mock_get):
    """Test successful fetching of news from the API."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_NEWS_API_RESPONSE
    mock_get.return_value = mock_response

    company_name = "Morgan Stanley"
    articles = fetch_news(company_name)

    assert len(articles) == 2
    assert articles[0]["title"] == "Morgan Stanley under investigation for fraud"
    assert articles[1]["source"]["name"] == "BBC"


@patch("app.news_scraper.requests.get")
def test_fetch_news_api_failure(mock_get):
    """Test API failure with status code != 200."""
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.text = "API key invalid"
    mock_get.return_value = mock_response

    company_name = "Tesla"
    articles = fetch_news(company_name)

    assert articles == []


@patch("app.news_scraper.requests.get")
def test_fetch_news_empty_response(mock_get):
    """Test empty response from API."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok", "totalResults": 0, "articles": []}
    mock_get.return_value = mock_response

    company_name = "Wirecard"
    articles = fetch_news(company_name)

    assert articles == []


# --- Test scrape_full_article() ---

@patch("app.news_scraper.requests.get")
def test_scrape_full_article_success(mock_get):
    """Test successful article scraping."""
    mock_html = """
    <html>
        <body>
            <p>This is the first paragraph of the article.</p>
            <p>This is the second paragraph with more content.</p>
            <p>Short text.</p>
        </body>
    </html>
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = mock_html
    mock_get.return_value = mock_response

    url = "https://example.com/article1"
    content = scrape_full_article(url)

    assert "This is the first paragraph" in content
    assert "This is the second paragraph" in content
    assert "Short text" not in content


@patch("app.news_scraper.requests.get")
def test_scrape_full_article_no_content(mock_get):
    """Test article with no valid content."""
    mock_html = """
    <html>
        <body>
            <p>Short text.</p>
        </body>
    </html>
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = mock_html
    mock_get.return_value = mock_response

    url = "https://example.com/article2"
    content = scrape_full_article(url)

    assert content == "Full article not available."


@patch("app.news_scraper.requests.get")
def test_scrape_full_article_error(mock_get):
    """Test error while scraping article."""
    mock_get.side_effect = Exception("Connection error")

    url = "https://example.com/article3"
    content = scrape_full_article(url)

    assert "Error fetching full article" in content


@patch("app.news_scraper.requests.get")
def test_scrape_full_article_non_200_response(mock_get):
    """Test non-200 response when fetching article."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    url = "https://example.com/not_found"
    content = scrape_full_article(url)

    assert content == "Full article not available."


# --- Edge Case Tests ---

def test_fetch_news_no_api_key(monkeypatch):
    """Test error when API key is missing."""
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    with pytest.raises(ValueError, match="NEWS_API_KEY environment variable is not set!"):
        fetch_news("Tesla")
