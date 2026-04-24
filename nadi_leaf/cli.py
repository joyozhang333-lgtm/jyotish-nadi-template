from __future__ import annotations

import argparse
import json
from datetime import date

from .chart_adapter import BirthData, PyJHoraConfig, generate_chart
from .cross_validator import calibrate_pyjhora_against_secondary_engine, compare_engine_charts
from .evaluation import score_product_quality
from .fingerprint import assess_fingerprint
from .jyotishganit_adapter import generate_chart_with_jyotishganit
from .models import ThemePack
from .reading_engine import build_reading_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Nadi Leaf reading bundle.")
    parser.add_argument("--date", required=True, help="Birth date in YYYY-MM-DD.")
    parser.add_argument("--time", required=True, help="Birth time in HH:MM or HH:MM:SS.")
    parser.add_argument("--location", required=True, help="Human-readable location label.")
    parser.add_argument("--latitude", required=True, type=float, help="Birth latitude.")
    parser.add_argument("--longitude", required=True, type=float, help="Birth longitude.")
    parser.add_argument("--timezone-offset", required=True, type=float, help="UTC offset, e.g. 8.")
    parser.add_argument("--timezone-name", default="UTC", help="IANA timezone name if known.")
    parser.add_argument("--chapters", default="1,4,7,10,12", help="Comma-separated kandam numbers.")
    parser.add_argument(
        "--themes",
        default="career,wealth,spirituality",
        help="Comma-separated theme pack ids.",
    )
    parser.add_argument("--fingerprint-image", default=None, help="Optional fingerprint image path.")
    parser.add_argument("--reference-date", default=None, help="Optional evaluation date in YYYY-MM-DD.")
    parser.add_argument("--pyjhora-ayanamsa", default="LAHIRI", help="Primary PyJHora ayanamsa mode.")
    parser.add_argument("--cross-validate", action="store_true", help="Run a secondary engine comparison.")
    parser.add_argument("--calibrate-primary-engine", action="store_true", help="Rank PyJHora ayanamsa candidates.")
    parser.add_argument("--quality-score", action="store_true", help="Score the output using the internal rubric.")
    args = parser.parse_args()

    reference_date = date.fromisoformat(args.reference_date) if args.reference_date else None
    primary_config = PyJHoraConfig(ayanamsa_mode=args.pyjhora_ayanamsa)
    chart = generate_chart(
        BirthData(
            date=args.date,
            time=args.time,
            location_name=args.location,
            latitude=args.latitude,
            longitude=args.longitude,
            timezone_offset=args.timezone_offset,
            timezone_name=args.timezone_name,
        ),
        reference_date=reference_date,
        config=primary_config,
    )
    fingerprint = assess_fingerprint(args.fingerprint_image)
    bundle = build_reading_bundle(
        chart=chart,
        requested_chapters=_parse_chapters(args.chapters),
        requested_theme_packs=_parse_theme_packs(args.themes),
        fingerprint_reading=fingerprint,
        reference_date=reference_date,
    )
    payload = {
        "chart": chart,
        "reading": bundle.to_dict(),
    }
    cross_validation = None
    if args.cross_validate:
        secondary_chart = generate_chart_with_jyotishganit(
            BirthData(
                date=args.date,
                time=args.time,
                location_name=args.location,
                latitude=args.latitude,
                longitude=args.longitude,
                timezone_offset=args.timezone_offset,
                timezone_name=args.timezone_name,
            ),
            reference_date=reference_date,
        )
        cross_validation = compare_engine_charts(chart, secondary_chart, reference_date=reference_date)
        payload["cross_validation"] = cross_validation
    if args.calibrate_primary_engine:
        payload["calibration"] = calibrate_pyjhora_against_secondary_engine(
            BirthData(
                date=args.date,
                time=args.time,
                location_name=args.location,
                latitude=args.latitude,
                longitude=args.longitude,
                timezone_offset=args.timezone_offset,
                timezone_name=args.timezone_name,
            ),
            reference_date=reference_date,
        )
    if args.quality_score:
        payload["quality_score"] = score_product_quality(
            chart=chart,
            reading=bundle.to_dict(),
            cross_validation=cross_validation,
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _parse_chapters(raw_value: str) -> list[int]:
    return [int(item.strip()) for item in raw_value.split(",") if item.strip()]


def _parse_theme_packs(raw_value: str) -> list[ThemePack]:
    return [ThemePack(item.strip()) for item in raw_value.split(",") if item.strip()]
