from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import io
from typing import Any
from contextlib import redirect_stdout
import swisseph as swe

with redirect_stdout(io.StringIO()):
    from jhora import const, utils
    from jhora.horoscope.chart import charts
    from jhora.horoscope.dhasa.graha import vimsottari
    from jhora.panchanga import drik

SIGN_NAMES = const.rasi_names_en
PLANET_NAMES = {
    0: "Sun",
    1: "Moon",
    2: "Mars",
    3: "Mercury",
    4: "Jupiter",
    5: "Venus",
    6: "Saturn",
    7: "Rahu",
    8: "Ketu",
}
PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
NAKSHATRA_NAMES = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]
SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
HOUSE_TOPICS = {
    1: "身份、身体与人生主轴",
    2: "财富、家庭资源与表达",
    3: "行动力、手足与执行",
    4: "家宅、母缘与内在安全感",
    5: "创造、子女与心智输出",
    6: "工作压力、债务与竞争",
    7: "婚姻、伴侣与合作",
    8: "突变、共享资源与深层转化",
    9: "信念、师承与远行",
    10: "事业、职责与社会角色",
    11: "收入、网络与结果兑现",
    12: "迁移、隐退、睡眠与灵性",
}
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}


@dataclass(frozen=True)
class BirthData:
    date: str
    time: str
    location_name: str
    latitude: float
    longitude: float
    timezone_offset: float
    timezone_name: str = "UTC"


@dataclass(frozen=True)
class PyJHoraConfig:
    ayanamsa_mode: str = "LAHIRI"
    ephe_path: str = "."


def generate_chart(
    birth: BirthData,
    reference_date: date | None = None,
    config: PyJHoraConfig | None = None,
) -> dict[str, Any]:
    config = config or PyJHoraConfig()
    parsed_birth = _parse_birth_datetime(birth.date, birth.time)
    place = drik.Place(
        birth.location_name,
        float(birth.latitude),
        float(birth.longitude),
        float(birth.timezone_offset),
    )
    jd = utils.julian_day_number(
        drik.Date(parsed_birth.year, parsed_birth.month, parsed_birth.day),
        (parsed_birth.hour, parsed_birth.minute, parsed_birth.second),
    )
    _configure_pyjhora_runtime(config)
    ayanamsa_value = float(drik.get_ayanamsa_value(jd))

    rasi_positions = _parse_positions(charts.rasi_chart(jd, place))
    navamsa_positions = _parse_positions(charts.divisional_chart(jd, place, divisional_chart_factor=9))
    lagna_sign_index = rasi_positions["Lagna"]["sign_index"]

    planets = []
    for name in PLANET_ORDER:
        data = rasi_positions[name]
        planets.append(
            {
                "name": name,
                "sign": SIGN_NAMES[data["sign_index"]],
                "sign_index": data["sign_index"],
                "degree": round(data["degree"], 4),
                "house_from_lagna": house_from_lagna(data["sign_index"], lagna_sign_index),
            }
        )

    navamsa = {
        "lagna": SIGN_NAMES[navamsa_positions["Lagna"]["sign_index"]],
        "venus_sign": SIGN_NAMES[navamsa_positions["Venus"]["sign_index"]],
        "jupiter_sign": SIGN_NAMES[navamsa_positions["Jupiter"]["sign_index"]],
        "ketu_sign": SIGN_NAMES[navamsa_positions["Ketu"]["sign_index"]],
    }

    nakshatra_data = drik.nakshatra(jd, place)
    nakshatra_number = int(nakshatra_data[0])
    pada = int(nakshatra_data[1])

    reference = reference_date or date.today()
    dasha_balance, maha_rows = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place, dhasa_level_index=1)
    _, antara_rows = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place, dhasa_level_index=2)
    current_maha, next_maha = _current_and_next_periods(maha_rows, reference, birth.timezone_offset)
    current_antara, next_antara = _current_and_next_periods(antara_rows, reference, birth.timezone_offset)
    all_maha = _attach_all_periods(maha_rows, birth.timezone_offset)
    all_antara = _attach_all_periods(antara_rows, birth.timezone_offset)

    lagna = SIGN_NAMES[lagna_sign_index]
    lagna_lord = sign_lord_name(lagna)
    moon_sign = SIGN_NAMES[rasi_positions["Moon"]["sign_index"]]

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
            "lagna": lagna,
            "lagna_degree": round(rasi_positions["Lagna"]["degree"], 4),
            "lagna_lord": lagna_lord,
            "moon_sign": moon_sign,
            "moon_house_from_lagna": house_from_lagna(rasi_positions["Moon"]["sign_index"], lagna_sign_index),
            "nakshatra": NAKSHATRA_NAMES[nakshatra_number - 1],
            "pada": pada,
            "navamsa_lagna": navamsa["lagna"],
            "dasha_balance_at_birth": {
                "years": int(dasha_balance[0]),
                "months": int(dasha_balance[1]),
                "days": int(dasha_balance[2]),
            },
            "current_mahadasha": current_maha["label"],
            "current_antardasha": current_antara["label"],
        },
        "planets": planets,
        "dashas": [current_maha, next_maha, current_antara, next_antara],
        "dasha_timeline": {
            "mahadasha": all_maha,
            "antardasha": all_antara,
        },
        "vargas": {"navamsa": navamsa},
        "engine_config": {
            "ayanamsa_mode": config.ayanamsa_mode,
            "ayanamsa_value": round(ayanamsa_value, 6),
            "node_mode": "true",
        },
        "source_engine": "pyjhora",
    }


def house_from_lagna(sign_index: int, lagna_sign_index: int) -> int:
    return ((sign_index - lagna_sign_index) % 12) + 1


def sign_lord_name(sign_name: str) -> str:
    return SIGN_LORDS[sign_name]


def house_sign_name(lagna_sign: str, house_number: int) -> str:
    lagna_index = SIGN_NAMES.index(lagna_sign)
    return SIGN_NAMES[(lagna_index + house_number - 1) % 12]


def describe_house(house_number: int) -> str:
    return HOUSE_TOPICS[house_number]


def _configure_pyjhora_runtime(config: PyJHoraConfig) -> None:
    swe.set_ephe_path(config.ephe_path)
    drik.set_planet_list(set_rahu_ketu_as_true_nodes=True, include_western_planets=False)
    drik.set_ayanamsa_mode(config.ayanamsa_mode)


def _build_input_quality(birth: BirthData) -> dict[str, Any]:
    warnings: list[str] = []
    if len(birth.time.split(":")) < 3:
        warnings.append("出生时间未提供秒级精度，月份级 timing windows 只作为参考。")
    if birth.timezone_name == "UTC":
        warnings.append("当前使用默认时区名，实际以 timezone_offset 为准。")
    return {
        "birth_time_precision": _infer_time_precision(birth.time),
        "location_precision": "exact",
        "warnings": warnings,
    }


def _infer_time_precision(time_value: str) -> str:
    parts = time_value.split(":")
    if len(parts) >= 2:
        return "minute"
    if len(parts) == 1 and parts[0]:
        return "hour"
    return "day"


def _parse_birth_datetime(date_value: str, time_value: str) -> datetime:
    normalized_time = _normalize_time_string(time_value)
    return datetime.strptime(f"{date_value} {normalized_time}", "%Y-%m-%d %H:%M:%S")


def _normalize_time_string(time_value: str) -> str:
    parts = time_value.split(":")
    if len(parts) == 2:
        return f"{parts[0]}:{parts[1]}:00"
    if len(parts) == 3:
        return time_value
    raise ValueError(f"Unsupported time format: {time_value}")


def _parse_positions(raw_positions: list[list[Any]]) -> dict[str, dict[str, float | int]]:
    parsed: dict[str, dict[str, float | int]] = {}
    for body, placement in raw_positions:
        sign_index, degree = placement
        if body == "L":
            name = "Lagna"
        else:
            planet_id = int(body)
            if planet_id not in PLANET_NAMES:
                continue
            name = PLANET_NAMES[planet_id]
        parsed[name] = {"sign_index": int(sign_index), "degree": float(degree)}
    return parsed


def _current_and_next_periods(
    rows: list[list[Any]],
    reference_date: date,
    timezone_offset: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    parsed_rows = [_serialize_dasha_row(row, timezone_offset) for row in rows]
    reference_value = reference_date.isoformat()

    current_index = 0
    for index, row in enumerate(parsed_rows):
        if row["start_date"] <= reference_value:
            current_index = index
        else:
            break

    current_period = _attach_end(parsed_rows, current_index, "current")
    next_period = _attach_end(parsed_rows, min(current_index + 1, len(parsed_rows) - 1), "next")
    return current_period, next_period


def _attach_all_periods(rows: list[list[Any]], timezone_offset: float) -> list[dict[str, Any]]:
    parsed_rows = [_serialize_dasha_row(row, timezone_offset) for row in rows]
    return [_attach_end(parsed_rows, index, "timeline") for index in range(len(parsed_rows))]


def _serialize_dasha_row(row: list[Any], timezone_offset: float) -> dict[str, Any]:
    lords = [PLANET_NAMES[int(item)] for item in row[0]]
    start = _fractional_gregorian_to_iso(row[1], timezone_offset)
    level = "mahadasha" if len(lords) == 1 else "antardasha"
    return {
        "level": level,
        "lords": lords,
        "label": " / ".join(lords),
        "start": start,
        "start_date": start[:10],
        "duration_years": round(float(row[2]), 4),
    }


def _attach_end(rows: list[dict[str, Any]], index: int, status: str) -> dict[str, Any]:
    row = dict(rows[index])
    row["status"] = status
    if index < len(rows) - 1:
        row["end"] = rows[index + 1]["start"]
        row["end_date"] = rows[index + 1]["start_date"]
    else:
        row["end"] = None
        row["end_date"] = None
    return row


def _fractional_gregorian_to_iso(value: tuple[int, int, int, float], timezone_offset: float) -> str:
    year, month, day, fractional_hour = value
    hour = int(fractional_hour)
    minute_fraction = (fractional_hour - hour) * 60
    minute = int(minute_fraction)
    second = int(round((minute_fraction - minute) * 60))
    if second == 60:
        minute += 1
        second = 0
    if minute == 60:
        hour += 1
        minute = 0
    offset_hours = int(timezone_offset)
    offset_minutes = int(abs(timezone_offset - offset_hours) * 60)
    offset = f"{offset_hours:+03d}:{offset_minutes:02d}"
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}{offset}"
