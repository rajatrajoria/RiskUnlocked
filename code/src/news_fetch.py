import requests
from bs4 import BeautifulSoup
import json
import os


# API_KEY = os.environ.get("NEWS_API_KEY")
API_KEY = "7454a3e8c68040abae666e5b9aa6a4b0"

if not API_KEY:
    raise ValueError("NEWS_API_KEY environment variable is not set!")

def fetch_news(company_name):
    url = f"https://newsapi.org/v2/everything?q={company_name} lawsuit OR fraud OR sanction&apiKey={API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"⚠️ Error fetching news for {company_name}: {response.text}")
        return []

    return response.json().get("articles", [])

def scrape_full_article(url):

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")


        paragraphs = soup.find_all("p")
        article_text = "\n".join([p.get_text() for p in paragraphs if len(p.get_text()) > 20])

        return article_text.strip() if article_text else "Full article not available."
    except Exception as e:
        return f"Error fetching full article: {e}"


companies = ["Morgan Stanley", "Wells Fargo", "Tesla", "Wirecard"]

news_data = {}

for company in companies:
    print(f"Fetching news for {company}...")
    news_articles = fetch_news(company)


    for article in news_articles:
        article["full_content"] = scrape_full_article(article["url"])

    news_data[company] = news_articles

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
save_path = os.path.join(root_dir, "artifacts", "arch", "news_with_full_content.json")


os.makedirs(os.path.dirname(save_path), exist_ok=True)


with open(save_path, "w", encoding="utf-8") as file:
    json.dump(news_data, file, indent=4, ensure_ascii=False)

print(f"News data with full content saved to {save_path}")
