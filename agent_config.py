"""
Shared helpers used by all agent scripts.

Provides:
  - get_model()             : returns ProxyGemini, LiteLlm(Ollama), or LiteLlm(Gemma4) based on .env
  - ProxyGemini             : Gemini model wired to the local proxy + API key, with retry
  - setup_opik()            : configure OPIK once from .env
  - build_runner_no_opik()  : create a plain Runner + InMemorySessionService (no tracing)
  - build_runner()          : same, but also attaches OpikTracer for full tracing
  - run_agent()             : run any agent and return the final response text
  - run_agent_multiturn()   : run with session reuse for multi-turn conversations
  - load_config()           : load a YAML config, resolving *_file keys to file contents

Model selection via .env  (set GEMINI_MODEL= to one of these):
  gemini-2.5-flash            → Gemini 2.5 Flash via proxy    5 RPM / 20 RPD
  gemini-3.1-flash-lite       → Gemini 3.1 Flash Lite          15 RPM / 500 RPD  ← recommended
  gemma-4-26b-it / gemma-4-31b-it → Gemma 4 via proxy         15 RPM / 1500 RPD / unlimited TPM
  ollama/llama3.2             → Ollama locally (no rate limit)
  ollama/gemma3               → Ollama locally (no rate limit)
"""

import os
from functools import cached_property
from pathlib import Path
import yaml

from dotenv import load_dotenv
import opik
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

from google.adk.models import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import Client, types
from google.genai.types import HttpOptions

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

# Retry config — retries on 429 (rate limit) and 400 (proxy transient errors)
_RETRY_OPTIONS = types.HttpRetryOptions(
    initial_delay=5,
    attempts=3,
    http_status_codes=[400, 408, 429, 500, 502, 503, 504],
)


# ── Gemini proxy ───────────────────────────────────────────────────────────────

def _patch_client_for_proxy(client: Client) -> Client:
    """Patch a genai Client so thoughtSignature is stripped from every request.

    The local proxy rejects multi-turn requests that carry thoughtSignature in
    content parts. ADK routes calls through client.aio._api_client, so we patch
    _build_request on that underlying BaseApiClient instance.
    """
    base = client.aio._api_client
    original_build = base._build_request

    def _build_request_patched(http_method, path, request_dict, http_options=None):
        if 'generateContent' in path:
            for content in request_dict.get('contents', []):
                for part in content.get('parts', []):
                    part.pop('thoughtSignature', None)
        return original_build(http_method, path, request_dict, http_options)

    base._build_request = _build_request_patched
    return client


class ProxyGemini(Gemini):
    """Gemini model — routes through a local proxy if GOOGLE_GEMINI_BASE_URL is set,
    otherwise calls Google's API directly. Retries automatically on 429.

    Strips thoughtSignature from history parts before each request — the proxy
    rejects multi-turn requests that carry this field in contents.
    """
    @cached_property
    def api_client(self) -> Client:
        base_url = os.getenv("GOOGLE_GEMINI_BASE_URL")
        client = Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            http_options=HttpOptions(
                base_url=base_url,
                retry_options=_RETRY_OPTIONS,
            ) if base_url else HttpOptions(retry_options=_RETRY_OPTIONS),
        )
        return _patch_client_for_proxy(client)


# ── Model selector ─────────────────────────────────────────────────────────────

def get_model(model_name: str = None):
    """Return the right model instance based on GEMINI_MODEL in .env.

    - ollama/llama3.2    → LiteLlm pointing at local Ollama (no rate limits)
    - ollama/gemma3      → LiteLlm pointing at local Ollama
    - gemma-4-26b-it     → LiteLlm pointing at proxy (15 RPM / 1500 RPD / unlimited TPM)
    - gemma-4-31b-it     → LiteLlm pointing at proxy (same limits)
    - gemini-3.1-flash-lite → ProxyGemini (15 RPM / 500 RPD) ← default
    - anything else      → ProxyGemini (Gemini via proxy or direct)

    Usage in agent files:
        model=get_model()                # reads GEMINI_MODEL from .env automatically
        model=get_model("gemma-4-26b-it")  # override explicitly
    """
    name = model_name or GEMINI_MODEL
    if name.startswith("ollama/"):
        ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return LiteLlm(
            model=name,
            api_base=ollama_base,
        )
    if name.startswith("gemma-"):
        # Gemma 4 models route through the same proxy using OpenAI-compatible endpoint
        proxy_base = os.getenv("GOOGLE_GEMINI_BASE_URL", "").rstrip("/")
        return LiteLlm(
            model=f"openai/{name}",
            api_base=proxy_base,
            api_key=os.getenv("GEMINI_API_KEY"),
        )
    return ProxyGemini(model=name)


# ── OPIK setup ─────────────────────────────────────────────────────────────────

def setup_opik(project_name: str = "engineering-faculty-assistant") -> None:
    """Configure OPIK from environment variables."""
    opik.configure(
        api_key=os.getenv("OPIK_API_KEY"),
        workspace=os.getenv("OPIK_WORKSPACE"),
        project_name=os.getenv("OPIK_PROJECT_NAME", project_name),
    )


# ── Runner factories ───────────────────────────────────────────────────────────

def build_runner_no_opik(agent, app_name: str) -> tuple:
    """Create a plain Runner with no tracing. Returns (runner, session_service)."""
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
    return runner, session_service


def build_runner(agent, app_name: str) -> tuple:
    """Create a Runner and attach OPIK tracing. Returns (runner, session_service)."""
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)
    tracer = OpikTracer()
    track_adk_agent_recursive(agent, tracer)
    return runner, session_service


# ── Run helper ─────────────────────────────────────────────────────────────────

async def run_agent(runner: Runner, session_service: InMemorySessionService,
                    message: str, app_name: str, user_id: str = "user-1") -> str:
    """Send a message to an agent and return the final response text."""
    session = await session_service.create_session(app_name=app_name, user_id=user_id)
    result_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            result_text = event.content.parts[0].text
    return result_text


async def run_agent_multiturn(runner: Runner, session_service: InMemorySessionService,
                              message: str, app_name: str, user_id: str = "user-1",
                              session_id: str = None) -> tuple:
    """Send a message reusing an existing session (for multi-turn conversations).

    Returns (response_text, session_id) so the caller can pass session_id back
    on the next turn to maintain conversation history.
    """
    if session_id:
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
    else:
        session = await session_service.create_session(app_name=app_name, user_id=user_id)

    result_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            result_text = event.content.parts[0].text
    return result_text, session.id


# ── Config loader ──────────────────────────────────────────────────────────────

def load_config(config_filename: str) -> dict:
    """Load a YAML config and resolve all *_file keys to their file contents."""
    base = Path(__file__).parent
    with open(base / config_filename) as f:
        cfg = yaml.safe_load(f)

    def resolve(node):
        if isinstance(node, dict):
            result = {}
            for k, v in node.items():
                if k.endswith("_file") and isinstance(v, str):
                    result[k[:-5]] = (base / v).read_text().strip()
                else:
                    result[k] = resolve(v)
            return result
        return node

    return resolve(cfg)
