class AuthServiceError(Exception):
    pass


class ResourceConflictError(AuthServiceError):
    pass


class InvalidCredentialsError(AuthServiceError):
    pass
