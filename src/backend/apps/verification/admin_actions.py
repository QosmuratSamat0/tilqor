from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from apps.verification.choices import COUNTED_DECISIONS
from apps.verification.services import resolve_version
from apps.verification.services.errors import ReviewError


class ResolutionForm(forms.Form):
    decision = forms.ChoiceField(choices=[(d.value, d.label) for d in COUNTED_DECISIONS])
    reason = forms.CharField(widget=forms.Textarea)


class ControlVersionForm(forms.ModelForm):
    def clean(self):
        data = super().clean()
        if data.get("is_control") and data.get("reference_decision") not in COUNTED_DECISIONS:
            self.add_error(
                "reference_decision", "Control versions need an accept, reject or edit answer."
            )
        return data


@admin.action(description="Resolve escalated versions with a reason", permissions=["resolve"])
def resolve_escalated(modeladmin, request, queryset):
    if not request.user.is_moderator:
        raise PermissionDenied
    form = ResolutionForm(request.POST if "apply_resolution" in request.POST else None)
    if "apply_resolution" in request.POST and form.is_valid():
        for version in queryset.order_by("pk"):
            try:
                resolve_version(moderator=request.user, version_id=version.pk, **form.cleaned_data)
            except ReviewError as exc:
                modeladmin.message_user(request, f"Version {version.pk}: {exc}", messages.ERROR)
            else:
                modeladmin.message_user(
                    request, f"Resolved version {version.pk}.", messages.SUCCESS
                )
        return None
    return render(
        request,
        "admin/verification/resolve.html",
        {
            **modeladmin.admin_site.each_context(request),
            "title": "Resolve escalated versions",
            "form": form,
            "versions": queryset,
            "opts": modeladmin.model._meta,
        },
    )
