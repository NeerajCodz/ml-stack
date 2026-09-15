"""Bounded, paper-first research with Python and Jupyter access."""
from .notebook import build_ipynb, read_ipynb, synthesize_notebook, validate_ipynb, write_ipynb, write_notebook
from .paper_first import PAPER_FIRST_KINDS, MemoryResearchAdapter, PaperFirstResearch, ResearchAdapter, ResearchRequest, ResearchResult
from .worker import ContextLimitExceeded, IterationLimitExceeded, READ_ONLY_TOOLS, ResearchAction, ResearchWorker, ReadOnlyResearchWorker, ToolAllowlist, ToolNotAllowed, ToolNotAvailable, WorkerResult
from .client import DatasetView, OptionalDependencyError, ResearchClient, create_research_client
from .web import ArxivAdapter, CrossrefAdapter, DomainNotAllowed, GitHubAdapter, HuggingFaceAdapter, MultiSourceAdapter, OpenAlexAdapter, ResponseTooLarge, SemanticScholarAdapter, WebClient, WebResearchError

__all__ = ["ArxivAdapter","build_ipynb","ContextLimitExceeded","create_research_client","CrossrefAdapter","DatasetView","DomainNotAllowed","GitHubAdapter","HuggingFaceAdapter","IterationLimitExceeded","MemoryResearchAdapter","MultiSourceAdapter","OpenAlexAdapter","OptionalDependencyError","PAPER_FIRST_KINDS","PaperFirstResearch","READ_ONLY_TOOLS","read_ipynb","ResearchAction","ResearchAdapter","ResearchClient","ResearchRequest","ResearchResult","ResearchWorker","ReadOnlyResearchWorker","ResponseTooLarge","SemanticScholarAdapter","synthesize_notebook","ToolAllowlist","ToolNotAllowed","ToolNotAvailable","validate_ipynb","WebClient","WebResearchError","WorkerResult","write_ipynb","write_notebook"]
