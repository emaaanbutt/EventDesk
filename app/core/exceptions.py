class DomainError(Exception):
    status_code = 500

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class UnauthenticatedError(DomainError):
    status_code = 401


class PermissionDeniedError(DomainError):
    status_code = 403


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class InvalidInputError(DomainError):
    status_code = 422


class InternalServiceError(DomainError):
    status_code = 500


class ServiceUnavailableError(DomainError):
    status_code = 503
