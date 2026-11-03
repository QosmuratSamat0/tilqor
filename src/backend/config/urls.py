from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.contributions.api.urls import contribution_urlpatterns, task_urlpatterns
from apps.glossary.api.urls import catalogue_urlpatterns, dictionary_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny]),
        name="swagger-ui",
    ),
    path("api/", include("apps.core.urls")),
    path("api/auth/", include("apps.accounts.api.urls")),
    path("api/tasks/", include((task_urlpatterns, "tasks"))),
    path("api/contributions/", include((contribution_urlpatterns, "contributions"))),
    path("api/reviews/", include("apps.verification.api.urls")),
    path("api/dictionary/", include((dictionary_urlpatterns, "dictionary"))),
    path("api/catalogue/", include((catalogue_urlpatterns, "catalogue"))),
    path("api/exports/", include("apps.exports.api.urls")),
]
