from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import User


@admin.register(User)
class TilqorUserAdmin(UserAdmin):
    list_display = ("username", "email", "display_name", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "display_name")
    fieldsets = UserAdmin.fieldsets + (("Tilqor", {"fields": ("role", "display_name")}),)
