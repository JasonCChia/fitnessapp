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

## Authentication Boundary
- Auth token issuing and password hashing live in `services/auth/*`.
- Route guarding lives in `core/security/auth_guard.py`.
- Blueprints under `/api/users/<user_id>/...` enforce token + user scope before handler logic.

## Scaling Notes
- Keep domains separated by folder.
- Add a feature by creating:
  - `blueprints/<feature>`
  - `schemas/request|response|validators`
  - `services/<feature>`
  - `repositories/<feature>_repository.py`
  - `tests/*`
  - `docs/*`
