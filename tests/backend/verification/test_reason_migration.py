"""Existing comments survive upgrade and rollback; new categorical reasons remain meaningful."""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

OLD = ("verification", "0003_review_matched_final_review_reputation_applied_at_and_more")
NEW = ("verification", "0004_review_reason_codes")


@pytest.mark.django_db(transaction=True)
def test_reason_migration_round_trip(version, reviewer_factory):
    executor = MigrationExecutor(connection)
    leaves = executor.loader.graph.leaf_nodes()
    try:
        executor.migrate([OLD])
        old_apps = executor.loader.project_state([OLD]).apps
        Review = old_apps.get_model("verification", "Review")
        Settings = old_apps.get_model("verification", "QualitySettings")
        settings, _ = Settings.objects.get_or_create(version=1, defaults={"is_active": True})
        common = {
            "version_id": version.pk,
            "quality_settings_id": settings.pk,
            "weight_snapshot": "1.00",
        }
        rows = []
        for decision in ("accept", "dont_know", "reject", "edit"):
            rows.append(
                Review.objects.create(
                    **common,
                    reviewer_id=reviewer_factory().pk,
                    decision=decision,
                    reason=f"Existing {decision} comment",
                )
            )
        executor = MigrationExecutor(connection)
        executor.migrate([NEW])
        Review = executor.loader.project_state([NEW]).apps.get_model("verification", "Review")
        for original in rows:
            migrated = Review.objects.get(pk=original.pk)
            assert migrated.reason == original.reason
            assert migrated.reason_code == (
                "other" if original.decision in ("reject", "edit") else ""
            )
        categorical = Review.objects.create(
            **common,
            reviewer_id=reviewer_factory().pk,
            decision="edit",
            reason_code="russian_connector",
            reason="",
        )
        executor = MigrationExecutor(connection)
        executor.migrate([OLD])
        Review = executor.loader.project_state([OLD]).apps.get_model("verification", "Review")
        assert Review.objects.get(pk=categorical.pk).reason == "Russian connector"
        assert [Review.objects.get(pk=row.pk).reason for row in rows] == [
            row.reason for row in rows
        ]
    finally:
        MigrationExecutor(connection).migrate(leaves)
