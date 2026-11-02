class ContributionError(Exception):
    status_code = 400

    def __init__(self, message: str, *, field: str = "detail"):
        super().__init__(message)
        self.message = message
        self.field = field

    def as_dict(self) -> dict[str, list[str]]:
        return {self.field: [self.message]}


class ContributionForbidden(ContributionError):
    status_code = 403


class ContributionConflict(ContributionError):
    status_code = 409
