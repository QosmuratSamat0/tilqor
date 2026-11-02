from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    """Standard API error response (`{"detail": "..."}` or field-keyed `{field: ["..."]}`)."""

    detail = serializers.CharField(required=False)
