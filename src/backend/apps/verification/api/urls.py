from django.urls import path

from .views import QueueView, ReviewView, StatsView

app_name = "reviews"
urlpatterns = [
    path("", ReviewView.as_view(), name="submit"),
    path("queue/", QueueView.as_view(), name="queue"),
    path("me/stats/", StatsView.as_view(), name="stats"),
]
