from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exports.api.serializers import DatasetJsonSerializer, ExportManifestSerializer
from apps.exports.domain import render_dataset_csv, render_dataset_json
from apps.exports.selectors import export_manifest, export_records


class DatasetCsvExportView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["exports"],
        operation_id="exports_dataset_csv_retrieve",
        responses={(200, "text/csv"): OpenApiTypes.STR},
    )
    def get(self, request):
        records = export_records()
        content = render_dataset_csv(records)
        response = HttpResponse(content, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="dataset.csv"'
        return response


class DatasetJsonExportView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["exports"],
        operation_id="exports_dataset_json_retrieve",
        responses={200: DatasetJsonSerializer},
    )
    def get(self, request):
        records = export_records()
        content = render_dataset_json(records)
        return HttpResponse(content, content_type="application/json; charset=utf-8")


class ExportManifestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["exports"],
        operation_id="exports_manifest_retrieve",
        responses={200: ExportManifestSerializer},
    )
    def get(self, request):
        return Response(ExportManifestSerializer(export_manifest()).data)
