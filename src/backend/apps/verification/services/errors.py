from common.feedback import FeedbackError


class ReviewError(FeedbackError):
    pass


class ReviewForbidden(ReviewError):
    status_code = 403


class ReviewConflict(ReviewError):
    status_code = 409
