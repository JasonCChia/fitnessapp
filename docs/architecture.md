# Architecture Overview

## Architecture Style
- Target: `Modular Monolith`
- Request flow:
  1. `blueprints/*` (HTTP layer)
  2. `schemas/*` (validation/shape)
  3. `services/*` (business logic)
  4. `repositories/*` (SQL/data access)
  5. `db/*` (connection/bootstrap/schema)

## Boundaries
- Blueprints: no SQL, no heavy business logic.
- Services: orchestration and domain rules only.
- Repositories: all SQL statements live here.
- Models: schema metadata and table contracts.
- Core: reusable cross-cutting infrastructure.

## Scaling Notes
- Keep domains separated by folder.
- Add a feature by creating:
  - `blueprints/<feature>`
  - `schemas/request|response|validators`
  - `services/<feature>`
  - `repositories/<feature>_repository.py`
  - `tests/*`
  - `docs/*`
