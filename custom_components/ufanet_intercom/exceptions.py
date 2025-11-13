"""Exceptions list for UfanetAPI."""


class UfanetIntercomAPIError(Exception):
    """Base exceptions class for UfanetAPI."""


class ClientConnectorUfanetIntercomAPIError(UfanetIntercomAPIError):
    """Ufanet API error."""


class UnauthorizedUfanetIntercomAPIError(UfanetIntercomAPIError):
    """Ufanet API error."""


class TimeoutUfanetIntercomAPIError(UfanetIntercomAPIError):
    """Ufanet API error."""


class UnknownUfanetIntercomAPIError(UfanetIntercomAPIError):
    """Ufanet API error."""
