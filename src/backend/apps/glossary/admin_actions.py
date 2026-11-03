from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from apps.contributions.models import ContributionVersion
from apps.contributions.selectors import eligible_versions
from apps.glossary.errors import GlossaryError
from apps.glossary.services import recommend_term_variant


class RecommendationForm(forms.Form):
    version = forms.ModelChoiceField(
        queryset=ContributionVersion.objects.all(),
        label="Eligible variant",
    )
    reason = forms.CharField(widget=forms.Textarea)

    def __init__(self, data=None, *args, terms=None, **kwargs):
        if data is not None and "version" not in data and "version_id" in data:
            data = data.copy()
            data["version"] = data["version_id"]
        super().__init__(data, *args, **kwargs)
        if terms is not None and (data is None or "apply_recommendation" not in data):
            self.fields["version"].queryset = (
                eligible_versions()
                .filter(contribution__task__term__in=terms)
                .select_related("contribution__author", "contribution__task__term")
                .order_by("pk")
            )


@admin.action(
    description="Set recommended variant for selected term with a reason",
    permissions=["recommend"],
)
def recommend_variant(modeladmin, request, queryset):
    if not request.user.is_moderator:
        raise PermissionDenied
    is_apply = "apply_recommendation" in request.POST
    form = RecommendationForm(
        request.POST if is_apply else None,
        terms=queryset,
    )
    if is_apply and form.is_valid():
        version = form.cleaned_data["version"]
        reason = form.cleaned_data["reason"]
        for term in queryset.order_by("pk"):
            try:
                recommend_term_variant(
                    moderator=request.user,
                    term_id=term.pk,
                    version_id=version.pk,
                    reason=reason,
                )
            except GlossaryError as exc:
                modeladmin.message_user(request, f"Term {term.pk}: {exc}", messages.ERROR)
            else:
                modeladmin.message_user(
                    request,
                    f"Updated recommended variant for term {term.pk}.",
                    messages.SUCCESS,
                )
        return None
    if is_apply and not form.is_valid() and "version" in form.errors:
        modeladmin.message_user(
            request,
            "Selected variant is not an eligible accepted variant.",
            messages.ERROR,
        )
    return render(
        request,
        "admin/glossary/recommend.html",
        {
            **modeladmin.admin_site.each_context(request),
            "title": "Set recommended variant",
            "form": form,
            "terms": queryset,
            "opts": modeladmin.model._meta,
        },
    )


@admin.action(description="Publish selected connector hints", permissions=["change"])
def publish_connector_hints(modeladmin, request, queryset):
    if not request.user.is_moderator:
        raise PermissionDenied
    queryset.update(is_published=True)


@admin.action(description="Unpublish selected connector hints", permissions=["change"])
def unpublish_connector_hints(modeladmin, request, queryset):
    if not request.user.is_moderator:
        raise PermissionDenied
    queryset.update(is_published=False)
