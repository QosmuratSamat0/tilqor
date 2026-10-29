from django.contrib import admin

from apps.verification.models import QualitySettings, Review, ReviewerProfile


@admin.register(QualitySettings)
class QualitySettingsAdmin(admin.ModelAdmin):
    list_display = ("version", "is_active", "threshold", "min_votes", "max_votes", "created_at")
    list_filter = ("is_active",)


@admin.register(ReviewerProfile)
class ReviewerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "weight", "updated_at")
    search_fields = ("user__username",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "version", "reviewer", "decision", "weight_snapshot", "created_at")
    list_filter = ("decision",)
    raw_id_fields = ("version", "reviewer")
