# Changelog

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
