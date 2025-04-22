class APIConnectionError(Exception):
    """Raised when unable to connect to the Walacor API."""


class BadRequestError(Exception):
    def __init__(self, reason: str, message: str, code: int = 400):
        self.reason = reason
        self.message = message
        self.code = code
        super().__init__(f"[{reason}] {message}")


class FileRequestError(RuntimeError):
    """Raised when a file‐service operation fails."""


class DuplicateFileError(FileRequestError):
    """Raised when the platform reports the file is a duplicate."""
