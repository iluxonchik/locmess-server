"""
Exception classes.
"""

class UserAlreadyExistsError(ValueError):
    """
    Raised when attempting to create a duplicate user.
    """
    pass

class UserNotFoundError(ValueError):
    pass

class TokenInvalidError(ValueError):
    pass
