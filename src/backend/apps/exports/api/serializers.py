from rest_framework import serializers

from apps.contributions.models import Task
from common.choices import Domain


class ExportRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.ChoiceField(choices=Task.Type.choices, read_only=True)
    domain = serializers.ChoiceField(choices=Domain.choices, read_only=True)
    text_ru = serializers.CharField(read_only=True)
    text_kk = serializers.CharField(read_only=True)
    version = serializers.IntegerField(read_only=True)
    source_url = serializers.CharField(read_only=True, allow_blank=True)
    licence = serializers.CharField(read_only=True)
    attribution = serializers.CharField(read_only=True, allow_blank=True)
    is_original = serializers.BooleanField(read_only=True)
    modifications = serializers.IntegerField(read_only=True)
    contributor = serializers.CharField(read_only=True)
    accepted_at = serializers.DateTimeField(read_only=True)


class DatasetJsonSerializer(serializers.Serializer):
    records = ExportRecordSerializer(many=True, read_only=True)


class ManifestConditionSerializer(serializers.Serializer):
    licence = serializers.CharField(read_only=True)
    attribution = serializers.CharField(read_only=True, allow_blank=True)
    source_url = serializers.CharField(read_only=True, allow_blank=True)
    count = serializers.IntegerField(read_only=True)


class ExportManifestSerializer(serializers.Serializer):
    generated_at = serializers.DateTimeField(read_only=True)
    record_count = serializers.IntegerField(read_only=True)
    terms_version = serializers.CharField(read_only=True)
    dataset_licence = serializers.CharField(read_only=True)
    conditions = ManifestConditionSerializer(many=True, read_only=True)
