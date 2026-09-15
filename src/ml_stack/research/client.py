"""First-class Python access for scripts, notebooks, and library users."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ..config import Settings, load_settings
from ..core import Ledger
from ..data import audit_file
from ..evidence import EvidenceCache
from .notebook import write_ipynb
from .paper_first import PAPER_FIRST_KINDS, PaperFirstResearch, ResearchRequest, ResearchResult
from .web import MultiSourceAdapter

class OptionalDependencyError(ImportError):
    """Raised when an optional notebook/dataframe integration is requested."""

@dataclass(slots=True)
class DatasetView:
    """Lazy dataset handle usable from Python and Jupyter."""
    path: Path
    target: str | None = None

    @property
    def audit(self) -> dict[str, Any]:
        return audit_file(self.path, self.target)

    def sample(self, n: int = 5) -> list[dict[str, Any]]:
        if n < 0: raise ValueError("sample size must be non-negative")
        return list(self.audit.get("sample", []))[:n]

    def to_pandas(self, **kwargs: Any):
        try:
            import pandas as pd
        except ImportError as exc:
            raise OptionalDependencyError("install pandas to use DatasetView.to_pandas()") from exc
        suffix = self.path.suffix.lower()
        if suffix == ".csv": return pd.read_csv(self.path, **kwargs)
        if suffix == ".tsv": return pd.read_csv(self.path, sep="\t", **kwargs)
        if suffix == ".jsonl": return pd.read_json(self.path, lines=True, **kwargs)
        if suffix == ".json": return pd.read_json(self.path, **kwargs)
        if suffix == ".parquet": return pd.read_parquet(self.path, **kwargs)
        if suffix == ".feather": return pd.read_feather(self.path, **kwargs)
        raise ValueError(f"pandas bridge does not support {suffix or 'extensionless'} files")

    def to_records(self) -> list[dict[str, Any]]:
        return self.to_pandas().to_dict(orient="records")

    def to_polars(self, **kwargs: Any):
        try:
            import polars as pl
        except ImportError as exc:
            raise OptionalDependencyError("install polars to use DatasetView.to_polars()") from exc
        suffix = self.path.suffix.lower()
        if suffix in {".csv", ".tsv"}:
            return pl.read_csv(self.path, separator="\t" if suffix == ".tsv" else ",", **kwargs)
        if suffix == ".parquet": return pl.read_parquet(self.path, **kwargs)
        if suffix in {".json", ".jsonl"}: return pl.read_ndjson(self.path, **kwargs) if suffix == ".jsonl" else pl.read_json(self.path, **kwargs)
        raise ValueError(f"polars bridge does not support {suffix or 'extensionless'} files")

    def to_arrow(self, **kwargs: Any):
        try:
            import pyarrow as pa
            import pyarrow.csv as pacsv
            import pyarrow.parquet as papq
        except ImportError as exc:
            raise OptionalDependencyError("install pyarrow to use DatasetView.to_arrow()") from exc
        suffix = self.path.suffix.lower()
        if suffix == ".parquet": return papq.read_table(self.path, **kwargs)
        if suffix == ".csv": return pacsv.read_csv(self.path, **kwargs)
        return pa.Table.from_pandas(self.to_pandas(**kwargs))

    def to_numpy(self, **kwargs: Any):
        try:
            import numpy as np
        except ImportError as exc:
            raise OptionalDependencyError("install numpy to use DatasetView.to_numpy()") from exc
        if self.path.suffix.lower() in {".npy", ".npz"}: return np.load(self.path, **kwargs)
        return self.to_pandas(**kwargs).to_numpy()

@dataclass(slots=True)
class ResearchClient:
    """Stable high-level facade around cache, web adapters, and notebooks."""
    root: Path
    cache: EvidenceCache
    adapter: Any | None = None
    offline: bool = False

    @classmethod
    def from_settings(cls, settings: Settings | None = None, *, adapter: Any | None = None, offline: bool | None = None) -> "ResearchClient":
        settings = settings or load_settings()
        settings.ensure_state()
        ledger = Ledger(settings.database)
        return cls(settings.root, EvidenceCache(settings.state_dir / "cache" / "evidence", ledger=ledger), adapter, settings.offline if offline is None else offline)

    @classmethod
    def open(cls, root: str | Path | None = None, *, adapter: Any | None = None, offline: bool = False) -> "ResearchClient":
        settings = load_settings(root)
        return cls.from_settings(settings, adapter=adapter, offline=offline)

    def research(
        self,
        query: str,
        *,
        kinds: Iterable[str] = PAPER_FIRST_KINDS,
        limit: int = 5,
        offline: bool | None = None,
        max_age_seconds: float | None = None,
        notebook_path: str | Path | None = None,
        ipynb_path: str | Path | None = None,
    ) -> ResearchResult:
        use_offline = self.offline if offline is None else offline
        source = self.adapter or (None if use_offline else MultiSourceAdapter())
        request = ResearchRequest(query=query, kinds=tuple(kinds), limit_per_kind=limit, offline=use_offline, max_age_seconds=max_age_seconds)
        result = PaperFirstResearch(self.cache, source).collect(request, notebook_path=str(notebook_path) if notebook_path else None)
        if ipynb_path:
            write_ipynb(result.records, ipynb_path, title=f"ML Stack research: {query}")
        return result

    search = research

    def anchor(self, query: str, **kwargs: Any) -> ResearchResult: return self.research(query, kinds=("anchor",), **kwargs)
    def recent(self, query: str, **kwargs: Any) -> ResearchResult: return self.research(query, kinds=("recent",), **kwargs)
    def citations(self, query: str, **kwargs: Any) -> ResearchResult: return self.research(query, kinds=("citations",), **kwargs)
    def code(self, query: str, **kwargs: Any) -> ResearchResult: return self.research(query, kinds=("code",), **kwargs)
    def datasets(self, query: str, **kwargs: Any) -> ResearchResult: return self.research(query, kinds=("dataset",), **kwargs)

    def dataset(self, path: str | Path, target: str | None = None) -> DatasetView:
        return DatasetView(Path(path).resolve(), target)

    @staticmethod
    def evidence_dataframe(result: ResearchResult):
        try:
            import pandas as pd
        except ImportError as exc:
            raise OptionalDependencyError("install pandas to use evidence_dataframe()") from exc
        return pd.DataFrame(result.provenance())

def create_research_client(root: str | Path | None = None, **kwargs: Any) -> ResearchClient:
    return ResearchClient.open(root, **kwargs)

__all__ = ["DatasetView", "OptionalDependencyError", "ResearchClient", "create_research_client"]
