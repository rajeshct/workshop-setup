import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import requests
from html.parser import HTMLParser
from google.adk.agents import LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL, setup_opik
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

setup_opik()


def fetch_college_info(page: str = "contact") -> str:
    """Fetch live information from the Global Academy of Technology (GAT) website."""
    urls = {"contact": "https://www.gat.ac.in/contact-us.html"}
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; educational-demo/1.0)"}
        response = requests.get(urls.get(page, urls["contact"]), headers=headers, timeout=10)
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


root_agent = LlmAgent(
    name="GATInfoAgent",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="When the conversation starts, greet the user with: 'Hi! I am the GAT Assistant. How can I help you today?' "
                "You are a helpful information assistant for Global Academy of Technology (GAT), Bengaluru. "
                "Use the fetch_college_info tool to get live data from the GAT website, "
                "then answer the user's question using that data. Be concise and helpful.",
    description="Ask me anything about GAT — contact, address, admissions. I fetch live data from gat.ac.in.",
    tools=[fetch_college_info],
)

_tracer = OpikTracer()
track_adk_agent_recursive(root_agent, _tracer)
