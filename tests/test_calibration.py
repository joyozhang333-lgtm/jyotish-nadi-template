from datetime import date

from nadi_leaf.chart_adapter import BirthData
from nadi_leaf.cross_validator import calibrate_pyjhora_against_secondary_engine


def test_calibration_returns_ranked_candidates() -> None:
    result = calibrate_pyjhora_against_secondary_engine(
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
        candidate_modes=["LAHIRI", "KP", "RAMAN"],
    )

    assert result["recommended"] is not None
    assert result["recommended"]["ayanamsa_mode"] in {"LAHIRI", "KP"}
    assert len(result["candidates"]) == 3
