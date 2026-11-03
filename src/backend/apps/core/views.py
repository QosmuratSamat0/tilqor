from django.db import DatabaseError, connection
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    database = serializers.CharField()


class HealthView(APIView):
    """Reports whether the backend is running and the database is reachable."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["health"],
        responses={200: HealthResponseSerializer, 503: HealthResponseSerializer},
    )
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except DatabaseError:
            return Response(
                {"status": "error", "database": "unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"status": "ok", "database": "ok"})
