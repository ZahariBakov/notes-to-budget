"""The error raised when the settings cannot be used."""

from notes_to_budget.user_facing_error import UserFacingError


class ConfigurationError(UserFacingError):
    """Something in the person's settings needs their attention."""
