import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import requests
from html.parser import HTMLParser
from google.adk.agents import LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL


def fetch_college_info(page: str = "contact") -> str:
    """Fetch information from the Global Academy of Technology (GAT) website."""
    urls = {"contact": "https://www.gat.ac.in/contact-us.html"}
    url = urls.get(page, urls["contact"])
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; educational-demo/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_parts = []
                self._skip = False
            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style", "nav", "header", "footer"):
                    self._skip = True
            def handle_endtag(self, tag):
                if tag in ("script", "style", "nav", "header", "footer"):
                    self._skip = False
            def handle_data(self, data):
                if not self._skip:
                    cleaned = data.strip()
                    if cleaned:
                        self.text_parts.append(cleaned)

        parser = TextExtractor()
        parser.feed(response.text)
        text = "\n".join(parser.text_parts)
        return text[:2000] if text else "No content found."
    except Exception as e:
        return f"Failed to fetch page: {e}"


college_data = fetch_college_info("contact")

root_agent = LlmAgent(
    name="GATInfoAgent",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are a helpful information assistant for Global Academy of Technology (GAT), "
                "Bengaluru. The user's message contains a question followed by live data fetched "
                "from the GAT website. Answer the question using that data. Be concise and helpful.\n\n"
                f"Live data from GAT website (gat.ac.in):\n{college_data}",
    description="Pattern 2 — Ask me anything about GAT. Try: 'What is the contact number and email address for GAT admissions?'",
)
