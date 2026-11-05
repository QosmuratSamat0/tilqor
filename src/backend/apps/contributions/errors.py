from common.feedback import FeedbackError


class ContributionError(FeedbackError):
    pass


class ContributionForbidden(ContributionError):
    status_code = 403


class ContributionConflict(ContributionError):
    status_code = 409
