# AI Module Notes

- AI HTTP endpoints live in `blueprints/ai/`.
- AI business logic lives in `services/ai/`.
- Prompt configuration persistence lives in `ai_prompt_configs` and is accessed via:
  - `repositories/prompt_repository.py`
  - `services/prompt/prompt_service.py`
- Route handlers must not call external providers directly; provider interaction must be inside `services/ai/*`.

## Provider Runtime
- Runtime provider: `groq`.
- API key is read globally from `.env` via `GROQ_API_KEY`.
- Default model: `openai/gpt-oss-120b`.
- Per-user `users.ai_provider` and `users.api_key_ref` are kept only for schema compatibility and are not used for provider calls.

## AI Endpoints
- `POST /api/ai/revise-proposal`: calls selected provider for plan revision JSON output.
- `POST /api/ai/analyze-food-photo`: requires a vision-capable model/provider; the default Groq text model will return an unsupported-image error.

## Token Logging
- Both endpoints write usage tokens (`input_tokens`, `output_tokens`) to `ai_request_logs`.
