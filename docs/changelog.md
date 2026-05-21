# Changelog

## 2026-05-21 - Global Groq AI Runtime
- Switched AI runtime resolution to a single global Groq key from `.env`.
- Added default model `openai/gpt-oss-120b` with Groq chat-completions settings.
- Removed onboarding/settings writes for per-user API key references.

## 2026-05-21 - User Authentication & Per-User Scope
- Added `password_hash` to `users` table contract and SQL schema.
- Added migration file: `db/migrations/20260521_add_password_hash_to_users.sql`.
- Added auth endpoints:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
- Added signed bearer token flow via `itsdangerous` with expiry support.
- Added route guard so `/api/users/<user_id>/...` can only be accessed by the token owner.
- Updated `GET /api/users` behavior to return only current authenticated user.
- Updated docs and guidance flow to include login-first app flow.

## 2026-05-21 - AI Request Token Logging
- Added table `ai_request_logs` for per-user AI request audit logging.
- Added fields for token usage: `input_tokens`, `output_tokens`, and `total_tokens`.
- Added migration file: `db/migrations/20260521_create_ai_request_logs.sql`.
- Added endpoints:
  - `POST /api/users/<user_id>/ai-request-logs`
  - `GET /api/users/<user_id>/ai-request-logs`

## 2026-05-21 - Real AI Provider Integration
- Replaced mock AI calls in `revise-proposal` and `analyze-food-photo` with real provider REST calls.
- Added provider support for `openai`, `anthropic`, and `gemini`.
- Added token usage extraction from provider responses and stored into `ai_request_logs`.
- Added config options:
  - `OPENAI_API_KEY`, `OPENAI_MODEL`
  - `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`
  - `GEMINI_API_KEY`, `GEMINI_MODEL`
