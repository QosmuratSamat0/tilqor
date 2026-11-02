from django.contrib import admin
from django.urls import include, path

from apps.contributions.api.urls import contribution_urlpatterns, task_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.core.urls")),
    path("api/auth/", include("apps.accounts.api.urls")),
    path("api/tasks/", include((task_urlpatterns, "tasks"))),
    path("api/contributions/", include((contribution_urlpatterns, "contributions"))),
    path("api/reviews/", include("apps.verification.api.urls")),
]
