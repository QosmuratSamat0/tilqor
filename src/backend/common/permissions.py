"""Role-based permissions checked on the server (FR-02)."""
from rest_framework.permissions import BasePermission


class IsReviewer(BasePermission):
    """Reviewers, moderators and administrators."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_reviewer)


class IsModerator(BasePermission):
    """Moderators and administrators."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_moderator)
