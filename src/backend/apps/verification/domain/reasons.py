"""Pure validation shared by review serializers and the locked review service."""

REASON_CODES = ("wrong_term", "russian_connector", "grammar", "other")


def reason_error(decision: str, reason_code: str, comment: str):
    """Return (field, code, message) or None; whitespace-only comments are empty."""
    if decision in ("reject", "edit"):
        if not reason_code:
            return (
                "reason_code",
                "reason_required",
                "A reason code is required for reject and edit.",
            )
        if reason_code not in REASON_CODES:
            return "reason_code", "invalid_choice", "Invalid reason code."
    elif reason_code:
        return (
            "reason_code",
            "reason_not_allowed",
            "Accept and don't know cannot carry a reason code.",
        )
    if reason_code == "other" and not comment.strip():
        return "reason", "comment_required", "A comment is required for reason other."
    return None
