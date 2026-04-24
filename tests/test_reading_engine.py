from datetime import date

from nadi_leaf.chart_adapter import BirthData, generate_chart
from nadi_leaf.models import ThemePack
from nadi_leaf.reading_engine import build_reading_bundle


def test_build_reading_bundle_returns_requested_sections() -> None:
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

    bundle = build_reading_bundle(
        chart=chart,
        requested_chapters=[1, 4, 7, 10, 12],
        requested_theme_packs=[ThemePack.CAREER, ThemePack.WEALTH, ThemePack.SPIRITUALITY],
    )
    data = bundle.to_dict()

    assert data["requested_chapters"] == [1, 4, 7, 10, 12]
    assert data["requested_theme_packs"] == ["career", "wealth", "spirituality"]
    assert len(data["kandam_reading"]) == 5
    assert len(data["theme_sections"]) == 3
    assert len(data["identity_checks"]) >= 4
    assert len(data["timing_windows"]) >= 2
    assert any("真实叶片语料库" in item for item in data["missing_capabilities"])


def test_build_reading_bundle_allows_empty_theme_selection() -> None:
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

    bundle = build_reading_bundle(
        chart=chart,
        requested_chapters=[4, 7],
        requested_theme_packs=[],
    )
    data = bundle.to_dict()

    assert data["requested_chapters"] == [4, 7]
    assert data["requested_theme_packs"] == []
    assert [item["kandam"] for item in data["kandam_reading"]] == [4, 7]
    assert data["theme_sections"] == []


def test_default_reading_bundle_covers_all_16_kandams() -> None:
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

    data = build_reading_bundle(chart=chart).to_dict()

    assert data["requested_chapters"] == list(range(1, 17))
    assert [item["kandam"] for item in data["kandam_reading"]] == list(range(1, 17))
    assert all(len(item["claims"]) >= 3 for item in data["kandam_reading"])
    assert any(item["title"].startswith("Aushadha") for item in data["kandam_reading"])
    assert any(item["title"].startswith("Dasa Bukthi") for item in data["kandam_reading"])
