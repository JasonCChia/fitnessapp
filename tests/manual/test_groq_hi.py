from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import Config
from services.ai.provider_client import ProviderClient


def main() -> int:
    if not Config.GROQ_API_KEY:
        print("Missing GROQ_API_KEY in .env")
        return 1

    try:
        result = ProviderClient().chat_text(
            provider="groq",
            api_key=Config.GROQ_API_KEY,
            model=Config.GROQ_MODEL,
            system_prompt="Reply with exactly: hi",
            user_prompt="hi",
            temperature=Config.GROQ_TEMPERATURE,
            max_tokens=Config.GROQ_MAX_COMPLETION_TOKENS,
        )
    except Exception as exc:
        print(f"Groq request failed: {exc}")
        return 1

    print(f"model: {result.get('model')}")
    print(f"response: {result.get('text')}")
    if not result.get("text"):
        print("Empty response text")
        return 1
    print(
        "usage: "
        f"input={result.get('input_tokens', 0)}, "
        f"output={result.get('output_tokens', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
