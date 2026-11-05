"""Stable feedback codes alongside the existing human-readable API errors."""

from rest_framework.views import exception_handler as drf_exception_handler


class FeedbackError(Exception):
    status_code = 400

    def __init__(self, message, *, field="detail", code="invalid", params=None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.code = code
        self.params = params or {}

    def as_dict(self):
        if self.field == "detail":
            result = {"detail": self.message, "code": self.code}
        else:
            result = {self.field: [self.message], "codes": {self.field: [self.code]}}
        if self.params:
            result["params"] = {self.field: self.params}
        return result


def exception_handler(exc, context):
    """Preserve DRF's messages and expose its validation/authentication codes."""
    response = drf_exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict) and hasattr(exc, "get_codes"):
        codes = exc.get_codes()
        if "detail" in response.data:
            response.data["code"] = codes.get("detail") if isinstance(codes, dict) else codes
        elif isinstance(codes, dict):
            response.data["codes"] = {
                field: value if isinstance(value, list) else [value]
                for field, value in codes.items()
            }
    return response
