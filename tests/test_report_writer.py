from datetime import date

from nadi_leaf.chart_adapter import BirthData, generate_chart
from nadi_leaf.evaluation import score_accuracy_profile, score_product_quality
from nadi_leaf.report_writer import render_premium_markdown_report
from nadi_leaf.models import ThemePack
from nadi_leaf.reading_engine import build_reading_bundle


PRIVATE_DEMO_PHRASES = [
    "你已经反馈",
    "你的进一步反馈",
]


def test_render_premium_markdown_report_contains_timeline_and_appendix() -> None:
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
        "validation_score": 94,
        "major_diffs": [],
        "minor_diffs": [{"field": "planet.Rahu.degree", "delta": 1.6347}],
    }
    quality_score = score_product_quality(chart=chart, reading=reading, cross_validation=cross_validation)
    accuracy_profile = score_accuracy_profile(chart=chart, reading=reading, cross_validation=cross_validation)

    report = render_premium_markdown_report(
        name="Demo Native",
        birth={
            "date": "2000-01-01",
            "time": "12:00",
            "location_name": "Chennai, India",
            "timezone_offset": 5.5,
        },
        reference_date=date(2026, 4, 23),
        preset_title="综合版",
        preset_subtitle="测试",
        chart=chart,
        reading=reading,
        quality_score=quality_score,
        accuracy_profile=accuracy_profile,
        cross_validation=cross_validation,
        feedback_profile={
            "checks": [
                {
                    "id": "career_trial_and_accumulation",
                    "claim": "职业前期试错较多，真正起势来自长期积累。",
                    "rating": "准",
                    "user_note": "准。",
                }
            ]
        },
    )

    assert "## 已验证锚点" in report
    assert "## 指导优先级" in report
    assert "## 过去、现在、未来" in report
    assert "## 技术附录" in report
    assert "名字边界" in report
    assert _private_demo_phrases(report) == []


def test_render_premium_markdown_report_can_render_all_16_kandams() -> None:
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
        requested_chapters=list(range(1, 17)),
        requested_theme_packs=[ThemePack.CAREER, ThemePack.WEALTH, ThemePack.SPIRITUALITY],
    ).to_dict()
    cross_validation = {
        "validation_score": 94,
        "major_diffs": [],
        "minor_diffs": [],
    }
    quality_score = score_product_quality(chart=chart, reading=reading, cross_validation=cross_validation)
    accuracy_profile = score_accuracy_profile(chart=chart, reading=reading, cross_validation=cross_validation)

    report = render_premium_markdown_report(
        name="Demo Native",
        birth={
            "date": "2000-01-01",
            "time": "12:00",
            "location_name": "Chennai, India",
            "timezone_offset": 5.5,
        },
        reference_date=date(2026, 4, 23),
        preset_title="完整16章版",
        preset_subtitle="测试",
        chart=chart,
        reading=reading,
        quality_score=quality_score,
        accuracy_profile=accuracy_profile,
        cross_validation=cross_validation,
    )

    assert "## 16 Kandam 完整正文" in report
    assert "### Kandam 16｜Dasa Bukthi：大运分运预测" in report
    assert "**现实中更可能这样表现**" in report
    assert "**这一章给你的指导**" in report
    assert "不预测死亡日期" in report
    assert "不提供诊断、药方或替代医疗建议" in report
    assert _private_demo_phrases(report) == []


def _private_demo_phrases(report: str) -> list[str]:
    return [phrase for phrase in PRIVATE_DEMO_PHRASES if phrase in report]
