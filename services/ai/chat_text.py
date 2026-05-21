import json

from services.ai.provider_client import ProviderClient


class ChatTextService:
    def __init__(self):
        self.client = ProviderClient()

    @staticmethod
    def _parse_json_text(text: str) -> dict:
        raw = (text or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:].strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise ValueError("AI response is not valid JSON")
            return json.loads(raw[start : end + 1])

    def ask_json(
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
        if not api_key:
            return {"status": "error", "data": None, "error": "Missing API key"}
        try:
            result = self.client.chat_text(
                provider=provider,
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            parsed = self._parse_json_text(result["text"])
            return {
                "status": "ok",
                "data": parsed,
                "error": None,
                "usage": {
                    "input_tokens": int(result.get("input_tokens") or 0),
                    "output_tokens": int(result.get("output_tokens") or 0),
                },
                "model": result.get("model"),
            }
        except Exception as exc:
            return {"status": "error", "data": None, "error": str(exc)}
