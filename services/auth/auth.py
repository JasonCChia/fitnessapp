from werkzeug.security import check_password_hash, generate_password_hash


class AuthService:
    def hash_password(self, plain_password: str) -> str:
        return generate_password_hash(plain_password)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, plain_password)

    def issue_access_token(self, user_id: str) -> str:
        return f"dev-token-{user_id}"
