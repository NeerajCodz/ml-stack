"""Optional IPython integration; importable without IPython installed."""
from __future__ import annotations
from typing import Any


def _client(namespace: dict[str, Any]):
    from .research import ResearchClient
    client = namespace.get("ml_client")
    if client is None:
        client = ResearchClient.open(namespace.get("ML_STACK_ROOT"))
        namespace["ml_client"] = client
    return client

def research_line(line: str, *, namespace: dict[str, Any]):
    """Execute a notebook line such as ``%ml_research transformer --kind anchor``."""
    import shlex
    tokens = shlex.split(line)
    if not tokens: raise ValueError("usage: %ml_research QUERY [--kind KIND] [--limit N]")
    kinds = []; limit = 5; offline = False; query = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--kind": index += 1; kinds.append(tokens[index])
        elif token == "--limit": index += 1; limit = int(tokens[index])
        elif token == "--offline": offline = True
        else: query.append(token)
        index += 1
    result = _client(namespace).research(" ".join(query), kinds=tuple(kinds) or ("anchor", "recent"), limit=limit, offline=offline)
    namespace["ml_result"] = result
    return result

def load_ipython_extension(ip):
    def _magic(line: str): return research_line(line, namespace=ip.user_ns)
    ip.register_magic_function(_magic, "line", "ml_research")

def unload_ipython_extension(ip):
    # IPython does not expose a stable unregister API across versions.
    ip.user_ns.pop("ml_result", None)

__all__ = ["load_ipython_extension", "research_line", "unload_ipython_extension"]
