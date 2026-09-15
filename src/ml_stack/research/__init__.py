"""Bounded, paper-first research and deterministic notebook synthesis."""
from .notebook import synthesize_notebook, write_notebook
from .paper_first import PAPER_FIRST_KINDS, MemoryResearchAdapter, PaperFirstResearch, ResearchAdapter, ResearchRequest, ResearchResult
from .worker import ContextLimitExceeded, IterationLimitExceeded, READ_ONLY_TOOLS, ResearchAction, ResearchWorker, ReadOnlyResearchWorker, ToolAllowlist, ToolNotAllowed, ToolNotAvailable, WorkerResult
from .web import ArxivAdapter, CrossrefAdapter, DomainNotAllowed, GitHubAdapter, HuggingFaceAdapter, MultiSourceAdapter, OpenAlexAdapter, ResponseTooLarge, SemanticScholarAdapter, WebClient, WebResearchError

__all__ = ["ArxivAdapter","ContextLimitExceeded","CrossrefAdapter","DomainNotAllowed","GitHubAdapter","HuggingFaceAdapter","IterationLimitExceeded","MemoryResearchAdapter","MultiSourceAdapter","OpenAlexAdapter","PAPER_FIRST_KINDS","PaperFirstResearch","READ_ONLY_TOOLS","ResearchAction","ResearchAdapter","ResearchRequest","ResearchResult","ResearchWorker","ReadOnlyResearchWorker","ResponseTooLarge","SemanticScholarAdapter","ToolAllowlist","ToolNotAllowed","ToolNotAvailable","WebClient","WebResearchError","WorkerResult","synthesize_notebook","write_notebook"]
