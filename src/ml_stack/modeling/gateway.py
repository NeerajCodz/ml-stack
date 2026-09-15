from __future__ import annotations
import json, urllib.request
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True)
class ModelResponse:
    text: str
    usage: dict[str, int]
    model: str

class ModelGateway:
    def __init__(self, endpoint: str | None = None, model: str = "local", timeout: float = 30): self.endpoint, self.model, self.timeout = endpoint, model, timeout
    def catalog(self): return {"model": self.model, "endpoint": self.endpoint, "capabilities": ["text"]}
    def complete(self, messages: list[dict[str, str]], **params: Any) -> ModelResponse:
        if not self.endpoint: return ModelResponse("Model endpoint is not configured.", {"prompt_tokens": 0, "completion_tokens": 0}, self.model)
        body = json.dumps({"model": self.model, "messages": messages, **params}).encode(); request = urllib.request.Request(self.endpoint, data=body, headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response: value = json.loads(response.read())
        text = value.get("choices", [{}])[0].get("message", {}).get("content", "")
        return ModelResponse(text, value.get("usage", {}), value.get("model", self.model))
