from typing import Any


class ApiError(Exception):
    def __init__(self, status_code: int, message: str, code: str, data: Any = None) -> None:
        self.status_code = status_code
        self.message = message
        self.code = code
        self.data = data
        super().__init__(message)

