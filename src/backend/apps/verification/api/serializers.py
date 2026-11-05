from rest_framework import serializers

from apps.contributions.models import ContributionVersion
from apps.verification.choices import Decision, ReviewReason
from apps.verification.domain.reasons import reason_error
from apps.verification.models import Review


class ReviewInputSerializer(serializers.Serializer):
    version_id = serializers.IntegerField(min_value=1)
    decision = serializers.ChoiceField(choices=Decision.choices)
    reason_code = serializers.ChoiceField(
        choices=ReviewReason.choices, required=False, allow_blank=True, default=""
    )
    reason = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        error = reason_error(attrs["decision"], attrs["reason_code"], attrs["reason"])
        if error:
            field, code, message = error
            raise serializers.ValidationError({field: serializers.ErrorDetail(message, code=code)})
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    reason_code = serializers.ChoiceField(
        choices=ReviewReason.choices, allow_blank=True, read_only=True
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "version_id",
            "decision",
            "reason_code",
            "reason",
            "weight_snapshot",
            "created_at",
        )
        read_only_fields = fields


class QueueSerializer(serializers.ModelSerializer):
    task_type = serializers.CharField(source="contribution.task.type")
    domain = serializers.CharField(source="contribution.task.domain")
    text_ru = serializers.SerializerMethodField()
    definition = serializers.SerializerMethodField()

    class Meta:
        model = ContributionVersion
        fields = ("id", "number", "text_kk", "task_type", "domain", "text_ru", "definition")
        read_only_fields = fields

    def get_text_ru(self, version) -> str:
        task = version.contribution.task
        return task.source_sentence.text_ru if task.source_sentence_id else task.term.text_ru

    def get_definition(self, version) -> str:
        task = version.contribution.task
        return task.term.definition if task.term_id else ""


class StatsSerializer(serializers.Serializer):
    weight = serializers.DecimalField(max_digits=3, decimal_places=2)
    matched_votes = serializers.IntegerField()
    finalized_votes = serializers.IntegerField()
    match_share = serializers.DecimalField(max_digits=9, decimal_places=8, allow_null=True)
