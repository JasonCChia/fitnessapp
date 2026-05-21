from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash


class AuthService:
    TOKEN_SALT = "fitdiscipline-auth-v1"

    def hash_password(self, plain_password: str) -> str:
        return generate_password_hash(plain_password)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, plain_password)

    def _token_serializer(self) -> URLSafeTimedSerializer:
        return URLSafeTimedSerializer(
            secret_key=current_app.config["SECRET_KEY"],
            salt=self.TOKEN_SALT,
        )

    def issue_access_token(self, user_id: str) -> str:
        payload = {"user_id": user_id}
        return self._token_serializer().dumps(payload)

    def verify_access_token(self, token: str) -> str | None:
        try:
            payload = self._token_serializer().loads(
                token,
                max_age=current_app.config["ACCESS_TOKEN_EXPIRES_SECONDS"],
            )
        except (BadSignature, SignatureExpired):
            return None

        user_id = payload.get("user_id")
        if not isinstance(user_id, str) or not user_id:
            return None
        return user_id
