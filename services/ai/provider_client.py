import base64
import json
from pathlib import Path
from urllib import error as url_error
from urllib import parse as url_parse
from urllib import request as url_request


def _http_post_json(url: str, headers: dict, payload: dict, timeout: int = 90) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = url_request.Request(url=url, data=data, headers=headers, method="POST")
    try:
        with url_request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8"))
    except url_error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Provider HTTP {exc.code}: {body}") from exc
    except url_error.URLError as exc:
        raise RuntimeError(f"Provider network error: {exc.reason}") from exc


def _guess_mime_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".webp":
        return "image/webp"
    return "application/octet-stream"


def _read_b64(path: str) -> str:
    raw = Path(path).read_bytes()
    return base64.b64encode(raw).decode("utf-8")


class ProviderClient:
    def chat_text(
        self,
        *,
        provider: str,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 900,
    ) -> dict:
        provider = provider.lower().strip()
        if provider == "groq":
            return self._groq_text(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        if provider == "openai":
            return self._openai_text(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        if provider == "anthropic":
            return self._anthropic_text(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        if provider == "gemini":
            return self._gemini_text(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        raise RuntimeError(f"Unsupported provider: {provider}")

    def analyze_image(
        self,
        *,
        provider: str,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        image_path: str,
        temperature: float = 0.1,
        max_tokens: int = 700,
    ) -> dict:
        provider = provider.lower().strip()
        if provider == "groq":
            raise RuntimeError(
                f"Configured Groq model '{model}' does not support image analysis in this app."
            )
        if provider == "openai":
            return self._openai_vision(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                image_path=image_path,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        if provider == "anthropic":
            return self._anthropic_vision(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                image_path=image_path,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        if provider == "gemini":
            return self._gemini_vision(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                image_path=image_path,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        raise RuntimeError(f"Unsupported provider: {provider}")

    def _groq_text(self, **kwargs) -> dict:
        payload = {
            "model": kwargs["model"],
            "messages": [
                {"role": "system", "content": kwargs["system_prompt"]},
                {"role": "user", "content": kwargs["user_prompt"]},
            ],
            "temperature": kwargs["temperature"],
            "max_completion_tokens": kwargs["max_tokens"],
            "top_p": 1,
            "reasoning_effort": "medium",
            "stream": False,
            "stop": None,
        }
        res = _http_post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {kwargs['api_key']}",
            },
            payload=payload,
        )
        text = (((res.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
        usage = res.get("usage") or {}
        return {
            "text": text,
            "model": res.get("model") or kwargs["model"],
            "input_tokens": int(usage.get("prompt_tokens") or 0),
            "output_tokens": int(usage.get("completion_tokens") or 0),
        }

    def _openai_text(self, **kwargs) -> dict:
        payload = {
            "model": kwargs["model"],
            "messages": [
                {"role": "system", "content": kwargs["system_prompt"]},
                {"role": "user", "content": kwargs["user_prompt"]},
            ],
            "temperature": kwargs["temperature"],
            "max_tokens": kwargs["max_tokens"],
            "response_format": {"type": "json_object"},
        }
        res = _http_post_json(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {kwargs['api_key']}",
            },
            payload=payload,
        )
        text = (((res.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
        usage = res.get("usage") or {}
        return {
            "text": text,
            "model": res.get("model") or kwargs["model"],
            "input_tokens": int(usage.get("prompt_tokens") or 0),
            "output_tokens": int(usage.get("completion_tokens") or 0),
        }

    def _openai_vision(self, **kwargs) -> dict:
        b64 = _read_b64(kwargs["image_path"])
        mime = _guess_mime_type(kwargs["image_path"])
        payload = {
            "model": kwargs["model"],
            "messages": [
                {"role": "system", "content": kwargs["system_prompt"]},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": kwargs["user_prompt"]},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    ],
                },
            ],
            "temperature": kwargs["temperature"],
            "max_tokens": kwargs["max_tokens"],
            "response_format": {"type": "json_object"},
        }
        res = _http_post_json(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {kwargs['api_key']}",
            },
            payload=payload,
        )
        text = (((res.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
        usage = res.get("usage") or {}
        return {
            "text": text,
            "model": res.get("model") or kwargs["model"],
            "input_tokens": int(usage.get("prompt_tokens") or 0),
            "output_tokens": int(usage.get("completion_tokens") or 0),
        }

    def _anthropic_text(self, **kwargs) -> dict:
        payload = {
            "model": kwargs["model"],
            "max_tokens": kwargs["max_tokens"],
            "temperature": kwargs["temperature"],
            "system": kwargs["system_prompt"],
            "messages": [{"role": "user", "content": [{"type": "text", "text": kwargs["user_prompt"]}]}],
        }
        res = _http_post_json(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": kwargs["api_key"],
                "anthropic-version": "2023-06-01",
            },
            payload=payload,
        )
        blocks = res.get("content") or []
        text = "\n".join(block.get("text", "") for block in blocks if block.get("type") == "text").strip()
        usage = res.get("usage") or {}
        return {
            "text": text,
            "model": res.get("model") or kwargs["model"],
            "input_tokens": int(usage.get("input_tokens") or 0),
            "output_tokens": int(usage.get("output_tokens") or 0),
        }

    def _anthropic_vision(self, **kwargs) -> dict:
        b64 = _read_b64(kwargs["image_path"])
        mime = _guess_mime_type(kwargs["image_path"])
        payload = {
            "model": kwargs["model"],
            "max_tokens": kwargs["max_tokens"],
            "temperature": kwargs["temperature"],
            "system": kwargs["system_prompt"],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                        {"type": "text", "text": kwargs["user_prompt"]},
                    ],
                }
            ],
        }
        res = _http_post_json(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": kwargs["api_key"],
                "anthropic-version": "2023-06-01",
            },
            payload=payload,
        )
        blocks = res.get("content") or []
        text = "\n".join(block.get("text", "") for block in blocks if block.get("type") == "text").strip()
        usage = res.get("usage") or {}
        return {
            "text": text,
            "model": res.get("model") or kwargs["model"],
            "input_tokens": int(usage.get("input_tokens") or 0),
            "output_tokens": int(usage.get("output_tokens") or 0),
        }

    def _gemini_text(self, **kwargs) -> dict:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{url_parse.quote(kwargs['model'])}:generateContent?key={url_parse.quote(kwargs['api_key'])}"
        )
        payload = {
            "contents": [{"parts": [{"text": f"{kwargs['system_prompt']}\n\n{kwargs['user_prompt']}"}]}],
            "generationConfig": {
                "temperature": kwargs["temperature"],
                "maxOutputTokens": kwargs["max_tokens"],
            },
        }
        res = _http_post_json(url, headers={"Content-Type": "application/json"}, payload=payload)
        candidates = res.get("candidates") or []
        parts = ((candidates[0] if candidates else {}).get("content") or {}).get("parts") or []
        text = "\n".join(part.get("text", "") for part in parts if part.get("text")).strip()
        usage = res.get("usageMetadata") or {}
        return {
            "text": text,
            "model": kwargs["model"],
            "input_tokens": int(usage.get("promptTokenCount") or 0),
            "output_tokens": int(usage.get("candidatesTokenCount") or 0),
        }

    def _gemini_vision(self, **kwargs) -> dict:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{url_parse.quote(kwargs['model'])}:generateContent?key={url_parse.quote(kwargs['api_key'])}"
        )
        b64 = _read_b64(kwargs["image_path"])
        mime = _guess_mime_type(kwargs["image_path"])
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{kwargs['system_prompt']}\n\n{kwargs['user_prompt']}"},
                        {"inline_data": {"mime_type": mime, "data": b64}},
                    ]
                }
            ],
            "generationConfig": {
                "temperature": kwargs["temperature"],
                "maxOutputTokens": kwargs["max_tokens"],
            },
        }
        res = _http_post_json(url, headers={"Content-Type": "application/json"}, payload=payload)
        candidates = res.get("candidates") or []
        parts = ((candidates[0] if candidates else {}).get("content") or {}).get("parts") or []
        text = "\n".join(part.get("text", "") for part in parts if part.get("text")).strip()
        usage = res.get("usageMetadata") or {}
        return {
            "text": text,
            "model": kwargs["model"],
            "input_tokens": int(usage.get("promptTokenCount") or 0),
            "output_tokens": int(usage.get("candidatesTokenCount") or 0),
        }
