from django.urls import path

from .views import (
    ContributionVersionView,
    MyContributionsView,
    TaskContributionView,
    TaskDetailView,
    TaskListView,
    TaskPreferenceView,
)

task_urlpatterns = [
    path("", TaskListView.as_view(), name="list"),
    path("<int:task_id>/", TaskDetailView.as_view(), name="detail"),
    path("<int:task_id>/contributions/", TaskContributionView.as_view(), name="contribute"),
    path("<int:task_id>/preference/", TaskPreferenceView.as_view(), name="preference"),
]

contribution_urlpatterns = [
    path("me/", MyContributionsView.as_view(), name="me"),
    path("<int:contribution_id>/versions/", ContributionVersionView.as_view(), name="versions"),
]

urlpatterns = contribution_urlpatterns
