from fractions import Fraction

import pytest

from apps.evaluation.domain.alpha import nominal_alpha


def test_hand_computed_coincidences():
    """Three units: (A,A), (A,B), (B,B), with an extra missing slot each.

    1. Each pairable unit has m=2, so divide ordered pairs by m-1=1.
       (A,A) adds 2 to O_AA; (A,B) adds 1 to O_AB and O_BA;
       (B,B) adds 2 to O_BB. Coincidence matrix O = [[2,1],[1,2]].
    2. Margins n_A=n_B=3; n=6. D_o=(O_AB+O_BA)/n=2/6=1/3.
    3. D_e=(n_A*n_B+n_B*n_A)/(n*(n-1))=18/30=3/5.
    4. Alpha=1-(1/3)/(3/5)=1-5/9=4/9 (exact fraction).
    """
    result = nominal_alpha([["A", "A", None], ["A", "B", None], ["B", "B", None]])
    assert result.value == pytest.approx(float(Fraction(4, 9)), abs=1e-6)
    assert result.observed_disagreement == pytest.approx(1 / 3)
    assert result.expected_disagreement == pytest.approx(3 / 5)


def test_published_nominal_missing_example():
    """Transcribed from Krippendorff (2011), section C, pp. 4-5, not a guessed value.

    https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff%27s%20Alpha-Reliability.pdf
    Four observer rows below, 12 units, 7 missing ratings. The last unit has
    only B's rating 3 and is dropped: 11 units, 40 pairable values. Printed
    alpha_nominal = 0.743, to three decimal places, on page 5. Margins are
    [9,13,10,5,3], diagonal [7,10,8,4,3], D_o=8/40=1/5,
    D_e=(1600-384)/(40*39)=152/195; exact alpha=113/152.
    """
    raters = [
        [1, 2, 3, 3, 2, 1, 4, 1, 2, None, None, None],
        [1, 2, 3, 3, 2, 2, 4, 1, 2, 5, None, 3],
        [None, 3, 3, 3, 2, 3, 4, 2, 2, 5, 1, None],
        [1, 2, 3, 3, 2, 4, 4, 1, 2, 5, 1, None],
    ]
    result = nominal_alpha(zip(*raters, strict=True))
    assert (result.pairable_units, result.pairable_values) == (11, 40)
    assert round(result.value, 3) == 0.743
    assert result.value == pytest.approx(float(Fraction(113, 152)), abs=1e-6)


@pytest.mark.parametrize(
    "units", [[], [[None]], [["A", "B"]], [["A"], ["B"]], [["A", "A"], ["A", "A"]]]
)
def test_degenerate_samples_are_explicitly_undefined(units):
    result = nominal_alpha(units)
    assert result.value is None
    assert result.reason


def test_missing_and_unpairable_values_do_not_enter_margins():
    complete = [["A", "A"], ["A", "B"], ["B", "B"]]
    missing = [*complete, ["new-category", None], [None, "dont_know"]]
    assert nominal_alpha(missing) == nominal_alpha(complete)


def test_systematic_disagreement_can_be_negative():
    assert nominal_alpha([["A", "B"], ["A", "B"]]).value == pytest.approx(-0.5)
