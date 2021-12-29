"""Exception classes."""


class FdkInvalidExtensionJson(Exception):
    """Class FdkInvalidExtensionJson."""

    def __init__(self, message="Failed while validating extension json."):
        """Initialize function __init__."""
        super(FdkInvalidExtensionJson, self).__init__(message)


class FdkClusterMetaMissingException(Exception):
    """Class FdkClusterMetaMissingException."""

    def __init__(self, message="Failed because fdk cluster meta was missing."):
        """Initialize function __init__."""
        super(FdkClusterMetaMissingException, self).__init__(message)


class FdkSessionNotFoundError(Exception):
    """Class FdkSessionNotFoundError."""

    def __init__(self, message="Failed as fdk session was not found."):
        """Initialize function __init__."""
        super(FdkSessionNotFoundError, self).__init__(message)


class FdkInvalidOAuthError(Exception):
    """Class FdkInvalidOAuthError."""

    def __init__(self, message="Failed as oauth was invalid."):
        """Initialize function __init__."""
        super(FdkInvalidOAuthError, self).__init__(message)


class FdkInvalidWebhookConfig(Exception):
    """Class FdkInvalidWebhookConfig."""

    def __init__(self, message="Failed as webhook config was invalid."):
        """Initialize function __init__."""
        super(FdkInvalidWebhookConfig, self).__init__(message)


class FdkWebhookRegistrationError(Exception):
    """Class FdkWebhookRegistrationError."""

    def __init__(self, message="Failed to sync webhook events."):
        """Initialize function __init__."""
        super(FdkWebhookRegistrationError, self).__init__(message)


class FdkInvalidHMacError(Exception):
    """Class FdkInvalidHMacError."""

    def __init__(self, message="Failed to validate signature."):
        """Initialize function __init__."""
        super(FdkInvalidHMacError, self).__init__(message)


class FdkWebhookHandlerNotFound(Exception):
    """Class FdkWebhookHandlerNotFound."""

    def __init__(self, message="Failed to find fdk webhook handler."):
        """Initialize function __init__."""
        super(FdkWebhookHandlerNotFound, self).__init__(message)


class FdkWebhookProcessError(Exception):
    """Class FdkWebhookProcessError."""

    def __init__(self, message="Failed to process webhook."):
        """Initialize function __init__."""
        super(FdkWebhookProcessError, self).__init__(message)
