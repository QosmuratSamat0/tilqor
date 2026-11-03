from django.urls import path

from apps.glossary.api.views import DailyCatalogueView, DictionaryDetailView, DictionaryListView

dictionary_urlpatterns = [
    path("", DictionaryListView.as_view(), name="dictionary-list"),
    path("<int:term_id>/", DictionaryDetailView.as_view(), name="dictionary-detail"),
]

catalogue_urlpatterns = [
    path("today/", DailyCatalogueView.as_view(), name="catalogue-today"),
]
