class GlossaryError(Exception):
    status_code = 400

    def __init__(self, message: str, *, field: str = "detail"):
        super().__init__(message)
        self.message = message
        self.field = field

    def as_dict(self) -> dict[str, list[str] | str]:
        if self.field == "detail":
            return {"detail": self.message}
        return {self.field: [self.message]}


class GlossaryForbidden(GlossaryError):
    status_code = 403


class GlossaryNotFound(GlossaryError):
    status_code = 404
