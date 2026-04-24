from datetime import date

from nadi_leaf.chart_adapter import BirthData, generate_chart


def test_generate_chart_returns_expected_summary() -> None:
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

    assert chart["source_engine"] == "pyjhora"
    assert chart["chart_summary"]["lagna"] == "Pisces"
    assert chart["chart_summary"]["moon_sign"] == "Libra"
    assert chart["chart_summary"]["nakshatra"] == "Swati"
    assert chart["chart_summary"]["current_mahadasha"] == "Saturn"
    assert chart["chart_summary"]["current_antardasha"] == "Saturn / Ketu"
    assert chart["vargas"]["navamsa"]["lagna"] == "Scorpio"
    assert chart["engine_config"]["ayanamsa_mode"] == "LAHIRI"
    assert len(chart["planets"]) == 9
    assert chart["dashas"][0]["status"] == "current"
    assert chart["dashas"][1]["status"] == "next"
    assert len(chart["dasha_timeline"]["mahadasha"]) >= 5
    assert chart["dasha_timeline"]["mahadasha"][0]["label"]
