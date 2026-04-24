from __future__ import annotations

from typing import Any

from .chart_adapter import house_sign_name, sign_lord_name


TRUE_RATINGS = {"true", "准"}
PARTIAL_RATINGS = {"partial", "half_true", "半准"}
PLANET_ZH = {
    "Sun": "太阳",
    "Moon": "月亮",
    "Mars": "火星",
    "Mercury": "水星",
    "Jupiter": "木星",
    "Venus": "金星",
    "Saturn": "土星",
    "Rahu": "罗喉",
    "Ketu": "计都",
}
HOUSE_ARENAS = {
    1: "自我、身体、个人主导权",
    2: "金钱、家庭资源与表达方式",
    3: "行动、技能、输出与胆识",
    4: "家庭、房产、居住与内在安全感",
    5: "创造、恋爱、子女与心智表达",
    6: "工作、服务、竞争、责任与问题处理",
    7: "伴侣、合作、客户与公众关系",
    8: "危机、共享资源、心理深处与重组",
    9: "信念、导师、父辈、远行与命运感",
    10: "事业、名声、职责与社会位置",
    11: "收益、平台、社群与结果兑现",
    12: "迁移、睡眠、损耗、隐退与灵修",
}


def build_guidance_profile(chart: dict[str, Any], feedback_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    feedback_profile = feedback_profile or {}
    validated_anchors = _validated_anchors(feedback_profile)
    current_maha = chart["chart_summary"]["current_mahadasha"]
    current_antara = chart["chart_summary"]["current_antardasha"]
    maha_lord = current_maha.split(" / ")[0]
    antara_lord = current_antara.split(" / ")[-1]

    guidance_items = _dynamic_guidance_items(chart, maha_lord, antara_lord)

    return {
        "source": "feedback_calibrated_guidance_v1",
        "current_dasha": current_maha,
        "current_antardasha": current_antara,
        "validated_anchors": validated_anchors,
        "guidance_items": guidance_items,
        "precision_rule": "优先放大使用者已验证为准的主题；半准主题只保留方向，不继续扩写成强结论。",
    }


def _dynamic_guidance_items(chart: dict[str, Any], maha_lord: str, antara_lord: str) -> list[dict[str, Any]]:
    maha_house = _planet_house(chart, maha_lord)
    antara_house = _planet_house(chart, antara_lord)
    dominant_house, dominant_planets = _dominant_house_cluster(chart)
    moon_house = _planet_house(chart, "Moon")
    rahu_house = _planet_house(chart, "Rahu")
    ketu_house = _planet_house(chart, "Ketu")
    tenth_lord = _house_lord(chart, 10)
    tenth_lord_house = _planet_house(chart, tenth_lord)
    seventh_lord = _house_lord(chart, 7)
    seventh_lord_house = _planet_house(chart, seventh_lord)

    return [
        {
            "priority": 1,
            "title": f"先处理{PLANET_ZH[maha_lord]}大运的第 {maha_house} 宫主课题",
            "timeframe": _current_antara_window(chart) or "当前分运",
            "why": (
                f"当前主运星{PLANET_ZH[maha_lord]}落第 {maha_house} 宫，主轴不是泛泛的成长，"
                f"而是{HOUSE_ARENAS[maha_house]}。分运星{PLANET_ZH[antara_lord]}落第 {antara_house} 宫，"
                f"会把{HOUSE_ARENAS[antara_house]}推到更具体的事件层。"
            ),
            "practice": _house_practice(maha_house, antara_house),
            "avoid": _house_avoid(maha_house),
        },
        {
            "priority": 2,
            "title": f"把第 {dominant_house} 宫的高密度能量做成主产品",
            "timeframe": "未来 12-24 个月持续观察",
            "why": (
                f"第 {dominant_house} 宫同时聚集{_planet_list_zh(dominant_planets)}，"
                f"说明{HOUSE_ARENAS[dominant_house]}不是边缘主题，而是整张盘最容易出事件、出机会、也出压力的地方。"
            ),
            "practice": _house_practice(dominant_house, dominant_house),
            "avoid": _house_avoid(dominant_house),
        },
        {
            "priority": 3,
            "title": f"按月亮第 {moon_house} 宫管理情绪和身体反应",
            "timeframe": "每月复盘，尤其在压力、合作或迁移变化时",
            "why": (
                f"月亮落第 {moon_house} 宫，安全感会通过{HOUSE_ARENAS[moon_house]}表现出来。"
                f"如果这一层没有被看见，报告很容易只写外部事件，却漏掉真正驱动选择的内在反应。"
            ),
            "practice": _moon_practice(moon_house),
            "avoid": _moon_avoid(moon_house),
        },
        {
            "priority": 4,
            "title": f"分清罗喉第 {rahu_house} 宫的扩张和计都第 {ketu_house} 宫的抽离",
            "timeframe": "每次重大选择前核验",
            "why": (
                f"罗喉在第 {rahu_house} 宫会放大{HOUSE_ARENAS[rahu_house]}，"
                f"计都在第 {ketu_house} 宫会让{HOUSE_ARENAS[ketu_house]}带有抽离、断裂或内化色彩。"
            ),
            "practice": _node_practice(rahu_house, ketu_house),
            "avoid": "避免把罗喉的强欲望当成使命，也避免把计都的抽离感误判成彻底不重要。",
        },
        {
            "priority": 5,
            "title": "把事业线和关系线分开核验，不再套通用模板",
            "timeframe": "作为后续反馈校准项",
            "why": (
                f"第 10 宫主{PLANET_ZH[tenth_lord]}落第 {tenth_lord_house} 宫，"
                f"第 7 宫主{PLANET_ZH[seventh_lord]}落第 {seventh_lord_house} 宫。"
                "这两条线共同决定此人的社会角色和关系模式，不能只用“长期积累、稳定交付”这种通用句子盖过去。"
            ),
            "practice": (
                f"分别记录：职业是否通过{HOUSE_ARENAS[tenth_lord_house]}打开，"
                f"关系是否通过{HOUSE_ARENAS[seventh_lord_house]}触发。"
            ),
            "avoid": "避免把事业、财富、伴侣、家庭全部写成同一种责任叙事。",
        },
    ]


def _planet_house(chart: dict[str, Any], planet_name: str) -> int:
    for planet in chart["planets"]:
        if planet["name"] == planet_name:
            return int(planet["house_from_lagna"])
    raise KeyError(planet_name)


def _house_lord(chart: dict[str, Any], house_number: int) -> str:
    sign = house_sign_name(chart["chart_summary"]["lagna"], house_number)
    return sign_lord_name(sign)


def _dominant_house_cluster(chart: dict[str, Any]) -> tuple[int, list[str]]:
    counts: dict[int, list[str]] = {}
    for planet in chart["planets"]:
        house = int(planet["house_from_lagna"])
        counts.setdefault(house, []).append(str(planet["name"]))
    return max(counts.items(), key=lambda item: (len(item[1]), item[0]))


def _planet_list_zh(planets: list[str]) -> str:
    return "、".join(PLANET_ZH[p] for p in planets)


def _house_practice(primary_house: int, secondary_house: int) -> str:
    if 10 in {primary_house, secondary_house}:
        return "把角色、作品、交付标准和对外身份写清楚，让别人知道你到底承担什么、交付什么、拒绝什么。"
    if 7 in {primary_house, secondary_house}:
        return "所有合作和亲密关系都要写清楚边界、责任、节奏和复盘机制，先定结构再谈感受。"
    if 1 in {primary_house, secondary_house}:
        return "把身体状态、情绪反应和个人判断权放进日程，而不是只迎合外部要求。"
    if 4 in {primary_house, secondary_house}:
        return "先稳定居住空间、家庭边界和睡眠节律，再谈长期选择。"
    if 8 in {primary_house, secondary_house}:
        return "把共享资源、信任、风险、心理压力和边界全部显性化，不让暗流长期积压。"
    if 12 in {primary_house, secondary_house}:
        return "用固定的独处、睡眠、运动或修行节律消化损耗，不用突然消失来解决问题。"
    return "把这一宫对应的现实领域拆成可观察、可复盘、可调整的行动项。"


def _house_avoid(house: int) -> str:
    if house == 10:
        return "避免只做幕后消耗，却不建立清楚的公开角色、作品和议价权。"
    if house == 7:
        return "避免用人情、暧昧或含糊承诺替代真实契约和边界。"
    if house == 1:
        return "避免把身体反应和第一直觉长期压下去，只按外界期待行动。"
    if house == 4:
        return "避免把家庭责任、居住压力和内在不安全部硬扛成沉默。"
    if house == 8:
        return "避免在钱、信任、控制和风险上保持模糊，最后被危机倒逼重组。"
    if house == 12:
        return "避免用逃离、熬夜、情绪性开销或突然断联来处理损耗。"
    return "避免把这一宫主题说成泛泛的性格形容词，要落到具体行为。"


def _moon_practice(house: int) -> str:
    if house == 1:
        return "情绪一上来先看身体：睡眠、脸色、胃口、冲动、表达速度，这些就是月亮在第 1 宫的真实仪表盘。"
    if house == 8:
        return "给危机感和不安全感留出口：心理复盘、财务透明、关系边界和深度谈话都要定期做。"
    if house == 10:
        return "公开角色变化会直接影响情绪，重大工作决定后要安排恢复和复盘。"
    if house == 4:
        return "家宅、睡眠和私人空间就是情绪核心，不要把它们当小事。"
    return f"用{HOUSE_ARENAS[house]}作为情绪观察入口，记录触发点和身体反应。"


def _moon_avoid(house: int) -> str:
    if house == 1:
        return "避免一边强行表现没事，一边让身体替你承受所有压力。"
    if house == 8:
        return "避免把深层不安全感伪装成理性判断或突然切断。"
    if house == 10:
        return "避免让外界评价完全决定情绪稳定。"
    return "避免只讲事件，不记录事件背后的情绪和身体代价。"


def _node_practice(rahu_house: int, ketu_house: int) -> str:
    if rahu_house == 10 and ketu_house == 4:
        return "向外建立事业角色时，必须同步修复家宅、睡眠和内在根基；否则越公开越空心。"
    if rahu_house == 3 and ketu_house == 9:
        return "把远大信念压缩成稳定输出：写、说、练、试错，比一直换体系更重要。"
    return f"罗喉第 {rahu_house} 宫负责扩张，计都第 {ketu_house} 宫负责清理旧身份；两个方向要同时看。"


def _validated_anchors(feedback_profile: dict[str, Any]) -> list[dict[str, str]]:
    anchors: list[dict[str, str]] = []
    for item in feedback_profile.get("checks", []):
        rating = str(item.get("rating", ""))
        if rating not in TRUE_RATINGS and rating not in PARTIAL_RATINGS:
            continue
        anchors.append(
            {
                "id": str(item.get("id", "")),
                "rating": rating,
                "claim": str(item.get("claim", "")),
                "user_note": str(item.get("user_note", "")),
            }
        )
    return anchors


def _current_antara_window(chart: dict[str, Any]) -> str | None:
    for dasha in chart.get("dashas", []):
        if dasha.get("status") == "current" and dasha.get("level") == "antardasha":
            return f"{dasha['start_date']} - {dasha['end_date']}"
    return None
