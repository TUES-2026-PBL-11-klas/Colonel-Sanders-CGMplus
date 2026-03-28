class AuthServiceError(Exception):
    pass


class ResourceConflictError(AuthServiceError):
    pass
