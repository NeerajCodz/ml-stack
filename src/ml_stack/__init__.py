"""Portable ML research and experiment capability layer."""

__version__ = "0.2.0"
from .research import ResearchClient, create_research_client

__all__ = ["ResearchClient", "__version__", "create_research_client"]
