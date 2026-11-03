from django.contrib import admin

from apps.glossary.admin_actions import (
    publish_connector_hints,
    recommend_variant,
    unpublish_connector_hints,
)
from apps.glossary.models import ConnectorHint, Term


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text_ru",
        "domain",
        "source",
        "licence",
        "recommended_version",
        "recommended_by",
        "recommended_at",
    )
    list_filter = ("domain", "licence")
    search_fields = ("text_ru", "definition", "source")
    readonly_fields = (
        "recommended_version",
        "recommended_reason",
        "recommended_by",
        "recommended_at",
    )
    actions = [recommend_variant]

    def has_add_permission(self, request):
        return request.user.is_moderator and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return request.user.is_moderator and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_moderator and super().has_delete_permission(request, obj)

    def has_recommend_permission(self, request):
        return request.user.is_moderator and self.has_change_permission(request)


@admin.register(ConnectorHint)
class ConnectorHintAdmin(admin.ModelAdmin):
    list_display = ("id", "text_ru", "text_kk", "is_published", "licence", "created_at")
    list_filter = ("is_published", "licence")
    search_fields = ("text_ru", "text_kk", "example_kk", "example_ru")
    actions = [publish_connector_hints, unpublish_connector_hints]

    def has_add_permission(self, request):
        return request.user.is_moderator and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return request.user.is_moderator and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_moderator and super().has_delete_permission(request, obj)
