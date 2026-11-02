from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.contributions.models import ContributionVersion
from apps.verification.choices import COUNTED_DECISIONS, DECISIONS_REQUIRING_REASON, Decision
from apps.verification.domain.decisions import STATUSES, Rules, Vote, evaluate
from apps.verification.domain.reputation import updated_weight
from apps.verification.models import Finalization, QualitySettings, Review, ReviewerProfile

from .errors import ReviewConflict, ReviewError, ReviewForbidden

OPEN_STATUSES = (ContributionVersion.Status.SUBMITTED, ContributionVersion.Status.IN_REVIEW)


def _locked_version(version_id):
    try:
        return (
            ContributionVersion.objects.select_for_update(of=("self",))
            .select_related("contribution")
            .get(pk=version_id)
        )
    except ContributionVersion.DoesNotExist as exc:
        raise ReviewError("Unknown version.") from exc


def _settings(version):
    first = version.reviews.select_related("quality_settings").order_by("pk").first()
    if first:
        return first.quality_settings
    try:
        return QualitySettings.objects.select_for_update().get(is_active=True)
    except QualitySettings.DoesNotExist as exc:
        raise ReviewConflict("No active quality settings.") from exc


def _lock_reviewers(version, extra_ids=()):
    # A fixed order avoids deadlocks across versions sharing reviewers. Lock users
    # as well as profiles so concurrent first reviews cannot create two profiles.
    ids = set(version.reviews.values_list("reviewer_id", flat=True)) | set(extra_ids)
    return list(get_user_model().objects.select_for_update().filter(pk__in=ids).order_by("pk"))


def _profile(user_id, settings):
    profile, _ = ReviewerProfile.objects.get_or_create(
        user_id=user_id, defaults={"weight": settings.weight_initial}
    )
    return ReviewerProfile.objects.select_for_update().get(pk=profile.pk)


def _apply_weight(review, final_decision, settings, *, control=False):
    if review.reputation_applied_at or review.decision == Decision.DONT_KNOW:
        return
    profile = _profile(review.reviewer_id, settings)
    profile.weight = updated_weight(
        profile.weight,
        review.decision,
        final_decision,
        correct_step=settings.control_correct_step if control else settings.match_step,
        wrong_step=settings.control_wrong_step if control else settings.mismatch_step,
        weight_min=settings.weight_min,
        weight_max=settings.weight_max,
    )
    profile.save(update_fields=["weight", "updated_at"])
    review.reputation_applied_at = timezone.now()
    review.matched_final = review.decision == final_decision
    review.save(update_fields=["reputation_applied_at", "matched_final"])


def _finish(version, decision, settings, *, moderator=None, reason=""):
    result = Finalization.objects.create(
        version=version,
        decision=decision,
        quality_settings=settings,
        moderator=moderator,
        reason=reason,
    )
    if not version.is_control:
        for review in version.reviews.order_by("reviewer_id"):
            _apply_weight(review, decision, settings)
        version.status = STATUSES[decision]
    # Control versions never become accepted publication candidates.
    version.escalated = False
    version.save(update_fields=["status", "escalated"])
    return result


def _evaluate(version, settings):
    votes = [Vote(r.reviewer_id, r.decision, r.weight_snapshot) for r in version.reviews.all()]
    rules = Rules(
        settings.threshold, settings.min_votes, settings.max_votes, settings.min_supporters
    )
    result = evaluate(votes, rules)
    if version.is_control:
        if result.counted_votes >= settings.max_votes:
            return _finish(version, version.reference_decision, settings)
        return None
    if result.decision:
        return _finish(version, result.decision, settings)
    version.escalated = result.escalated
    version.save(update_fields=["escalated"])
    return None


@transaction.atomic
def submit_review(*, reviewer, version_id, decision, reason=""):
    version = _locked_version(version_id)
    users = _lock_reviewers(version, [reviewer.pk])
    reviewer = next(user for user in users if user.pk == reviewer.pk)
    if not reviewer.is_active or not reviewer.is_reviewer:
        raise ReviewForbidden("Reviewer access is required.")
    if version.contribution.author_id == reviewer.pk:
        raise ReviewForbidden("You cannot review your own contribution.")
    if decision not in Decision.values:
        raise ReviewError("Invalid decision.")
    reason = reason.strip()
    if decision in DECISIONS_REQUIRING_REASON and not reason:
        raise ReviewError("A reason is required for reject and edit.")
    if version.reviews.filter(reviewer=reviewer).exists():
        raise ReviewConflict("You have already reviewed this version.")
    settings = _settings(version)
    if (
        version.status not in OPEN_STATUSES
        or version.escalated
        or version.is_withdrawn
        or Finalization.objects.filter(version=version).exists()
        or version.reviews.filter(decision__in=COUNTED_DECISIONS).count() >= settings.max_votes
    ):
        raise ReviewConflict("This version is closed for review.")
    if version.is_control and version.reference_decision not in COUNTED_DECISIONS:
        raise ReviewError("Control version requires a counted reference decision.")
    profile = _profile(reviewer.pk, settings)
    review = Review.objects.create(
        version=version,
        reviewer=reviewer,
        decision=decision,
        reason=reason,
        weight_snapshot=profile.weight,
        quality_settings=settings,
    )
    if decision in COUNTED_DECISIONS:
        if version.status == ContributionVersion.Status.SUBMITTED:
            version.status = ContributionVersion.Status.IN_REVIEW
            version.save(update_fields=["status"])
        if version.is_control:
            _apply_weight(review, version.reference_decision, settings, control=True)
        _evaluate(version, settings)
    return review


@transaction.atomic
def finalize_version(*, version_id):
    """Retry automatic finalization safely; only the first result changes weight."""
    version = _locked_version(version_id)
    existing = Finalization.objects.filter(version=version).first()
    if existing:
        return existing
    if version.status not in OPEN_STATUSES or version.escalated:
        return None
    _lock_reviewers(version)
    return _evaluate(version, _settings(version))


@transaction.atomic
def resolve_version(*, moderator, version_id, decision, reason):
    version = _locked_version(version_id)
    users = _lock_reviewers(version, [moderator.pk])
    moderator = next(user for user in users if user.pk == moderator.pk)
    if not moderator.is_active or not moderator.is_moderator:
        raise ReviewForbidden("Moderator access is required.")
    reason = reason.strip()
    if decision not in COUNTED_DECISIONS or not reason:
        raise ReviewError("A counted decision and a reason are required.")
    existing = Finalization.objects.filter(version=version).first()
    if existing:
        if existing.moderator_id == moderator.pk and existing.decision == decision:
            return existing
        raise ReviewConflict("This version has already been finalized.")
    if not version.escalated or version.status != ContributionVersion.Status.IN_REVIEW:
        raise ReviewConflict("Only escalated versions may be resolved by a moderator.")
    if version.is_control:
        raise ReviewConflict("Control versions cannot receive a standard override.")
    return _finish(version, decision, _settings(version), moderator=moderator, reason=reason)
