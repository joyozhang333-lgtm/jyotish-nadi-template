from datetime import date

from nadi_leaf.chart_adapter import BirthData, generate_chart
from nadi_leaf.evaluation import score_accuracy_profile, score_feedback_alignment, score_product_quality
from nadi_leaf.models import ThemePack
from nadi_leaf.reading_engine import build_reading_bundle


def test_score_product_quality_returns_dimensioned_scorecard() -> None:
    chart = generate_chart(
        BirthData(
            date="2000-01-01",
            time="12:00",
            location_name="Chennai, India",
            latitude=13.0827,
            longitude=80.2707,
            timezone_offset=5.5,
            timezone_name="Asia/Kolkata",
        ),
        reference_date=date(2026, 4, 23),
    )
    reading = build_reading_bundle(
        chart=chart,
        requested_chapters=[1, 4, 7, 10, 12],
        requested_theme_packs=[ThemePack.CAREER, ThemePack.WEALTH, ThemePack.SPIRITUALITY],
    ).to_dict()
    cross_validation = {
        "major_diffs": [{"field": "chart_summary.current_mahadasha"}],
        "minor_diffs": [{"field": "planet.Sun.degree"}],
    }

    scorecard = score_product_quality(chart=chart, reading=reading, cross_validation=cross_validation)

    assert scorecard["max_score"] == 100
    assert len(scorecard["dimensions"]) == 5
    assert 0 <= scorecard["total_score"] <= 100
    assert scorecard["grade"] in {"A+", "A", "B", "C", "D"}


def test_score_accuracy_profile_separates_calculation_from_validation_maturity() -> None:
    chart = generate_chart(
        BirthData(
            date="2000-01-01",
            time="12:00",
            location_name="Chennai, India",
            latitude=13.0827,
            longitude=80.2707,
            timezone_offset=5.5,
            timezone_name="Asia/Kolkata",
        ),
        reference_date=date(2026, 4, 23),
    )
    reading = build_reading_bundle(
        chart=chart,
        requested_chapters=[1, 4, 7, 10, 12],
        requested_theme_packs=[ThemePack.CAREER, ThemePack.WEALTH, ThemePack.SPIRITUALITY],
    ).to_dict()
    cross_validation = {
        "major_diffs": [],
        "minor_diffs": [{"field": "planet.Rahu.degree"}, {"field": "planet.Ketu.degree"}],
    }
    corpus_case = {
        "expected_chart_summary": {
            "lagna": "Pisces",
            "moon_sign": "Libra",
            "nakshatra": "Swati",
        },
        "validation_meta": {
            "benchmark_case_count": 1,
            "expert_review_count": 0,
            "longitudinal_follow_up_count": 0,
        },
    }

    profile = score_accuracy_profile(
        chart=chart,
        reading=reading,
        cross_validation=cross_validation,
        corpus_case=corpus_case,
    )

    dimensions = {item["id"]: item for item in profile["dimensions"]}
    assert profile["max_score"] == 100
    assert len(profile["dimensions"]) == 3
    assert dimensions["chart_calculation_accuracy"]["score"] >= 95
    assert dimensions["empirical_validation_maturity"]["score"] < dimensions["chart_calculation_accuracy"]["score"]
    assert "95%" not in profile["claim_boundary"]


def test_score_feedback_alignment_uses_user_ratings_without_overclaiming() -> None:
    profile = score_feedback_alignment(
        {
            "checks": [
                {"rating": "准"},
                {"rating": "准"},
                {"rating": "半准"},
                {"rating": "不准"},
            ]
        }
    )

    assert profile["total_score"] == 62
    assert profile["sample_count"] == 4
    assert profile["rating_counts"] == {"准": 2, "半准": 1, "不准": 1}
    assert "不能声称总体准确率" in profile["claim_boundary"]
