from __future__ import annotations

from contextlib import redirect_stdout
from datetime import date, datetime
import io
from typing import Any

from .chart_adapter import (
    BirthData,
    PLANET_ORDER,
    SIGN_NAMES,
    _build_input_quality,
    _normalize_time_string,
    _parse_birth_datetime,
    sign_lord_name,
)


def generate_chart_with_jyotishganit(birth: BirthData, reference_date: date | None = None) -> dict[str, Any]:
    try:
        from jyotishganit import calculate_birth_chart
    except ImportError as exc:
        raise RuntimeError("jyotishganit is not installed in the current environment.") from exc

    parsed_birth = _parse_birth_datetime(birth.date, birth.time)
    with redirect_stdout(io.StringIO()):
        raw_chart = calculate_birth_chart(
            parsed_birth,
            birth.latitude,
            birth.longitude,
            timezone_offset=birth.timezone_offset,
            location_name=birth.location_name,
            name="Nadi Leaf",
        )

    planets_by_name = {planet.celestial_body: planet for planet in raw_chart.d1_chart.planets}
    lagna_house = raw_chart.d1_chart.houses[0]
    moon = planets_by_name["Moon"]
    navamsa = _extract_navamsa_summary(raw_chart.divisional_charts.get("d9"))
    dasha_balance = _normalize_balance(raw_chart.dashas.balance)
    reference = reference_date or date.today()
    current_maha, next_maha = _extract_current_and_next_dasha_periods(
        _flatten_mahadashas(raw_chart.dashas.all),
        reference,
        birth.timezone_offset,
        level="mahadasha",
    )
    current_antara, next_antara = _extract_current_and_next_dasha_periods(
        _flatten_antardashas(raw_chart.dashas.all),
        reference,
        birth.timezone_offset,
        level="antardasha",
    )

    planets = []
    for name in PLANET_ORDER:
        planet = planets_by_name[name]
        planets.append(
            {
                "name": name,
                "sign": planet.sign,
                "sign_index": SIGN_NAMES.index(planet.sign),
                "degree": round(float(planet.sign_degrees), 4),
                "house_from_lagna": int(planet.house),
            }
        )

    return {
        "input_quality": _build_input_quality(birth),
        "birth": {
            "date": birth.date,
            "time": _normalize_time_string(birth.time),
            "timezone": birth.timezone_name,
            "timezone_offset": birth.timezone_offset,
            "location": birth.location_name,
            "latitude": birth.latitude,
            "longitude": birth.longitude,
        },
        "chart_summary": {
            "lagna": lagna_house.sign,
            "lagna_degree": round(float(lagna_house.sign_degrees or 0.0), 4),
            "lagna_lord": sign_lord_name(lagna_house.sign),
            "moon_sign": moon.sign,
            "moon_house_from_lagna": int(moon.house),
            "nakshatra": moon.nakshatra,
            "pada": int(moon.pada),
            "navamsa_lagna": navamsa["lagna"],
            "dasha_balance_at_birth": dasha_balance,
            "current_mahadasha": current_maha["label"],
            "current_antardasha": current_antara["label"],
        },
        "planets": planets,
        "dashas": [current_maha, next_maha, current_antara, next_antara],
        "vargas": {"navamsa": navamsa},
        "engine_config": {
            "ayanamsa_mode": raw_chart.ayanamsa.name,
            "ayanamsa_value": round(float(raw_chart.ayanamsa.value), 6),
            "dasha_reference_policy": "recomputed_from_all_periods_using_reference_date",
        },
        "source_engine": "jyotishganit",
    }


def _extract_navamsa_summary(divisional_chart: Any) -> dict[str, str]:
    if divisional_chart is None:
        return {
            "lagna": "Unknown",
            "venus_sign": "Unknown",
            "jupiter_sign": "Unknown",
            "ketu_sign": "Unknown",
        }

    return {
        "lagna": divisional_chart.ascendant.sign,
        "venus_sign": _find_divisional_planet_sign(divisional_chart, "Venus"),
        "jupiter_sign": _find_divisional_planet_sign(divisional_chart, "Jupiter"),
        "ketu_sign": _find_divisional_planet_sign(divisional_chart, "Ketu"),
    }


def _find_divisional_planet_sign(divisional_chart: Any, planet_name: str) -> str:
    for house in divisional_chart.houses:
        for occupant in house.occupants:
            if occupant.celestial_body == planet_name:
                return occupant.sign
    return "Unknown"


def _normalize_balance(balance: dict[str, float]) -> dict[str, Any]:
    if not balance:
        return {"years": 0, "months": 0, "days": 0}
    lord, remaining_years = next(iter(balance.items()))
    whole_years = int(remaining_years)
    remaining_months_raw = max(0.0, (remaining_years - whole_years) * 12.0)
    months = int(remaining_months_raw)
    days = int(round((remaining_months_raw - months) * 30.0))
    return {
        "lord": lord,
        "years": whole_years,
        "months": months,
        "days": days,
        "remaining_years": round(float(remaining_years), 4),
    }


def _flatten_mahadashas(all_periods: dict[str, Any]) -> list[tuple[list[str], dict[str, Any]]]:
    mahadashas = all_periods.get("mahadashas", {})
    return [([lord], data) for lord, data in mahadashas.items()]


def _flatten_antardashas(all_periods: dict[str, Any]) -> list[tuple[list[str], dict[str, Any]]]:
    flattened: list[tuple[list[str], dict[str, Any]]] = []
    for maha_lord, maha_data in all_periods.get("mahadashas", {}).items():
        for antara_lord, antara_data in maha_data.get("antardashas", {}).items():
            flattened.append(([maha_lord, antara_lord], antara_data))
    return flattened


def _extract_current_and_next_dasha_periods(
    periods: list[tuple[list[str], dict[str, Any]]],
    reference_date: date,
    timezone_offset: float,
    level: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not periods:
        empty = {
            "level": level,
            "lords": [],
            "label": "Unknown",
            "start": None,
            "start_date": None,
            "end": None,
            "end_date": None,
            "duration_years": None,
            "status": "current",
        }
        return empty, dict(empty, status="next")

    current_index = 0
    for index, (_, data) in enumerate(periods):
        start_date = data["start"].date()
        if start_date <= reference_date:
            current_index = index
        else:
            break

    current = _serialize_dasha_period(periods, current_index, timezone_offset, level, "current")
    next_period = _serialize_dasha_period(
        periods,
        min(current_index + 1, len(periods) - 1),
        timezone_offset,
        level,
        "next",
    )
    return current, next_period


def _serialize_dasha_period(
    periods: list[tuple[list[str], dict[str, Any]]],
    index: int,
    timezone_offset: float,
    level: str,
    status: str,
) -> dict[str, Any]:
    lords, data = periods[index]
    start = data.get("start")
    end = data.get("end")
    duration_years = None
    if start is not None and end is not None:
        duration_years = round((end - start).total_seconds() / (365.2425 * 24 * 3600), 4)

    return {
        "level": level,
        "lords": lords,
        "label": " / ".join(lords),
        "start": _datetime_to_iso(start, timezone_offset),
        "start_date": start.date().isoformat() if start else None,
        "end": _datetime_to_iso(end, timezone_offset),
        "end_date": end.date().isoformat() if end else None,
        "duration_years": duration_years,
        "status": status,
    }


def _datetime_to_iso(value: datetime | None, timezone_offset: float) -> str | None:
    if value is None:
        return None
    offset_hours = int(timezone_offset)
    offset_minutes = int(round(abs(timezone_offset - offset_hours) * 60))
    offset = f"{offset_hours:+03d}:{offset_minutes:02d}"
    return value.strftime("%Y-%m-%dT%H:%M:%S") + offset
