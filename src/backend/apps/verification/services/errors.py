class ReviewError(Exception):
    status_code = 400


class ReviewForbidden(ReviewError):
    status_code = 403


class ReviewConflict(ReviewError):
    status_code = 409
