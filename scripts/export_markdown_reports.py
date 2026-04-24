from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datetime import date
import argparse
import json

from nadi_leaf.chart_adapter import BirthData, PyJHoraConfig, generate_chart
from nadi_leaf.cross_validator import compare_engine_charts
from nadi_leaf.evaluation import score_accuracy_profile, score_feedback_alignment, score_product_quality
from nadi_leaf.jyotishganit_adapter import generate_chart_with_jyotishganit
from nadi_leaf.models import ThemePack
from nadi_leaf.report_writer import render_premium_markdown_report
from nadi_leaf.reading_engine import build_reading_bundle


REPORT_PRESETS = [
    {
        "slug": "00-完整16章版",
        "title": "完整16章版",
        "subtitle": "用于一次性核对公开 Nadi 阅读常见的 16 个 Kandam：身份、财富、手足、家宅、子女、疾病债务、婚姻、风险、父缘福德、事业、收益、迁移灵性、业力补救、修法、健康倾向与大运分运。",
        "chapters": list(range(1, 17)),
        "themes": [ThemePack.CAREER, ThemePack.WEALTH, ThemePack.SPIRITUALITY],
    },
    {
        "slug": "01-综合版",
        "title": "综合版",
        "subtitle": "用于整体核对身份主轴、家宅、关系、事业、迁移与三大专题。",
        "chapters": [1, 4, 7, 10, 12],
        "themes": [ThemePack.CAREER, ThemePack.WEALTH, ThemePack.SPIRITUALITY],
    },
    {
        "slug": "02-事业财富版",
        "title": "事业财富版",
        "subtitle": "用于重点核对职业路径、角色权威、长期收入结构与财富累积方式。",
        "chapters": [1, 10],
        "themes": [ThemePack.CAREER, ThemePack.WEALTH],
    },
    {
        "slug": "03-关系家宅版",
        "title": "关系家宅版",
        "subtitle": "用于重点核对母缘、家宅、亲密关系和长期伴侣模式。",
        "chapters": [4, 7],
        "themes": [],
    },
    {
        "slug": "04-灵性迁移版",
        "title": "灵性迁移版",
        "subtitle": "用于重点核对迁移、抽离感、修行纪律与内在重组周期。",
        "chapters": [1, 12],
        "themes": [ThemePack.SPIRITUALITY],
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Markdown reports for a birth profile.")
    parser.add_argument("--date", required=True, help="Birth date in YYYY-MM-DD.")
    parser.add_argument("--time", required=True, help="Birth time in HH:MM or HH:MM:SS.")
    parser.add_argument("--location", required=True, help="Human-readable location label.")
    parser.add_argument("--latitude", required=True, type=float, help="Birth latitude.")
    parser.add_argument("--longitude", required=True, type=float, help="Birth longitude.")
    parser.add_argument("--timezone-offset", required=True, type=float, help="UTC offset, e.g. 8.")
    parser.add_argument("--timezone-name", default="UTC", help="IANA timezone name if known.")
    parser.add_argument("--reference-date", default=None, help="Optional evaluation date in YYYY-MM-DD.")
    parser.add_argument("--name", default="用户", help="Name used in the report title.")
    parser.add_argument("--output-dir", required=True, help="Directory to write the markdown reports to.")
    parser.add_argument("--pyjhora-ayanamsa", default="LAHIRI", help="Primary PyJHora ayanamsa mode.")
    parser.add_argument("--case-file", default=None, help="Optional JSON case file for scoring.")
    parser.add_argument("--feedback-file", default=None, help="Optional JSON feedback file for calibrated guidance.")
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
        reading=build_reading_bundle(chart=chart).to_dict(),
        cross_validation=cross_validation,
        corpus_case=corpus_case,
    )
    accuracy_profile = score_accuracy_profile(
        chart=chart,
        reading=build_reading_bundle(chart=chart).to_dict(),
        cross_validation=cross_validation,
        corpus_case=corpus_case,
    )
    feedback_alignment = score_feedback_alignment(feedback_profile)

    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    written_files: list[str] = []
    for preset in REPORT_PRESETS:
        bundle = build_reading_bundle(
            chart=chart,
            requested_chapters=preset["chapters"],
            requested_theme_packs=preset["themes"],
            reference_date=reference_date,
        )
        content = render_premium_markdown_report(
            name=args.name,
            birth={
                "date": birth.date,
                "time": birth.time,
                "location_name": birth.location_name,
                "timezone_offset": birth.timezone_offset,
            },
            reference_date=reference_date or date.today(),
            preset_title=preset["title"],
            preset_subtitle=preset["subtitle"],
            chart=chart,
            reading=bundle.to_dict(),
            quality_score=quality_score,
            accuracy_profile=accuracy_profile,
            cross_validation=cross_validation,
            feedback_profile=feedback_profile,
        )
        path = output_dir / f"{preset['slug']}.md"
        path.write_text(content, encoding="utf-8")
        written_files.append(str(path))

    manifest = {
        "name": args.name,
        "reference_date": (reference_date or date.today()).isoformat(),
        "output_dir": str(output_dir),
        "files": written_files,
        "quality_score": quality_score["total_score"],
        "accuracy_profile": accuracy_profile["total_score"],
        "chart_calculation_accuracy": _dimension_score(accuracy_profile, "chart_calculation_accuracy"),
        "feedback_alignment": feedback_alignment["total_score"],
        "feedback_sample_count": feedback_alignment["sample_count"],
        "feedback_file": args.feedback_file,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def _dimension_score(scorecard: dict, identifier: str) -> int:
    for item in scorecard.get("dimensions", []):
        if item["id"] == identifier:
            return int(item["score"])
    raise KeyError(identifier)


if __name__ == "__main__":
    main()
