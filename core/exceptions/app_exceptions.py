class AppError(Exception):
    status_code = 400

    def __init__(self, message: str, detail=None):
        super().__init__(message)
        self.message = message
        self.detail = detail


class ValidationError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404


class DatabaseError(AppError):
    status_code = 500


class PermissionDenied(AppError):
    status_code = 403
