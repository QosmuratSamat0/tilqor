from django.contrib import admin

from apps.verification.models import Finalization, QualitySettings, Review, ReviewerProfile


@admin.register(QualitySettings)
class QualitySettingsAdmin(admin.ModelAdmin):
    list_display = ("version", "is_active", "threshold", "min_votes", "max_votes", "created_at")
    list_filter = ("is_active",)

    def has_add_permission(self, request):
        return request.user.is_admin_role and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return request.user.is_admin_role and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return (
            request.user.is_admin_role
            and not (obj and obj.reviews.exists())
            and super().has_delete_permission(request, obj)
        )


class AuditAdmin(admin.ModelAdmin):
    """Review and reputation records are written only through the locked services."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ReviewerProfile)
class ReviewerProfileAdmin(AuditAdmin):
    list_display = ("user", "weight", "updated_at")
    search_fields = ("user__username",)


@admin.register(Review)
class ReviewAdmin(AuditAdmin):
    list_display = ("id", "version", "reviewer", "decision", "weight_snapshot", "created_at")
    list_filter = ("decision",)
    raw_id_fields = ("version", "reviewer")


@admin.register(Finalization)
class FinalizationAdmin(AuditAdmin):
    list_display = ("version", "decision", "moderator", "reason", "created_at")
