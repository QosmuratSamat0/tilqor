from rest_framework import serializers

from apps.contributions.models import ContributionVersion
from common.choices import Domain


class DictionaryVariantSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text_kk = serializers.CharField(read_only=True)
    public_name = serializers.CharField(read_only=True)


class RecommendedVariantSerializer(DictionaryVariantSerializer):
    reason = serializers.CharField(read_only=True, allow_blank=True)


class PendingVariantSerializer(DictionaryVariantSerializer):
    status = serializers.ChoiceField(
        choices=ContributionVersion.Status.choices,
        read_only=True,
    )


class DictionaryTermSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text_ru = serializers.CharField(read_only=True)
    definition = serializers.CharField(read_only=True, allow_blank=True)
    domain = serializers.ChoiceField(choices=Domain.choices, read_only=True)
    source = serializers.CharField(read_only=True, allow_blank=True)
    recommended = RecommendedVariantSerializer(read_only=True, allow_null=True)
    alternatives = DictionaryVariantSerializer(many=True, read_only=True)


class PaginatedDictionaryTermListSerializer(serializers.Serializer):
    count = serializers.IntegerField(read_only=True)
    next = serializers.URLField(allow_null=True, read_only=True)
    previous = serializers.URLField(allow_null=True, read_only=True)
    results = DictionaryTermSerializer(many=True, read_only=True)


class DictionaryTermDetailSerializer(DictionaryTermSerializer):
    pending = PendingVariantSerializer(many=True, read_only=True, required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, dict) and "pending" not in instance:
            data.pop("pending", None)
        return data


class WordOfTheDaySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    term_id = serializers.IntegerField(read_only=True)
    text_ru = serializers.CharField(read_only=True)
    definition = serializers.CharField(read_only=True, allow_blank=True)
    domain = serializers.ChoiceField(choices=Domain.choices, read_only=True)
    text_kk = serializers.CharField(read_only=True)
    public_name = serializers.CharField(read_only=True)
    variant = DictionaryVariantSerializer(read_only=True)


class TopWordSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    term_id = serializers.IntegerField(read_only=True)
    text_ru = serializers.CharField(read_only=True)
    domain = serializers.ChoiceField(choices=Domain.choices, read_only=True)
    text_kk = serializers.CharField(read_only=True)
    public_name = serializers.CharField(read_only=True)
    preference_count = serializers.IntegerField(read_only=True)


class ConnectorHintSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    text_ru = serializers.CharField(read_only=True)
    text_kk = serializers.CharField(read_only=True)
    example_kk = serializers.CharField(read_only=True)
    example_ru = serializers.CharField(read_only=True)
    source = serializers.CharField(read_only=True, allow_blank=True)
    licence = serializers.CharField(read_only=True, allow_blank=True)


class DailyCatalogueSerializer(serializers.Serializer):
    date = serializers.DateField(read_only=True)
    word_of_the_day = WordOfTheDaySerializer(read_only=True, allow_null=True)
    top_words = TopWordSerializer(many=True, read_only=True)
    connector_hints = ConnectorHintSerializer(many=True, read_only=True)
