# Same pattern as research-agent but standalone functions
# (not LangChain tools) so the debate loop controls them directly.

import os
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from tavily import TavilyClient


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using Tavily and return formatted results."""
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query, max_results=max_results)
        results = []
        for r in response["results"]:
            results.append(
                f"Title: {r['title']}\n"
                f"URL:   {r['url']}\n"
                f"Info:  {r['content']}\n"
            )
        return "\n---\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search failed: {str(e)}"


def scrape_page(url: str) -> str:
    """Fetch and clean the text content of a web page."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [l.strip() for l in text.splitlines()]
        cleaned = "\n".join(l for l in lines if l)
        return cleaned[:4000] + "\n[truncated]" if len(cleaned) > 4000 else cleaned
    except Exception as e:
        return f"Could not scrape {url}: {str(e)}"


def save_report(content: str, topic: str = "report") -> str:
    """Save the final report to the reports/ folder."""
    Path("reports").mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = topic[:40].replace(" ", "_").lower()
    filepath = f"reports/{slug}_{timestamp}.md"
    Path(filepath).write_text(content, encoding="utf-8")
    return filepath