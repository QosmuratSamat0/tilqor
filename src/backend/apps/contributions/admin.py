from django.contrib import admin

from apps.contributions.models import (
    Contribution,
    ContributionVersion,
    SourceSentence,
    Task,
    VariantPreference,
)


@admin.register(SourceSentence)
class SourceSentenceAdmin(admin.ModelAdmin):
    list_display = ("id", "text_ru", "domain", "is_original", "licence")
    list_filter = ("domain", "is_original", "licence")
    search_fields = ("text_ru", "attribution")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "domain", "source_sentence", "term", "is_active")
    list_filter = ("type", "domain", "is_active")


class ContributionVersionInline(admin.TabularInline):
    model = ContributionVersion
    extra = 0
    fields = ("number", "text_kk", "status", "escalated", "is_withdrawn", "is_control")
    readonly_fields = ("number", "text_kk")


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "author", "created_at")
    list_filter = ("task__type", "task__domain")
    inlines = [ContributionVersionInline]


@admin.register(ContributionVersion)
class ContributionVersionAdmin(admin.ModelAdmin):
    list_display = ("id", "contribution", "number", "status", "escalated", "is_withdrawn")
    list_filter = ("status", "escalated", "is_withdrawn", "is_control")
    search_fields = ("text_kk",)


admin.site.register(VariantPreference)
