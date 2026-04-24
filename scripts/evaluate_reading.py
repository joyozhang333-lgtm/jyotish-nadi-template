from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
from datetime import date

from nadi_leaf.chart_adapter import BirthData, PyJHoraConfig, generate_chart
from nadi_leaf.cross_validator import calibrate_pyjhora_against_secondary_engine, compare_engine_charts
from nadi_leaf.evaluation import score_accuracy_profile, score_feedback_alignment, score_product_quality
from nadi_leaf.fingerprint import assess_fingerprint
from nadi_leaf.jyotishganit_adapter import generate_chart_with_jyotishganit
from nadi_leaf.models import ThemePack
from nadi_leaf.reading_engine import build_reading_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a Nadi Leaf reading bundle.")
    parser.add_argument("--date", required=True, help="Birth date in YYYY-MM-DD.")
    parser.add_argument("--time", required=True, help="Birth time in HH:MM or HH:MM:SS.")
    parser.add_argument("--location", required=True, help="Human-readable location label.")
    parser.add_argument("--latitude", required=True, type=float, help="Birth latitude.")
    parser.add_argument("--longitude", required=True, type=float, help="Birth longitude.")
    parser.add_argument("--timezone-offset", required=True, type=float, help="UTC offset, e.g. 8.")
    parser.add_argument("--timezone-name", default="UTC", help="IANA timezone name if known.")
    parser.add_argument("--chapters", default=",".join(str(item) for item in range(1, 17)), help="Comma-separated kandam numbers.")
    parser.add_argument(
        "--themes",
        default="career,wealth,spirituality",
        help="Comma-separated theme pack ids.",
    )
    parser.add_argument("--fingerprint-image", default=None, help="Optional fingerprint image path.")
    parser.add_argument("--reference-date", default=None, help="Optional evaluation date in YYYY-MM-DD.")
    parser.add_argument("--pyjhora-ayanamsa", default="LAHIRI", help="Primary PyJHora ayanamsa mode.")
    parser.add_argument("--case-file", default=None, help="Optional JSON case file for benchmark scoring.")
    parser.add_argument("--feedback-file", default=None, help="Optional JSON feedback file for user alignment scoring.")
    parser.add_argument("--cross-validate", action="store_true", help="Run the second-engine comparison.")
    parser.add_argument("--calibrate-primary-engine", action="store_true", help="Rank PyJHora ayanamsa candidates.")
    parser.add_argument("--min-product-score", default=None, type=int, help="Fail with exit code 2 if product quality is below this score.")
    parser.add_argument("--min-accuracy-profile", default=None, type=int, help="Fail with exit code 2 if accuracy profile is below this score.")
    args = parser.parse_args()

    birth = BirthData(
        date=args.date,
        time=args.time,
        location_name=args.location,
        latitude=args.latitude,
        longitude=args.longitude,
        timezone_offset=args.timezone_offset,
        timezone_name=args.timezone_name,
    )
    reference_date = date.fromisoformat(args.reference_date) if args.reference_date else None
    chart = generate_chart(
        birth,
        reference_date=reference_date,
        config=PyJHoraConfig(ayanamsa_mode=args.pyjhora_ayanamsa),
    )
    reading = build_reading_bundle(
        chart=chart,
        requested_chapters=[int(item.strip()) for item in args.chapters.split(",") if item.strip()],
        requested_theme_packs=[ThemePack(item.strip()) for item in args.themes.split(",") if item.strip()],
        fingerprint_reading=assess_fingerprint(args.fingerprint_image),
        reference_date=reference_date,
    ).to_dict()
    cross_validation = None
    if args.cross_validate:
        secondary_chart = generate_chart_with_jyotishganit(birth, reference_date=reference_date)
        cross_validation = compare_engine_charts(chart, secondary_chart, reference_date=reference_date)

    corpus_case = None
    if args.case_file:
        corpus_case = json.loads(Path(args.case_file).read_text(encoding="utf-8"))
    feedback_profile = None
    if args.feedback_file:
        feedback_profile = json.loads(Path(args.feedback_file).read_text(encoding="utf-8"))
    quality_score = score_product_quality(
        chart=chart,
        reading=reading,
        cross_validation=cross_validation,
        corpus_case=corpus_case,
    )
    accuracy_profile = score_accuracy_profile(
        chart=chart,
        reading=reading,
        cross_validation=cross_validation,
        corpus_case=corpus_case,
    )
    payload = {
        "chart_summary": chart["chart_summary"],
        "cross_validation": cross_validation,
        "quality_score": quality_score,
        "accuracy_profile": accuracy_profile,
        "feedback_alignment": score_feedback_alignment(feedback_profile),
    }
    if args.calibrate_primary_engine:
        payload["calibration"] = calibrate_pyjhora_against_secondary_engine(birth, reference_date=reference_date)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.min_product_score is not None and quality_score["total_score"] < args.min_product_score:
        raise SystemExit(2)
    if args.min_accuracy_profile is not None and accuracy_profile["total_score"] < args.min_accuracy_profile:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
