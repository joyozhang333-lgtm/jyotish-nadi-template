from nadi_leaf.cross_validator import compare_engine_charts


def test_compare_engine_charts_surfaces_major_and_minor_diffs() -> None:
    primary = {
        "source_engine": "pyjhora",
        "engine_config": {"ayanamsa_mode": "TRUE_PUSHYA", "ayanamsa_value": 24.05},
        "chart_summary": {
            "lagna": "Leo",
            "lagna_degree": 21.94,
            "moon_sign": "Pisces",
            "nakshatra": "Uttara Bhadrapada",
            "current_mahadasha": "Ketu",
            "current_antardasha": "Ketu / Mercury",
        },
        "planets": [
            {"name": "Sun", "sign": "Aquarius", "degree": 18.1, "house_from_lagna": 7},
            {"name": "Moon", "sign": "Pisces", "degree": 12.2, "house_from_lagna": 8},
        ],
    }
    secondary = {
        "source_engine": "jyotishganit",
        "engine_config": {
            "ayanamsa_mode": "True Chitra Paksha",
            "ayanamsa_value": 23.84,
            "dasha_reference_policy": "recomputed_from_all_periods_using_reference_date",
        },
        "chart_summary": {
            "lagna": "Leo",
            "lagna_degree": 21.61,
            "moon_sign": "Pisces",
            "nakshatra": "Uttara Bhadrapada",
            "current_mahadasha": "Venus",
            "current_antardasha": "Venus / Saturn",
        },
        "planets": [
            {"name": "Sun", "sign": "Aquarius", "degree": 18.55, "house_from_lagna": 7},
            {"name": "Moon", "sign": "Pisces", "degree": 12.18, "house_from_lagna": 8},
        ],
    }

    result = compare_engine_charts(primary, secondary)

    assert any(item["field"] == "chart_summary.lagna" for item in result["matches"])
    assert any(item["field"] == "chart_summary.current_mahadasha" for item in result["major_diffs"])
    assert any(item["field"] == "planet.Sun.degree" for item in result["minor_diffs"])
    assert result["validation_score"] < 100
    assert any("ayanamsa" in note for note in result["configuration_notes"])
