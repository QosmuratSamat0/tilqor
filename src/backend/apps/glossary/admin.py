from django.contrib import admin

from apps.glossary.models import Term


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("text_ru", "domain", "recommended_version")
    list_filter = ("domain",)
    search_fields = ("text_ru", "definition")
    raw_id_fields = ("recommended_version",)
