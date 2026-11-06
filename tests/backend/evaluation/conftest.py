import pytest

from apps.evaluation.domain.types import Ballot


@pytest.fixture
def ballots():
    def make(decisions, record_id="r", reviewers=None):
        return [
            Ballot(
                record_id, index + 1, str(reviewers[index]) if reviewers else str(index), decision
            )
            for index, decision in enumerate(decisions)
        ]

    return make
