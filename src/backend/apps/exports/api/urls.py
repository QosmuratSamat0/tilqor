from django.urls import path

from apps.exports.api.views import (
    DatasetCsvExportView,
    DatasetJsonExportView,
    ExportManifestView,
)

urlpatterns = [
    path("dataset.csv", DatasetCsvExportView.as_view(), name="exports-dataset-csv"),
    path("dataset.json", DatasetJsonExportView.as_view(), name="exports-dataset-json"),
    path("manifest.json", ExportManifestView.as_view(), name="exports-manifest"),
]
