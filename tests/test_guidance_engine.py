from datetime import date

from nadi_leaf.chart_adapter import BirthData, generate_chart
from nadi_leaf.guidance_engine import build_guidance_profile


def test_build_guidance_profile_uses_confirmed_feedback() -> None:
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

    profile = build_guidance_profile(
        chart,
        {
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

    assert profile["validated_anchors"][0]["id"] == "career_trial_and_accumulation"
    assert profile["guidance_items"][0]["priority"] == 1
    assert "稳定交付" in profile["guidance_items"][0]["title"]
