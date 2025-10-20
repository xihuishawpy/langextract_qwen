from __future__ import annotations

import dataclasses
import os
from typing import Any, Iterator, Sequence

from langextract.core import base_model
from langextract.core import data
from langextract.core import exceptions
from langextract.core import types as core_types
from langextract.providers import router


@router.register(r"^qwen", priority=20)
@dataclasses.dataclass(init=False)
class QwenLanguageModel(base_model.BaseLanguageModel):
    """LangExtract provider for Qwen via DashScope OpenAI-compatible API."""

    model_id: str = "qwen-plus"
    api_key: str | None = None
    base_url: str | None = None
    format_type: data.FormatType = data.FormatType.JSON
    temperature: float | None = None
    max_workers: int = 10

    _client: Any = dataclasses.field(default=None, repr=False, compare=False)

    @property
    def requires_fence_output(self) -> bool:
        # JSON mode should return raw JSON (OpenAI response_format=json_object)
        return False if self.format_type == data.FormatType.JSON else super().requires_fence_output

    def __init__(
        self,
        model_id: str = "qwen-plus",
        api_key: str | None = None,
        base_url: str | None = None,
        format_type: data.FormatType = data.FormatType.JSON,
        temperature: float | None = None,
        max_workers: int = 10,
        **_: Any,
    ) -> None:
        try:
            # Lazy import to avoid hard dep if provider not used
            from openai import OpenAI  # type: ignore
        except Exception as e:
            raise exceptions.InferenceConfigError(
                "Qwen provider requires openai package. Install with: pip install openai"
            ) from e

        self.model_id = model_id
        # Fallback to environment if not provided in kwargs
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("LANGEXTRACT_API_KEY")
        self.base_url = base_url or os.environ.get("DASHSCOPE_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.format_type = format_type
        self.temperature = temperature
        self.max_workers = max_workers

        if not self.api_key:
            raise exceptions.InferenceConfigError("API key not provided. Set DASHSCOPE_API_KEY or pass api_key.")

        # Initialize OpenAI client (DashScope OpenAI-compatible endpoint)
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        # No enforced schema constraints here
        super().__init__()

    def _build_api_params(self, prompt: str, cfg: dict[str, Any]) -> dict[str, Any]:
        system_message = ""
        if self.format_type == data.FormatType.JSON:
            system_message = "You are a helpful assistant that responds in JSON format."
        elif self.format_type == data.FormatType.YAML:
            system_message = "You are a helpful assistant that responds in YAML format."

        messages = [{"role": "user", "content": prompt}]
        if system_message:
            messages.insert(0, {"role": "system", "content": system_message})

        params: dict[str, Any] = {
            "model": self.model_id,
            "messages": messages,
            "n": 1,
        }

        temp = cfg.get("temperature", self.temperature)
        if temp is not None:
            params["temperature"] = temp

        if self.format_type == data.FormatType.JSON:
            params.setdefault("response_format", {"type": "json_object"})

        # Common optional params
        if (v := cfg.get("max_output_tokens")) is not None:
            params["max_tokens"] = v
        if (v := cfg.get("top_p")) is not None:
            params["top_p"] = v
        for key in [
            "frequency_penalty",
            "presence_penalty",
            "seed",
            "stop",
            "logprobs",
            "top_logprobs",
            "reasoning",
            "response_format",
        ]:
            if (v := cfg.get(key)) is not None:
                params[key] = v

        return params

    def infer(self, batch_prompts: Sequence[str], **kwargs: Any) -> Iterator[Sequence[core_types.ScoredOutput]]:
        # Merge kwargs coming from LangExtract (temperature etc.)
        merged = self.merge_kwargs(kwargs)
        cfg: dict[str, Any] = {}
        if (v := merged.get("temperature", self.temperature)) is not None:
            cfg["temperature"] = v
        for k in ("max_output_tokens", "top_p", "frequency_penalty", "presence_penalty", "seed", "stop", "logprobs", "top_logprobs", "reasoning", "response_format"):
            if k in merged:
                cfg[k] = merged[k]

        for prompt in batch_prompts:
            try:
                params = self._build_api_params(prompt, cfg)
                resp = self._client.chat.completions.create(**params)
                output_text = resp.choices[0].message.content
                yield [core_types.ScoredOutput(score=1.0, output=output_text)]
            except Exception as e:  # noqa: BLE001
                raise exceptions.InferenceRuntimeError(f"DashScope(OpenAI) API error: {e}", original=e)
