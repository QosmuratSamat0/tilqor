from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.utils import (
    OpenApiExample,
    PolymorphicProxySerializer,
    extend_schema_serializer,
)
from rest_framework import serializers

DETAIL_ERROR_EXAMPLE = OpenApiExample(
    "DetailErrorExample",
    summary="Top-level detail error",
    value={"detail": "Authentication credentials were not provided."},
    response_only=True,
    status_codes=["400", "403", "404", "409"],
)

FIELD_ERRORS_EXAMPLE = OpenApiExample(
    "FieldErrorsExample",
    summary="Field-keyed error messages",
    value={"text_kk": ["Text cannot be empty."]},
    response_only=True,
    status_codes=["400", "403", "409"],
)


@extend_schema_serializer(
    component_name="DetailError",
    examples=[DETAIL_ERROR_EXAMPLE],
)
class DetailErrorSerializer(serializers.Serializer):
    """Error response with a single top-level `detail` message."""

    detail = serializers.CharField()
    code = serializers.CharField(required=False)
    params = serializers.DictField(child=serializers.JSONField(), required=False)


@extend_schema_serializer(
    component_name="FieldErrors",
    examples=[FIELD_ERRORS_EXAMPLE],
)
class FieldErrorsSerializer(serializers.Serializer):
    """Error response mapping field names to lists of error messages."""


class DetailErrorSerializerExtension(OpenApiSerializerExtension):
    target_class = "common.serializers.DetailErrorSerializer"

    def get_name(self):
        return "DetailError"

    def map_serializer(self, auto_schema, direction):
        schema = auto_schema._map_basic_serializer(self.target, direction)
        schema["example"] = {"detail": "Authentication credentials were not provided."}
        return schema


class FieldErrorsSerializerExtension(OpenApiSerializerExtension):
    target_class = "common.serializers.FieldErrorsSerializer"

    def get_name(self):
        return "FieldErrors"

    def map_serializer(self, auto_schema, direction):
        return {
            "type": "object",
            "description": "Field messages plus stable codes and interpolation parameters.",
            "properties": {
                "codes": {
                    "type": "object",
                    "additionalProperties": {"type": "array", "items": {"type": "string"}},
                },
                "params": {"type": "object", "additionalProperties": {"type": "object"}},
            },
            "additionalProperties": {
                "oneOf": [
                    {"type": "array", "items": {"type": "string"}},
                    {"type": "object", "additionalProperties": {}},
                ],
            },
            "example": {"text_kk": ["Text cannot be empty."]},
        }


AnyErrorSerializer = PolymorphicProxySerializer(
    component_name="ErrorResponse",
    serializers=[DetailErrorSerializer, FieldErrorsSerializer],
    resource_type_field_name=None,
)
