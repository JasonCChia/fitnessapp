# AI Module Notes

- AI HTTP endpoints live in `blueprints/ai/`.
- AI business logic lives in `services/ai/`.
- Prompt configuration persistence lives in `ai_prompt_configs` and is accessed via:
  - `repositories/prompt_repository.py`
  - `services/prompt/prompt_service.py`
- Route handlers must not call external providers directly; provider interaction must be inside `services/ai/*`.
