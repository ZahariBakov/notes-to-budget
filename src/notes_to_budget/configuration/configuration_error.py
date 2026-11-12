"""The error raised when the settings cannot be used."""


class ConfigurationError(Exception):
    """Something in the person's settings needs their attention.

    The error carries a message key and the details to fill in, not a
    finished sentence, so the command line can show it in the person's
    language (see ``localization/locales``).
    """

    def __init__(self, message_key: str, **details: object) -> None:
        super().__init__(message_key, details)
        self.message_key = message_key
        self.details = details

    def __str__(self) -> str:
        if not self.details:
            return self.message_key
        described_details = ", ".join(f"{name}={value}" for name, value in self.details.items())
        return f"{self.message_key} ({described_details})"
