import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import requests
from html.parser import HTMLParser
from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from agent_config import ProxyGemini, GEMINI_MODEL


def fetch_college_info(page: str = "contact") -> str:
    """Fetch information from the Global Academy of Technology (GAT) website."""
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


class GATInfoAgent(LlmAgent):
    async def _run_async_impl(self, ctx: InvocationContext):
        user_msg = ""
        for event in reversed(ctx.session.events):
            if hasattr(event, "author") and event.author == "user":
                if event.content and event.content.parts:
                    user_msg = event.content.parts[0].text
                    break
        if user_msg and "Live data from GAT" not in user_msg:
            college_data = fetch_college_info("contact")
            enriched = (
                f"Question: {user_msg}\n\n"
                f"Live data from GAT website (gat.ac.in):\n{college_data}\n\n"
                f"Please answer the question using the data above."
            )
            for event in reversed(ctx.session.events):
                if hasattr(event, "author") and event.author == "user":
                    if event.content and event.content.parts:
                        event.content.parts[0].text = enriched
                        break
        async for e in super()._run_async_impl(ctx):
            yield e


root_agent = GATInfoAgent(
    name="GATInfoAgent",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="When the conversation starts, greet the user with: 'Hi! I am the GAT Assistant. How can I help you today?' Then proceed to answer their questions. You are a helpful information assistant for Global Academy of Technology (GAT), "
                "Bengaluru. The user's message contains a question followed by live data fetched "
                "from the GAT website. Answer the question using that data. Be concise and helpful.",
    description="Ask me anything about GAT — contact, address, admissions. I fetch live data from gat.ac.in.",
)
