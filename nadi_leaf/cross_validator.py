from __future__ import annotations

from datetime import date
from typing import Any

from .chart_adapter import BirthData, PLANET_ORDER, PyJHoraConfig, generate_chart
from .jyotishganit_adapter import generate_chart_with_jyotishganit

NUMERIC_MINOR_THRESHOLD = 0.35
NUMERIC_MAJOR_THRESHOLD = 1.0
NODE_NUMERIC_MINOR_THRESHOLD = 0.75
NODE_NUMERIC_MAJOR_THRESHOLD = 2.0


def cross_validate_birth_data(
    birth: BirthData,
    reference_date: date | None = None,
    primary_config: PyJHoraConfig | None = None,
) -> dict[str, Any]:
    primary_chart = generate_chart(birth, reference_date=reference_date, config=primary_config)
    secondary_chart = generate_chart_with_jyotishganit(birth, reference_date=reference_date)
    return compare_engine_charts(primary_chart, secondary_chart, reference_date=reference_date)


def calibrate_pyjhora_against_secondary_engine(
    birth: BirthData,
    reference_date: date | None = None,
    candidate_modes: list[str] | None = None,
) -> dict[str, Any]:
    candidate_modes = candidate_modes or ["LAHIRI", "KP", "SS_CITRA", "RAMAN", "YUKTESHWAR"]
    secondary_chart = generate_chart_with_jyotishganit(birth, reference_date=reference_date)
    candidates: list[dict[str, Any]] = []
    for mode in candidate_modes:
        try:
            primary_chart = generate_chart(
                birth,
                reference_date=reference_date,
                config=PyJHoraConfig(ayanamsa_mode=mode),
            )
            comparison = compare_engine_charts(primary_chart, secondary_chart, reference_date=reference_date)
            candidates.append(
                {
                    "ayanamsa_mode": mode,
                    "validation_score": comparison["validation_score"],
                    "major_diffs": len(comparison["major_diffs"]),
                    "minor_diffs": len(comparison["minor_diffs"]),
                    "current_mahadasha": primary_chart["chart_summary"]["current_mahadasha"],
                    "current_antardasha": primary_chart["chart_summary"]["current_antardasha"],
                }
            )
        except Exception as exc:
            candidates.append(
                {
                    "ayanamsa_mode": mode,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    ranked = sorted(
        candidates,
        key=lambda item: item.get("validation_score", -1),
        reverse=True,
    )
    return {
        "reference_date": (reference_date or date.today()).isoformat(),
        "candidates": ranked,
        "recommended": ranked[0] if ranked else None,
    }


def compare_engine_charts(
    primary_chart: dict[str, Any],
    secondary_chart: dict[str, Any],
    reference_date: date | None = None,
) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    minor_diffs: list[dict[str, Any]] = []
    major_diffs: list[dict[str, Any]] = []
    configuration_notes: list[str] = []

    _compare_string_field(
        matches,
        major_diffs,
        field="chart_summary.lagna",
        left=primary_chart["chart_summary"]["lagna"],
        right=secondary_chart["chart_summary"]["lagna"],
    )
    _compare_numeric_field(
        matches,
        minor_diffs,
        major_diffs,
        field="chart_summary.lagna_degree",
        left=float(primary_chart["chart_summary"]["lagna_degree"]),
        right=float(secondary_chart["chart_summary"]["lagna_degree"]),
    )
    _compare_string_field(
        matches,
        major_diffs,
        field="chart_summary.moon_sign",
        left=primary_chart["chart_summary"]["moon_sign"],
        right=secondary_chart["chart_summary"]["moon_sign"],
    )
    _compare_string_field(
        matches,
        major_diffs,
        field="chart_summary.nakshatra",
        left=primary_chart["chart_summary"]["nakshatra"],
        right=secondary_chart["chart_summary"]["nakshatra"],
    )
    _compare_string_field(
        matches,
        major_diffs,
        field="chart_summary.current_mahadasha",
        left=primary_chart["chart_summary"]["current_mahadasha"],
        right=secondary_chart["chart_summary"]["current_mahadasha"],
    )
    _compare_string_field(
        matches,
        major_diffs,
        field="chart_summary.current_antardasha",
        left=primary_chart["chart_summary"]["current_antardasha"],
        right=secondary_chart["chart_summary"]["current_antardasha"],
    )

    primary_planets = {planet["name"]: planet for planet in primary_chart.get("planets", [])}
    secondary_planets = {planet["name"]: planet for planet in secondary_chart.get("planets", [])}
    for planet_name in PLANET_ORDER:
        if planet_name not in primary_planets or planet_name not in secondary_planets:
            continue
        primary = primary_planets[planet_name]
        secondary = secondary_planets[planet_name]
        _compare_string_field(
            matches,
            major_diffs,
            field=f"planet.{planet_name}.sign",
            left=primary["sign"],
            right=secondary["sign"],
        )
        _compare_numeric_field(
            matches,
            minor_diffs,
            major_diffs,
            field=f"planet.{planet_name}.degree",
            left=float(primary["degree"]),
            right=float(secondary["degree"]),
            planet_name=planet_name,
        )
        _compare_integer_field(
            matches,
            minor_diffs,
            field=f"planet.{planet_name}.house_from_lagna",
            left=int(primary["house_from_lagna"]),
            right=int(secondary["house_from_lagna"]),
        )

    left_config = primary_chart.get("engine_config", {})
    right_config = secondary_chart.get("engine_config", {})
    if left_config.get("ayanamsa_mode") != right_config.get("ayanamsa_mode"):
        configuration_notes.append(
            "两套引擎当前 ayanamsa 配置不一致："
            f"{primary_chart['source_engine']}={left_config.get('ayanamsa_mode')}，"
            f"{secondary_chart['source_engine']}={right_config.get('ayanamsa_mode')}。"
        )

    left_ayanamsa = left_config.get("ayanamsa_value")
    right_ayanamsa = right_config.get("ayanamsa_value")
    if isinstance(left_ayanamsa, (int, float)) and isinstance(right_ayanamsa, (int, float)):
        delta = abs(float(left_ayanamsa) - float(right_ayanamsa))
        if delta > 0.05:
            configuration_notes.append(
                "两套引擎当前 ayanamsa 数值差异为 "
                f"{delta:.4f} 度，这足以带来 nakshatra / dasha 的实际偏移。"
            )

    if secondary_chart["engine_config"].get("dasha_reference_policy"):
        configuration_notes.append(
            "jyotishganit 的 dasha 对比结果已改为基于完整 period tree 按 reference_date 重算，"
            "没有直接采用库内的 current/upcoming 字段。"
        )

    validation_score = max(0, 100 - (len(major_diffs) * 12) - (len(minor_diffs) * 3))
    return {
        "reference_date": (reference_date or date.today()).isoformat(),
        "engines": {
            primary_chart["source_engine"]: {
                "chart_summary": primary_chart["chart_summary"],
                "engine_config": primary_chart.get("engine_config", {}),
            },
            secondary_chart["source_engine"]: {
                "chart_summary": secondary_chart["chart_summary"],
                "engine_config": secondary_chart.get("engine_config", {}),
            },
        },
        "matches": matches,
        "minor_diffs": minor_diffs,
        "major_diffs": major_diffs,
        "configuration_notes": configuration_notes,
        "validation_score": validation_score,
    }


def _compare_string_field(
    matches: list[dict[str, Any]],
    major_diffs: list[dict[str, Any]],
    *,
    field: str,
    left: str,
    right: str,
) -> None:
    if left == right:
        matches.append({"field": field, "value": left})
        return
    major_diffs.append({"field": field, "left": left, "right": right})


def _compare_numeric_field(
    matches: list[dict[str, Any]],
    minor_diffs: list[dict[str, Any]],
    major_diffs: list[dict[str, Any]],
    *,
    field: str,
    left: float,
    right: float,
    planet_name: str | None = None,
) -> None:
    delta = abs(left - right)
    minor_threshold = NUMERIC_MINOR_THRESHOLD
    major_threshold = NUMERIC_MAJOR_THRESHOLD
    if planet_name in {"Rahu", "Ketu"}:
        minor_threshold = NODE_NUMERIC_MINOR_THRESHOLD
        major_threshold = NODE_NUMERIC_MAJOR_THRESHOLD
    if delta <= minor_threshold:
        matches.append({"field": field, "left": round(left, 4), "right": round(right, 4), "delta": round(delta, 4)})
        return
    entry = {"field": field, "left": round(left, 4), "right": round(right, 4), "delta": round(delta, 4)}
    if delta >= major_threshold:
        major_diffs.append(entry)
    else:
        minor_diffs.append(entry)


def _compare_integer_field(
    matches: list[dict[str, Any]],
    minor_diffs: list[dict[str, Any]],
    *,
    field: str,
    left: int,
    right: int,
) -> None:
    if left == right:
        matches.append({"field": field, "value": left})
        return
    minor_diffs.append({"field": field, "left": left, "right": right})
