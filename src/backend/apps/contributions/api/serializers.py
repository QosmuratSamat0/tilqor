from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.contributions.models import Contribution, ContributionVersion, Task, VariantPreference


class TextInputSerializer(serializers.Serializer):
    text_kk = serializers.CharField(allow_blank=True, trim_whitespace=False)


class PreferenceInputSerializer(serializers.Serializer):
    version_id = serializers.IntegerField(min_value=1)


class TaskSerializer(serializers.ModelSerializer):
    text_ru = serializers.SerializerMethodField()
    definition = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ("id", "type", "domain", "text_ru", "definition", "created_at")
        read_only_fields = fields

    def get_text_ru(self, task: Task) -> str:
        return task.source_sentence.text_ru if task.source_sentence_id else task.term.text_ru

    def get_definition(self, task: Task) -> str:
        return task.term.definition if task.term_id else ""


class VariantSerializer(serializers.ModelSerializer):
    public_name = serializers.CharField(source="contribution.author.public_name", read_only=True)

    class Meta:
        model = ContributionVersion
        fields = ("id", "text_kk", "status", "public_name", "created_at")
        read_only_fields = fields


class TaskDetailSerializer(TaskSerializer):
    variants = VariantSerializer(source="visible_variants", many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = (*TaskSerializer.Meta.fields, "variants")
        read_only_fields = fields


class VersionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContributionVersion
        fields = ("id", "number", "text_kk", "status", "created_at")
        read_only_fields = fields


class ContributionSubmissionSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="contribution.id", read_only=True)
    task_id = serializers.IntegerField(source="contribution.task_id", read_only=True)
    created_at = serializers.DateTimeField(source="contribution.created_at", read_only=True)
    version = VersionSummarySerializer(read_only=True)
    warnings = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()), read_only=True
    )


class VersionSubmissionSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="version.id", read_only=True)
    contribution_id = serializers.IntegerField(source="version.contribution_id", read_only=True)
    number = serializers.IntegerField(source="version.number", read_only=True)
    text_kk = serializers.CharField(source="version.text_kk", read_only=True)
    status = serializers.CharField(source="version.status", read_only=True)
    created_at = serializers.DateTimeField(source="version.created_at", read_only=True)
    warnings = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()), read_only=True
    )


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantPreference
        fields = ("id", "task_id", "version_id", "updated_at")
        read_only_fields = fields


class OwnVersionSerializer(serializers.ModelSerializer):
    decision_reasons = serializers.SerializerMethodField()

    class Meta:
        model = ContributionVersion
        fields = ("id", "number", "text_kk", "status", "decision_reasons", "created_at")
        read_only_fields = fields

    def get_decision_reasons(self, version: ContributionVersion) -> list[str]:
        try:
            finalization = version.finalization
        except ObjectDoesNotExist:
            return []
        if finalization is None:
            return []
        reasons: list[str] = []
        seen: set[str] = set()
        reviews = (
            version.reviews.all()
            if "reviews" in getattr(version, "_prefetched_objects_cache", {})
            else version.reviews.order_by("created_at", "pk")
        )
        candidates = [finalization.reason]
        candidates.extend(
            review.reason for review in reviews if review.decision == finalization.decision
        )
        for reason in candidates:
            if reason and reason not in seen:
                seen.add(reason)
                reasons.append(reason)
        return reasons


class OwnContributionSerializer(serializers.ModelSerializer):
    task_type = serializers.CharField(source="task.type", read_only=True)
    domain = serializers.CharField(source="task.domain", read_only=True)
    text_ru = serializers.SerializerMethodField()
    versions = OwnVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Contribution
        fields = ("id", "task_id", "task_type", "domain", "text_ru", "created_at", "versions")
        read_only_fields = fields

    def get_text_ru(self, contribution: Contribution) -> str:
        task = contribution.task
        return task.source_sentence.text_ru if task.source_sentence_id else task.term.text_ru
