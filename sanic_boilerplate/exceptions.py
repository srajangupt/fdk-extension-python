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
