from __future__ import annotations

from datetime import date
from typing import Any

from .chart_adapter import (
    DUSTHANA_HOUSES,
    KENDRA_HOUSES,
    PLANET_ORDER,
    TRIKONA_HOUSES,
    describe_house,
    house_sign_name,
    sign_lord_name,
)
from .guidance_engine import build_guidance_profile

SIGN_ZH = {
    "Aries": "白羊",
    "Taurus": "金牛",
    "Gemini": "双子",
    "Cancer": "巨蟹",
    "Leo": "狮子",
    "Virgo": "处女",
    "Libra": "天秤",
    "Scorpio": "天蝎",
    "Sagittarius": "射手",
    "Capricorn": "摩羯",
    "Aquarius": "水瓶",
    "Pisces": "双鱼",
}
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
THEME_ZH = {
    "career": "事业版",
    "wealth": "财富版",
    "spirituality": "灵性版",
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
PLANET_ESSENCE = {
    "Sun": "权威、角色感、判断权与被看见的方式",
    "Moon": "情绪体、内在安全感与习惯性反应",
    "Mars": "行动力、切断力、怒气与突破方式",
    "Mercury": "认知、沟通、交易、分析与连接能力",
    "Jupiter": "信念、成长、资源放大与贵人线",
    "Venus": "价值感、关系、审美、舒适度与交换关系",
    "Saturn": "责任、延迟、结构、长期主义与现实压力",
    "Rahu": "放大、欲望、越界、野心与非传统追求",
    "Ketu": "抽离、旧业、内化能力与割舍",
}
EXALTATION_SIGNS = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
}
DEBILITATION_SIGNS = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
}
UPACHAYA_HOUSES = {3, 6, 10, 11}


def render_premium_markdown_report(
    *,
    name: str,
    birth: dict[str, Any],
    reference_date: date,
    preset_title: str,
    preset_subtitle: str,
    chart: dict[str, Any],
    reading: dict[str, Any],
    quality_score: dict[str, Any],
    accuracy_profile: dict[str, Any],
    cross_validation: dict[str, Any],
    feedback_profile: dict[str, Any] | None = None,
) -> str:
    lines: list[str] = []
    guidance_profile = build_guidance_profile(chart, feedback_profile)
    lines.append(f"# {name}｜{preset_title}纳迪式阅读")
    lines.append("")
    lines.append(preset_subtitle)
    lines.append("")
    lines.append("## 先说结论")
    for item in _executive_summary(chart, reading):
        lines.append(f"- {item}")
    lines.append("")
    if guidance_profile["validated_anchors"]:
        lines.extend(_section_verified_anchors(guidance_profile))
    lines.extend(_section_guidance_priorities(guidance_profile))
    lines.append("## 命盘骨架")
    for item in _chart_skeleton(chart):
        lines.append(f"- {item}")
    lines.append("")

    if 1 in reading.get("requested_chapters", []):
        lines.extend(_section_identity(chart))
    if 4 in reading.get("requested_chapters", []):
        lines.extend(_section_home(chart))
    if 7 in reading.get("requested_chapters", []):
        lines.extend(_section_relationship(chart))
    if 10 in reading.get("requested_chapters", []):
        lines.extend(_section_career(chart))
    if 12 in reading.get("requested_chapters", []):
        lines.extend(_section_spirituality(chart))

    lines.extend(_section_kandam_claims(chart, reading))

    theme_ids = set(reading.get("requested_theme_packs", []))
    if "career" in theme_ids or "wealth" in theme_ids:
        lines.extend(_section_career_wealth_synthesis(chart, theme_ids))
    if "spirituality" in theme_ids:
        lines.extend(_section_spiritual_tone(chart))

    lines.extend(_section_timing(chart))
    lines.extend(_section_past_present_future(chart))
    lines.extend(_section_validation(reading))
    lines.extend(
        _section_appendix(
            birth=birth,
            reference_date=reference_date,
            chart=chart,
            quality_score=quality_score,
            accuracy_profile=accuracy_profile,
            cross_validation=cross_validation,
            missing_capabilities=reading.get("missing_capabilities", []),
        )
    )
    return "\n".join(lines)


def _executive_summary(chart: dict[str, Any], reading: dict[str, Any]) -> list[str]:
    lagna_lord = chart["chart_summary"]["lagna_lord"]
    lagna_lord_house = _planet_house(chart, lagna_lord)
    moon_house = _planet_house(chart, "Moon")
    current_maha = _current_maha_lord(chart)
    current_maha_house = _planet_house(chart, current_maha)
    first = (
        f"这张盘不是松散漂浮型，而是典型的“被现实课题推着成长”的盘。"
        f"人生主线会反复被 {HOUSE_ARENAS[lagna_lord_house]} 拉到台前。"
    )
    second = (
        f"内在层面，月亮落在第 {moon_house} 宫，说明情绪和安全感并不走表面轻松路线，"
        f"真正改变你的往往是危机、重组、深层关系或价值观翻修。"
    )
    third = _current_period_one_liner(chart, current_maha, current_maha_house)
    return [first, second, third]


def _chart_skeleton(chart: dict[str, Any]) -> list[str]:
    skeleton_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]
    items = [
        f"上升：{_sign_zh(chart['chart_summary']['lagna'])}上升，命主星为{PLANET_ZH[chart['chart_summary']['lagna_lord']]}。"
    ]
    for planet in skeleton_planets:
        items.append(_placement_sentence(chart, planet))
    items.append(
        f"月宿：{chart['chart_summary']['nakshatra']} 第 {chart['chart_summary']['pada']} pada；"
        f"Navamsa 上升落在{_sign_zh(chart['chart_summary']['navamsa_lagna'])}。"
    )
    return items


def _section_verified_anchors(guidance_profile: dict[str, Any]) -> list[str]:
    lines = [
        "## 已验证锚点",
        "",
        "下面这些不是重新猜，是根据你已经反馈过的 `准 / 半准` 收敛出来的判断边界：",
    ]
    for anchor in guidance_profile["validated_anchors"]:
        lines.append(f"- `{anchor['rating']}`：{anchor['claim']}")
        if anchor["user_note"]:
            lines.append(f"  你的反馈：{anchor['user_note']}")
    lines.append("")
    return lines


def _section_guidance_priorities(guidance_profile: dict[str, Any]) -> list[str]:
    lines = [
        "## 指导优先级",
        "",
        "这部分只放当前最该执行的建议，不扩写成泛泛的人生建议。",
    ]
    for item in guidance_profile["guidance_items"]:
        lines.append(f"### {item['priority']}. {item['title']}")
        lines.append(f"- 时间：{item['timeframe']}")
        lines.append(f"- 为什么：{item['why']}")
        lines.append(f"- 做法：{item['practice']}")
        lines.append(f"- 避免：{item['avoid']}")
    lines.append("")
    return lines


def _section_kandam_claims(chart: dict[str, Any], reading: dict[str, Any]) -> list[str]:
    kandams = sorted(reading.get("kandam_reading", []), key=lambda item: item["kandam"])
    if len(kandams) <= 5:
        return []
    lines = [
        "## 16 Kandam 完整正文",
        "",
        "这一节按公开 Nadi 阅读常见的 Kandam 结构逐章展开。前半部分写成可直接阅读的正文，最后保留证据链。标为 `requires_corpus` 的内容，代表需要真实叶片语料、传承文本或人工校勘后才能升级为强结论。",
    ]
    for item in kandams:
        lines.extend(_render_kandam_longform(chart, item))
    lines.append("")
    return lines


def _render_kandam_longform(chart: dict[str, Any], item: dict[str, Any]) -> list[str]:
    kandam = int(item["kandam"])
    chapter = _kandam_longform_content(chart, kandam)
    lines = [
        f"### Kandam {kandam}｜{item['title']}",
        "",
        f"**主判断**：{item['summary']}",
        "",
    ]
    lines.extend(chapter["paragraphs"])
    lines.extend(["", "**现实中更可能这样表现**："])
    for point in chapter["manifestations"]:
        lines.append(f"- {point}")
    lines.extend(["", "**这一章给你的指导**："])
    for point in chapter["guidance"]:
        lines.append(f"- {point}")
    lines.extend(["", "**证据链**："])
    for claim in item.get("claims", []):
        lines.append(f"- `{claim['evidence_tag']}`：{claim['text']}")
    if chapter.get("boundary"):
        lines.extend(["", f"**边界**：{chapter['boundary']}"])
    lines.append("")
    return lines


def _kandam_longform_content(chart: dict[str, Any], kandam: int) -> dict[str, Any]:
    current_maha = _current_dasha(chart, "current", level=1)
    current_antara = _current_dasha(chart, "current", level=2)
    next_maha = _current_dasha(chart, "next", level=1)
    current_lord = current_maha["lords"][0]
    lagna = chart["chart_summary"]["lagna"]
    lagna_lord = chart["chart_summary"]["lagna_lord"]
    lagna_lord_house = _planet_house(chart, lagna_lord)
    moon_house = _planet_house(chart, "Moon")
    rahu_house = _planet_house(chart, "Rahu")
    ketu_house = _planet_house(chart, "Ketu")

    if kandam == 1:
        return {
            "paragraphs": [
                (
                    f"你这张盘的第一章不是“安静地做自己”，而是“通过他人、合作、公众关系和现实绑定来认识自己”。"
                    f"{_sign_zh(lagna)}上升给你一种要主导人生、要形成个人判断的底色，但命主星{PLANET_ZH[lagna_lord]}落第 {lagna_lord_house} 宫，"
                    "说明你的身份感不是单独长出来的，而是在关系、客户、合作、外部评价中被不断磨出来的。"
                ),
                (
                    f"月亮落第 {moon_house} 宫，让你的内在比外表深很多。你不是没有情绪，而是很多感受会先被压到更深处，"
                    "等到关系、金钱、信任或安全感被触发时，才会以重组、抽离、换方向的方式冒出来。"
                    f"罗喉第 {rahu_house} 宫、计都第 {ketu_house} 宫，也说明你不是完全沿着父辈或传统路线走的人。"
                ),
            ],
            "manifestations": [
                "别人容易看到你的能力、表达或承担，但不一定看到你内在的复杂度。",
                "人生重要转折多半绕不开合作、关系、客户、公众角色或外部评价。",
                "你真正成熟，不是变得更会讨好，而是在关系里保住判断权、边界和角色中心。",
            ],
            "guidance": [
                "把“我是谁”落实成稳定角色：你提供什么价值、对谁负责、边界在哪里。",
                "不要把关系里的压力都理解成失败；这张盘本来就是在关系场里练主导权。",
                "每次重大转折后都做复盘：这次到底是别人改变了你，还是你通过别人看清了自己。",
            ],
        }

    if kandam == 2:
        second_lord = _house_lord(chart, 2)
        second_house = _planet_house(chart, second_lord)
        mercury_house = _planet_house(chart, "Mercury")
        jupiter_house = _planet_house(chart, "Jupiter")
        return {
            "paragraphs": [
                (
                    f"第二章看钱，但你的钱不是孤立的钱。第 2 宫主{PLANET_ZH[second_lord]}落第 {second_house} 宫，"
                    f"水星本身也在第 {mercury_house} 宫发力，木星落第 {jupiter_house} 宫，说明财富要通过表达、技能、秩序、信誉和长期服务慢慢做厚。"
                ),
                (
                    "这不是一张适合只靠短线刺激、冲动交易或单次机会翻身的财富盘。更像是你越能把能力讲清楚、流程化、产品化、稳定交付，"
                    "收入越容易稳定。家庭资源和教育背景会给你一部分底层影响，但真正决定后续财富质量的，是你能不能把认知变成可复用的价值。"
                ),
            ],
            "manifestations": [
                "钱和工作压力、客户需求、交付质量经常绑在一起，不太能完全轻松地赚钱。",
                "表达能力、写作、咨询、整理复杂信息、方法论输出，会直接影响收入。",
                "家庭和财务秩序需要分开看，不能把所有支持或压力都混成一个家庭主题。",
            ],
            "guidance": [
                "把收入拆成三层：稳定现金流、可复用产品、长期资源池。",
                "所有合作都要明确报价、交付边界、修改次数和复盘周期。",
                "少追“暴利机会”，多做能复购、能沉淀口碑、能被长期信任的收入结构。",
            ],
        }

    if kandam == 3:
        third_lord = _house_lord(chart, 3)
        third_house = _planet_house(chart, third_lord)
        mars_house = _planet_house(chart, "Mars")
        return {
            "paragraphs": [
                (
                    f"第三章讲兄弟姐妹、胆识、技能和主动开路。第 3 宫主{PLANET_ZH[third_lord]}落第 {third_house} 宫，"
                    f"罗喉又在第 {rahu_house} 宫，说明你的人生不是等机会来，而是要靠输出、表达、自学、内容、短途试错和主动连接来打开局面。"
                ),
                (
                    f"火星落第 {mars_house} 宫，让行动力带有隐忍、耗损和突然切断的色彩。你不是没胆识，而是容易先积压，"
                    "然后在某个节点突然决定离开、重启或自己干。这一章的关键，是把冲动变成训练，把表达变成资产。"
                ),
            ],
            "manifestations": [
                "你适合靠写、说、做内容、做方法论、做连接来开路。",
                "同辈、小团队、兄弟姐妹或朋友关系中，既可能有帮助，也可能有竞争和压力。",
                "越是被现实逼着输出，越能练出真正可迁移的技能。",
            ],
            "guidance": [
                "建立固定输出节奏：每周固定文章、案例、复盘或产品说明。",
                "不要只在情绪强烈时行动，要把行动变成训练计划。",
                "把短期试错记录下来，未来它会变成你的方法论和商业资产。",
            ],
        }

    if kandam == 4:
        fourth_lord = _house_lord(chart, 4)
        fourth_house = _planet_house(chart, fourth_lord)
        jupiter_house = _planet_house(chart, "Jupiter")
        return {
            "paragraphs": [
                (
                    f"第四章看母亲、家宅、房产、居住环境和内在稳定。第 4 宫主{PLANET_ZH[fourth_lord]}落第 {fourth_house} 宫，"
                    f"木星落第 {jupiter_house} 宫，说明家不是一个简单背景，而是会长期影响你情绪、睡眠、选择和根基感的主题。"
                ),
                (
                    "结合你的进一步反馈，这里要拆成三层：家庭财务的主要来源是父亲的工资收入；资金管理权在母亲手里；"
                    "直接给你钱的人通常是母亲，但她会和父亲商量。这说明第 4 宫母亲线不能只写成情绪责任，"
                    "也不能把财务支持简单归到父亲或母亲某一方，而是“父亲供给、母亲掌管、父母协商”。"
                ),
            ],
            "manifestations": [
                "家宅主题容易和迁移、距离、情绪责任、睡眠或隐性负担连在一起。",
                "你需要自己的私人空间，否则判断力和情绪会被家庭场域拖住。",
                "房子、居住城市、工作空间的变化，常常不只是生活变化，也代表内在重组。",
            ],
            "guidance": [
                "把父亲收入来源、母亲资金管理、父母共同决策、你自己的情绪责任分开记录。",
                "固定整理居住空间和睡眠节律，这对你不是小事，而是稳定内在的根基。",
                "不要长期默认自己承担家庭隐性责任，责任要说清楚、分清楚。",
            ],
        }

    if kandam == 5:
        fifth_lord = _house_lord(chart, 5)
        fifth_house = _planet_house(chart, fifth_lord)
        venus_house = _planet_house(chart, "Venus")
        return {
            "paragraphs": [
                (
                    f"第五章看子女、创造力、恋爱、学习成果和传承。第 5 宫主{PLANET_ZH[fifth_lord]}落第 {fifth_house} 宫，"
                    f"金星落第 {venus_house} 宫，说明你的创造力不是纯玩乐型，而是要通过稳定环境、长期培养和现实打磨才能成形。"
                ),
                (
                    "对你来说，“创造”不只是灵感，而是把复杂体验转成可以教、可以写、可以卖、可以传给别人的东西。"
                    "如果以后涉及子女或传承，也不是只看有没有，而是看你能不能提供稳定结构、情绪安全和价值观传递。"
                ),
            ],
            "manifestations": [
                "作品、内容、课程、方法论、咨询体系都属于你的第 5 章出口。",
                "恋爱和创造力容易被现实责任影响，不能只靠感觉维持。",
                "你更适合慢慢培养一个系统，而不是频繁追新鲜主题。",
            ],
            "guidance": [
                "把灵感写成框架，把经验写成案例，把认知写成可复用产品。",
                "涉及恋爱或子女议题时，先看稳定性和长期责任，而不是只看情绪浓度。",
                "每季度保留一个创造项目，不求多，但要求能沉淀。",
            ],
        }

    if kandam == 6:
        sixth_lord = _house_lord(chart, 6)
        sixth_house = _planet_house(chart, sixth_lord)
        saturn_house = _planet_house(chart, "Saturn")
        return {
            "paragraphs": [
                (
                    f"第六章看疾病、债务、敌人、竞争、诉讼和日常阻碍。第 6 宫主{PLANET_ZH[sixth_lord]}落第 {sixth_house} 宫，"
                    f"而这颗土星本身也落在第 {saturn_house} 宫，说明你的问题处理能力很强，但它不是天生轻松来的，是在压力、规则、合作和长期责任里练出来的。"
                ),
                (
                    "这章不能简单理解成坏事。第 6 宫强的人，往往能在复杂问题、客户需求、竞争、系统搭建、流程优化里练出专业度。"
                    "但代价是身体节律、睡眠、慢性压力和边界管理必须认真做，否则能力越强，消耗也越大。"
                ),
            ],
            "manifestations": [
                "越是复杂、麻烦、需要长期服务的事，越可能逼出你的专业能力。",
                "合作中的分工不清、收费不清、责任不清，会直接变成消耗。",
                "压力容易先进入睡眠、身体紧张、消化、炎症或疲劳感。",
            ],
            "guidance": [
                "建立工作 SOP：需求确认、报价、交付、验收、复盘全部标准化。",
                "债务、合同、诉讼和健康问题都不要凭感觉处理，要用专业意见和书面记录。",
                "每天固定一个身体恢复动作：睡眠、拉伸、步行、呼吸或力量训练。",
            ],
            "boundary": "这一章可以提示压力和健康管理主题，但不能替代医生、律师或财务顾问。",
        }

    if kandam == 7:
        seventh_lord = _house_lord(chart, 7)
        seventh_house = _planet_house(chart, seventh_lord)
        venus_house = _planet_house(chart, "Venus")
        navamsa_venus = chart["vargas"]["navamsa"]["venus_sign"]
        return {
            "paragraphs": [
                (
                    f"第七章看婚姻、伴侣、合作和客户关系。第 7 宫主{PLANET_ZH[seventh_lord]}落第 {seventh_house} 宫，"
                    f"金星落第 {venus_house} 宫，Navamsa 金星在{_sign_zh(navamsa_venus)}，说明关系对你不是装饰，而是人生主线之一。"
                ),
                (
                    "你已经反馈过：很难接受纯轻松型伴侣是准的，但是否会被高压力的人吸引不能下强结论。"
                    "所以更准确的表达是：你要的不是沉重，而是深度、可靠、能谈现实、能共同复盘的人。"
                ),
            ],
            "manifestations": [
                "你不会满足于只开心、只暧昧、只轻松的关系。",
                "关系会牵动你的工作节奏、价值感、责任感和人生秩序。",
                "合作对象、客户、伴侣的质量，会直接影响你的事业和内在稳定。",
            ],
            "guidance": [
                "筛选关系时看三件事：能不能谈现实，能不能守边界，能不能共同成长。",
                "不要把沉重感误判为深度，也不要把轻松感一概判成不可靠。",
                "重要关系要建立复盘机制，而不是让情绪长期积压。",
            ],
        }

    if kandam == 8:
        eighth_lord = _house_lord(chart, 8)
        eighth_house = _planet_house(chart, eighth_lord)
        saturn_house = _planet_house(chart, "Saturn")
        return {
            "paragraphs": [
                (
                    f"第八章看寿元、风险、事故、共享资源、危机和深层转化。第 8 宫主{PLANET_ZH[eighth_lord]}落第 {eighth_house} 宫，"
                    f"月亮也在第 {moon_house} 宫，所以这章对你非常重要：危机不只是外部事件，也会进入心理、安全感和身体节律。"
                ),
                (
                    f"土星第 {saturn_house} 宫说明长期责任和关系结构会成为风险管理的一部分。你真正要防的不是某个神秘灾难，"
                    "而是长期压力无人处理、关系边界不清、共享资源混乱、睡眠情绪被不断透支。"
                ),
            ],
            "manifestations": [
                "人生中容易有几次明显重组：关系、财务、居住、信念或身份突然需要翻修。",
                "你对心理学、玄学、生死议题、深层疗愈会比一般人更敏感。",
                "共享金钱、信任、合同和隐性控制，是这章最需要小心的现实入口。",
            ],
            "guidance": [
                "所有共享资源都要透明：钱、权责、账号、合同、风险分担写清楚。",
                "把危机当作结构修复信号，不要等到爆发才处理。",
                "建立稳定身心支持系统：睡眠、运动、心理复盘、专业咨询都可以纳入。",
            ],
            "boundary": "本系统不预测死亡日期、死亡地点或灾难定论，只做风险主题和生活管理提示。",
        }

    if kandam == 9:
        ninth_lord = _house_lord(chart, 9)
        ninth_house = _planet_house(chart, ninth_lord)
        sun_house = _planet_house(chart, "Sun")
        return {
            "paragraphs": [
                (
                    f"第九章看父亲、福德、导师、信仰、寺庙、远行和人生意义感。第 9 宫主{PLANET_ZH[ninth_lord]}落第 {ninth_house} 宫，"
                    f"太阳落第 {sun_house} 宫，计都落第 {ketu_house} 宫，说明你和父辈、权威、传统信念之间不会只是顺从关系。"
                ),
                (
                    "这章的重点不是“有没有福气”这么简单，而是你的福气来自哪里。对你来说，福德更像是长期正向选择、导师线、学习、远行、"
                    "布施或帮助别人之后形成的回流，而不是纯粹被动等好运。"
                ),
            ],
            "manifestations": [
                "父亲线和资源来源需要单独看：父亲更像家庭财务来源，母亲更像资金管理者和直接给付者。",
                "你会尊重传统，但不会完全照父辈或权威指定的路线走。",
                "外地、远行、导师、课程、修行体系会周期性改变你的方向感。",
            ],
            "guidance": [
                "保留学习和导师线，但不要盲从任何权威。",
                "把父辈给你的资源、压力和信念分别写清楚，避免混成一种模糊命运感。",
                "多做长期有福报的事：教学、分享、帮助、布施、稳定修行和真实输出。",
            ],
        }

    if kandam == 10:
        tenth_lord = _house_lord(chart, 10)
        tenth_house = _planet_house(chart, tenth_lord)
        sun_house = _planet_house(chart, "Sun")
        saturn_house = _planet_house(chart, "Saturn")
        return {
            "paragraphs": [
                (
                    f"第十章看职业、事业、地位、职责和社会角色。第 10 宫主{PLANET_ZH[tenth_lord]}落第 {tenth_house} 宫，"
                    f"太阳第 {sun_house} 宫、土星第 {saturn_house} 宫，说明事业不是靠一阵爆发，而是靠长期责任、合作场景和稳定交付建立起来。"
                ),
                (
                    "你已经反馈职业前期试错多、真正起势靠长期积累是准的。这个判断应该作为事业章的核心锚点："
                    "你不是能力不行，而是需要把能力从零散状态推进到流程、产品、案例、客户和权威。"
                ),
            ],
            "manifestations": [
                "早年在组织和独立之间摆荡，是这张盘很典型的事业训练。",
                "你适合做复杂协作、咨询、内容策略、产品运营、研究分析、审美和商业结合型工作。",
                "真正的上升点来自可信度、结构化能力、长期服务和可复利资产。",
            ],
            "guidance": [
                "现在不要只问做什么行业，要问你能沉淀什么长期资产。",
                "把个人能力产品化：固定模块、固定流程、固定报价、固定复盘。",
                "事业中必须争取判断权，否则会一直被合作方、客户或组织节奏牵着走。",
            ],
        }

    if kandam == 11:
        eleventh_lord = _house_lord(chart, 11)
        eleventh_house = _planet_house(chart, eleventh_lord)
        second_lord = _house_lord(chart, 2)
        second_house = _planet_house(chart, second_lord)
        return {
            "paragraphs": [
                (
                    f"第十一章看收益、机会、朋友、社群、平台和欲望兑现。第 11 宫主{PLANET_ZH[eleventh_lord]}落第 {eleventh_house} 宫，"
                    f"第 2 宫主{PLANET_ZH[second_lord]}落第 {second_house} 宫，说明机会不是没有，但要通过工作系统、服务质量和长期合作兑现。"
                ),
                (
                    "这章和第二章、十章绑得很紧：你赚钱的方式更像技能沉淀、结构化合作或长期资源盘，而不是短期投机。"
                    "所以朋友、社群、平台、客户池，对你来说不是热闹，而是未来收益结构的一部分。"
                ),
            ],
            "manifestations": [
                "机会往往来自合作、社群、老客户、内容曝光或长期关系。",
                "你不适合只靠人情换机会，最好把人脉变成清楚的项目和价值交换。",
                "收益增长会被服务压力和交付能力限制，越标准化越容易放大。",
            ],
            "guidance": [
                "建立客户池、案例库、合作名单和复购机制。",
                "社交不要只泛泛认识人，要形成明确主题和可互相支持的资源网络。",
                "每一个机会都问：它能不能复用、能不能转介绍、能不能沉淀资产。",
            ],
        }

    if kandam == 12:
        twelfth_lord = _house_lord(chart, 12)
        twelfth_house = _planet_house(chart, twelfth_lord)
        navamsa_ketu = chart["vargas"]["navamsa"]["ketu_sign"]
        return {
            "paragraphs": [
                (
                    f"第十二章看支出、海外、迁移、隐退、睡眠、灵性和解脱。第 12 宫主{PLANET_ZH[twelfth_lord]}落第 {twelfth_house} 宫，"
                    f"罗喉第 {rahu_house} 宫、计都第 {ketu_house} 宫，Navamsa 计都在{_sign_zh(navamsa_ketu)}，说明迁移和抽离感不是偶发主题。"
                ),
                (
                    "你已经反馈外地、迁移、隐退、睡眠波动或想离开熟悉圈层重新开始这一条是准的。"
                    "所以这章应当重点写：你不是为了逃避而迁移，而是环境变化会帮你切断旧惯性、重新组织内在和事业。"
                ),
            ],
            "manifestations": [
                "睡眠、梦境、独处、远方、离开熟悉圈层会反复成为信号。",
                "支出不只是钱，也包括精力、情绪和关系消耗。",
                "灵性兴趣不能只是强体验，它需要稳定纪律和现实落地。",
            ],
            "guidance": [
                "建立固定修行节奏：书写、静坐、诵念、运动、睡眠复盘任选两项，坚持 90 天。",
                "做迁移或重启决定前，先分清是逃避消耗，还是新阶段真的需要新环境。",
                "把开销分成投资、消耗、修复、逃避四类，尤其注意情绪性支出。",
            ],
        }

    if kandam == 13:
        return {
            "paragraphs": [
                (
                    "第十三章是 Santhi Pariharam，传统上讲前世业力、重复模式和补救。当前系统没有真实叶片 verse，"
                    "所以不能给你编造某个前世身份、地点或罪业故事。更诚实的做法，是把它落到今生反复出现的模式上。"
                ),
                (
                    f"你的计都在第 {ketu_house} 宫，月亮在第 {moon_house} 宫，说明信念、父辈、远行、深层心理和抽离感会反复出现。"
                    "如果某类关系、某类责任、某类逃离冲动一直换形式回来，它就是这章应该处理的业力线。"
                ),
            ],
            "manifestations": [
                "同一类关系模式反复出现：责任、边界、精神理解、距离感或失控感。",
                "你会反复被玄学、心理、生死、宿命、修行主题吸引。",
                "某些阶段会突然觉得旧信念不再能解释自己，需要换一套人生框架。",
            ],
            "guidance": [
                "把“业力”翻译成可处理的问题：我反复在哪类人、哪类关系、哪类选择上失去边界。",
                "补救不只是仪式，更是修正行为：守信、布施、道歉、偿还、停止重复伤害。",
                "记录 3 个反复出现的人生模式，再为每个模式设计一个现实修正动作。",
            ],
            "boundary": "具体前世故事、罪业细节和叶片原文必须依赖真实叶片语料与人工校勘。",
        }

    if kandam == 14:
        ninth_lord = _house_lord(chart, 9)
        twelfth_lord = _house_lord(chart, 12)
        return {
            "paragraphs": [
                (
                    f"第十四章是 Deeksha，传统上讲 mantra、japa、护持、护符和精神纪律。第 9 宫主{PLANET_ZH[ninth_lord]}、"
                    f"第 12 宫主{PLANET_ZH[twelfth_lord]}以及土星共同说明：你的修行不适合只追求强烈体验，而要靠固定频率和长期纪律。"
                ),
                (
                    "你之前对“稳定本身就是修行”有收获，这应当作为这一章的核心。对你来说，真正有效的修法不是越神秘越好，"
                    "而是能不能让你睡眠更稳、边界更清楚、工作更有秩序、关系更少内耗。"
                ),
            ],
            "manifestations": [
                "强烈体验会吸引你，但长期真正改变你的是稳定频率。",
                "修行一旦脱离生活秩序，容易变成逃避现实责任。",
                "导师、传统、mantra、仪式可以帮助你，但不能替代现实选择。",
            ],
            "guidance": [
                "先固定 90 天基础法：书写、静坐、诵念、身体训练、早睡中的两项。",
                "修法效果只看现实指标：睡眠、情绪、边界、工作稳定度、关系清晰度。",
                "任何 mantra 或护符都需要可信传承来源，不要随便混用体系。",
            ],
            "boundary": "具体 mantra、护符、供养对象和仪轨不由当前系统编造，必须由真实传承文本或合格老师确认。",
        }

    if kandam == 15:
        sixth_lord = _house_lord(chart, 6)
        eighth_lord = _house_lord(chart, 8)
        saturn_house = _planet_house(chart, "Saturn")
        return {
            "paragraphs": [
                (
                    f"第十五章是 Aushadha，传统上讲长期疾病和药物。本系统不做诊断，也不给药方。只能从第 6 宫主{PLANET_ZH[sixth_lord]}、"
                    f"第 8 宫主{PLANET_ZH[eighth_lord]}、月亮第 {moon_house} 宫、土星第 {saturn_house} 宫，提示长期身心管理的方向。"
                ),
                (
                    "你的身体信号很可能和压力、睡眠、情绪压抑、合作责任、长期消耗有关。真正要重视的是：不要等身体把你按停，"
                    "才开始调整工作节奏和生活结构。"
                ),
            ],
            "manifestations": [
                "压力可能先表现为睡眠、疲劳、炎症、消化、紧张或情绪波动。",
                "关系、客户、工作责任如果边界不清，会直接进入身体层面。",
                "长期健康不是靠一次补救，而是靠作息、运动、饮食、检查和边界管理。",
            ],
            "guidance": [
                "做基础体检和长期指标记录，任何症状优先找专业医生。",
                "把工作负荷和身体状态一起复盘，不要只看收入和产出。",
                "建立最低健康纪律：固定睡眠窗口、每周运动、减少情绪性熬夜。",
            ],
            "boundary": "不提供诊断、药方、剂量或替代医疗建议；真实 Aushadha 章节也应由专业人士复核。",
        }

    if kandam == 16:
        return {
            "paragraphs": [
                (
                    f"第十六章是 Dasa Bukthi，大运分运预测。你当前走 {current_maha['label']}，时间从 {current_maha['start_date']} 到 {current_maha['end_date']}；"
                    f"当前分运是 {current_antara['label']}，时间从 {current_antara['start_date']} 到 {current_antara['end_date']}。"
                    f"下一步会进入 {next_maha['label']}。"
                ),
                (
                    _period_signature_paragraph(chart, current_lord, _planet_house(chart, current_lord), mode="present")
                    + "所以这几年最关键的不是等一个神秘事件发生，而是把大运主题变成行动：能力产品化、合作结构化、价值交换稳定化。"
                ),
            ],
            "manifestations": [
                f"{current_antara['start_date']} - {current_antara['end_date']} 更适合处理事业、合作、定价、交付和身体节律。",
                f"{next_maha['label']} 会把下一阶段重心转向新的主导权和角色定位。",
                "年度到季度可以看大运分运，月份级事件还需要 transit、真实反馈和长期回看继续校准。",
            ],
            "guidance": [
                "用 90 天为单位做大运复盘：事业、关系、财务、睡眠、迁移感各打一分。",
                "在当前金星阶段，优先把产品、合作、收入结构做稳。",
                "提前为下一主运准备角色权和公开表达，不要等切换时被动适应。",
            ],
            "boundary": "第 16 章可以给年度到季度级窗口，不能在缺少 transit 和回看样本时强断具体日期。",
        }

    raise ValueError(f"Unsupported Kandam: {kandam}")


def _section_identity(chart: dict[str, Any]) -> list[str]:
    lagna = chart["chart_summary"]["lagna"]
    lagna_lord = chart["chart_summary"]["lagna_lord"]
    lagna_lord_house = _planet_house(chart, lagna_lord)
    lagna_lord_sign = _planet(chart, lagna_lord)["sign"]
    moon_house = _planet_house(chart, "Moon")
    sun_companions = _companions(chart, lagna_lord)
    rahu_house = _planet_house(chart, "Rahu")
    ketu_house = _planet_house(chart, "Ketu")

    body = [
        "## 身份与人生主轴",
        "",
        (
            f"{_sign_zh(lagna)}上升的人，本来就有“我得成为自己人生主角”的底色。"
            f"但你的命主星{PLANET_ZH[lagna_lord]}并没有落回自我领域，而是落到了第 {lagna_lord_house} 宫，"
            f"所以你的人生不是关起门来完成的，而是通过 {HOUSE_ARENAS[lagna_lord_house]} 被塑形。"
        ),
        "",
        (
            f"{PLANET_ZH[lagna_lord]}落在{_sign_zh(lagna_lord_sign)}，"
            f"{_dignity_phrase(chart, lagna_lord)}"
            f"{_conjunction_phrase(chart, lagna_lord)}"
            f"这让你既有想主导局面的心，又很难完全按个人喜好随意来，"
            "因为现实关系、合作结构、责任边界会不断要求你成熟。"
        ),
        "",
        (
            f"月亮在第 {moon_house} 宫，又把情绪体放进了 {HOUSE_ARENAS[moon_house]}。"
            "这类配置通常不是表面外向、内里轻松，而是外面能扛，里面很深。"
            "你很可能不是一直都在表达感受，而是等事情累积到一定程度后，才突然决定重组、切换或离开。"
        ),
        "",
        (
            f"罗喉在第 {rahu_house} 宫、计都在第 {ketu_house} 宫，"
            "说明你的成长方式也带有典型的“离开旧秩序、自己去开路”的色彩。"
            "很多关键选择，不会完全按父辈路线或传统安全牌去走，而会被你亲自试出来。"
        ),
        "",
        "推导链：",
        f"- 命主星：{PLANET_ZH[lagna_lord]}落第 {lagna_lord_house} 宫，主线落在 {describe_house(lagna_lord_house)}。",
        f"- 情绪体：月亮落第 {moon_house} 宫，安全感与 {describe_house(moon_house)} 强绑定。",
        f"- 业力轴：罗喉/计都落在第 {rahu_house}/{ketu_house} 宫，推动你离开既定信念或路径。",
        "",
    ]
    return body


def _section_home(chart: dict[str, Any]) -> list[str]:
    fourth_lord = _house_lord(chart, 4)
    fourth_lord_house = _planet_house(chart, fourth_lord)
    fourth_lord_sign = _planet(chart, fourth_lord)["sign"]
    moon_house = _planet_house(chart, "Moon")
    jupiter_house = _planet_house(chart, "Jupiter")
    body = [
        "## 家宅、母缘与内在稳定",
        "",
        (
            f"你的第 4 宫由{PLANET_ZH[fourth_lord]}主导，而它落在第 {fourth_lord_house} 宫。"
            f"这说明“家”对你来说不是单纯背景，而是会直接牵动人生选择的重要因子。"
        ),
        "",
        (
            f"{PLANET_ZH[fourth_lord]}落在{_sign_zh(fourth_lord_sign)}，{_dignity_phrase(chart, fourth_lord)}"
            f"如果这颗星同时又落在第 {fourth_lord_house} 宫这样的耗损或迁移区域，"
            "常见表现就是：家宅主题容易伴随距离、牺牲、迁动、隐忍或情绪负担。"
        ),
        "",
        (
            f"再看月亮落第 {moon_house} 宫，木星落第 {jupiter_house} 宫。"
            "这组合更像是：真正压在你心里的，不一定只是钱，而是情绪牵连、照料感、家庭里的隐性责任和无法彻底放下的挂念。"
            "你并不是没有建立安全感的能力，而是你需要比别人更深地整理情绪、空间和家庭边界。"
            "只靠扛、只靠忍，最后往往会以睡眠、情绪波动、搬家冲动或突然抽离的方式表现出来。"
        ),
        "",
        "你更适合的家宅路径，不是追求表面完美，而是：",
        "- 有可退回的私人空间。",
        "- 家庭责任要说清楚，不要长期默认自己承担。",
        "- 居住环境、睡眠节律、财务秩序要一起调，不然内在会一直散。",
        "",
        "推导链：",
        f"- 第 4 宫主：{PLANET_ZH[fourth_lord]}落第 {fourth_lord_house} 宫。",
        f"- 月亮落第 {moon_house} 宫，显示家庭和安全感议题会进入深层心理。",
        f"- 木星落第 {jupiter_house} 宫，说明仍然存在修复与重建家庭感的能力。",
        "",
    ]
    return body


def _section_relationship(chart: dict[str, Any]) -> list[str]:
    seventh_lord = _house_lord(chart, 7)
    seventh_lord_house = _planet_house(chart, seventh_lord)
    seventh_lord_sign = _planet(chart, seventh_lord)["sign"]
    venus_house = _planet_house(chart, "Venus")
    venus_sign = _planet(chart, "Venus")["sign"]
    navamsa_venus = chart["vargas"]["navamsa"]["venus_sign"]
    body = [
        "## 关系、伴侣与合作模式",
        "",
        (
            f"你的关系线不是轻松型，也不是只靠感觉推进的类型。"
            f"第 7 宫主{PLANET_ZH[seventh_lord]}落在第 {seventh_lord_house} 宫，"
            "说明伴侣关系、合作关系、客户关系都会直接进入你的人生主线。"
        ),
        "",
        (
            f"{PLANET_ZH[seventh_lord]}落在{_sign_zh(seventh_lord_sign)}，{_dignity_phrase(chart, seventh_lord)}"
            f"金星落在第 {venus_house} 宫的{_sign_zh(venus_sign)}，Navamsa 金星又落在{_sign_zh(navamsa_venus)}。"
            "这常见的现实版本是：你不是只要心动，你要的是能一起扛现实、一起成长、最好还能在精神上互相理解的人。"
        ),
        "",
        (
            "所以你的关系课题通常不是“有没有桃花”这么简单，而是："
            "你会不会因为责任、工作节奏、现实压力、价值感问题，把关系推进得太沉；"
            "或者反过来，因为害怕失控，而迟迟不肯真正交付。"
        ),
        "",
        "对你更好的关系，不是没有压力，而是压力可以被共同处理：",
        "- 对方本身要有责任感和边界感。",
        "- 关系里必须允许现实问题被讨论，而不是全部用情绪吞下去。",
        "- 你需要的是长期可共建，而不是短期热烈后迅速耗尽。",
        "",
        "推导链：",
        f"- 第 7 宫主：{PLANET_ZH[seventh_lord]}落第 {seventh_lord_house} 宫。",
        f"- 金星：落第 {venus_house} 宫，关系与价值感会进入工作与现实责任线。",
        f"- Navamsa 金星：落在{_sign_zh(navamsa_venus)}，长期关系要求精神和价值观的契合。",
        "",
    ]
    return body


def _section_career(chart: dict[str, Any]) -> list[str]:
    tenth_lord = _house_lord(chart, 10)
    tenth_lord_house = _planet_house(chart, tenth_lord)
    tenth_lord_sign = _planet(chart, tenth_lord)["sign"]
    saturn_house = _planet_house(chart, "Saturn")
    mercury_house = _planet_house(chart, "Mercury")
    venus_house = _planet_house(chart, "Venus")
    body = [
        "## 事业与社会角色",
        "",
        (
            f"你的事业不是那种“天赋一露面就一路直冲”的盘。"
            f"第 10 宫主{PLANET_ZH[tenth_lord]}落第 {tenth_lord_house} 宫，"
            f"说明职业路线要通过 {HOUSE_ARENAS[tenth_lord_house]} 打磨出来。"
        ),
        "",
        (
            f"{PLANET_ZH[tenth_lord]}落在{_sign_zh(tenth_lord_sign)}，{_dignity_phrase(chart, tenth_lord)}"
            f"再看土星落第 {saturn_house} 宫，水星和金星都参与了第 {mercury_house}/{venus_house} 宫这条线。"
            "这类配置很适合做需要长期沉淀、持续服务、复杂协作、结构搭建、审美和认知都要一起工作的事情。"
        ),
        "",
        (
            "更直接地说，你的事业好结果，不来自一把梭的冲刺，而来自以下几类能力的复利："
        ),
        "- 把复杂问题拆开、整理、流程化。",
        "- 把关系、内容、审美或策略转成稳定可交付的价值。",
        "- 在合作和客户场景里建立自己的角色权威，而不是只做幕后执行。",
        "",
        (
            "如果职业早年有反复试错、在组织与独立之间摆荡、明明能力不差却经常被现实琐事拖住，"
            "这反而和你的盘是相符的。因为这张盘的成长路径本来就不是先轻松、后成熟，"
            "而是先在责任里练出专业度，后面才逐渐把判断权拿回来。"
        ),
        "",
        "推导链：",
        f"- 第 10 宫主：{PLANET_ZH[tenth_lord]}落第 {tenth_lord_house} 宫。",
        f"- 土星落第 {saturn_house} 宫，事业抬升依赖长期主义和结构。",
        f"- 水星落第 {mercury_house} 宫、金星落第 {venus_house} 宫，说明认知、沟通、审美和服务会一起进入职业线。",
        "",
    ]
    return body


def _section_spirituality(chart: dict[str, Any]) -> list[str]:
    ninth_lord = _house_lord(chart, 9)
    ninth_lord_house = _planet_house(chart, ninth_lord)
    twelfth_lord = _house_lord(chart, 12)
    twelfth_lord_house = _planet_house(chart, twelfth_lord)
    ketu_house = _planet_house(chart, "Ketu")
    moon_house = _planet_house(chart, "Moon")
    navamsa_lagna = chart["chart_summary"]["navamsa_lagna"]
    body = [
        "## 迁移、灵性与内在重组",
        "",
        (
            f"这张盘的灵性线不是抽象兴趣，而是和现实人生真正拴在一起。"
            f"第 9 宫主{PLANET_ZH[ninth_lord]}落第 {ninth_lord_house} 宫，"
            f"第 12 宫主{PLANET_ZH[twelfth_lord]}落第 {twelfth_lord_house} 宫，"
            "再加上计都参与，这往往意味着信念、迁移、修行、抽离感这些主题会反复出现。"
        ),
        "",
        (
            f"尤其当月亮落在第 {moon_house} 宫、计都落在第 {ketu_house} 宫时，"
            "你会对“表层生活不够解释一切”这件事特别敏感。"
            "你可能比周围人更早接触深层心理、玄学、修行、梦境、宿命感、突然的离开冲动，"
            "或者总觉得自己终究要走一条和常规路线不太一样的路。"
        ),
        "",
        (
            f"Navamsa 上升落在{_sign_zh(navamsa_lagna)}，这提醒你：真正适合你的修行不是逃开现实，"
            "而是把关系、选择、边界、价值观和现实执行慢慢统一。"
            "如果修行只停留在情绪起伏时的短暂寄托，它不会真的稳。"
        ),
        "",
        "这条线更可能以这些现实形式出现：",
        "- 迁移、换城市、离开熟悉圈层后反而打开自己。",
        "- 睡眠、梦境、情绪潮汐明显，需要独处和恢复空间。",
        "- 对父辈信念、传统路径或权威体系既尊重又不完全服从。",
        "",
        "推导链：",
        f"- 第 9 宫主：{PLANET_ZH[ninth_lord]}落第 {ninth_lord_house} 宫。",
        f"- 第 12 宫主：{PLANET_ZH[twelfth_lord]}落第 {twelfth_lord_house} 宫。",
        f"- 计都落第 {ketu_house} 宫，月亮落第 {moon_house} 宫，增强抽离和内在重组主题。",
        "",
    ]
    return body


def _section_career_wealth_synthesis(chart: dict[str, Any], theme_ids: set[str]) -> list[str]:
    second_lord = _house_lord(chart, 2)
    second_lord_house = _planet_house(chart, second_lord)
    eleventh_lord = _house_lord(chart, 11)
    eleventh_lord_house = _planet_house(chart, eleventh_lord)
    jupiter_house = _planet_house(chart, "Jupiter")
    body = [
        "## 事业财富合参",
        "",
        (
            f"你的财富逻辑和事业逻辑是绑在一起的。"
            f"第 2 宫主{PLANET_ZH[second_lord]}落第 {second_lord_house} 宫，"
            f"第 11 宫主{PLANET_ZH[eleventh_lord]}落第 {eleventh_lord_house} 宫，"
            f"木星又落第 {jupiter_house} 宫。"
            "这不是一张单靠短线刺激、投机波动就能长期舒服赚钱的盘。"
        ),
        "",
        (
            "它更像这样一种模式：先用认知、沟通、系统、长期合作把价值做厚，"
            "然后收益才逐步累积起来。你适合的是能被复用、能被信任、能被持续购买的价值，"
            "而不是只靠一次交易或一次运气。"
        ),
        "",
        "如果你要判断“创业还是上班”，更准确的问法不是二选一，而是：",
        "- 你能不能把自己的能力沉淀成可反复出售的结构。",
        "- 你能不能在合作/客户场景中保留判断权。",
        "- 你能不能承受早期并不轻松、但长期能复利的路径。",
        "",
    ]
    if "career" in theme_ids:
        body.extend(
            [
                "事业上更适合的方向特征：",
                "- 复杂协作、咨询、研究、内容策略、产品/运营、审美和商业结合型工作。",
                "- 需要长期积累信任，不是纯短平快的岗位。",
                "- 能在结构里成长，后期再逐步放大独立性。",
                "",
            ]
        )
    if "wealth" in theme_ids:
        body.extend(
            [
                "财富上更适合的策略：",
                "- 建长期客户或长期合作，而不是只追一次性回款。",
                "- 让收入和方法论、作品、系统、口碑挂钩。",
                "- 高波动投机可以研究，但不宜作为主命脉。",
                "",
            ]
        )
    return body


def _section_spiritual_tone(chart: dict[str, Any]) -> list[str]:
    body = [
        "## 灵性线的正确打开方式",
        "",
        (
            "你的盘确实有灵性、玄学、深层心理、迁移和抽离感这些线索。"
            "但这并不意味着最适合你的路是彻底脱离现实。"
            "相反，你真正的功课，是在现实责任、关系秩序和内在修行之间建立稳定桥梁。"
        ),
        "",
        (
            "所以比起追求瞬间开悟、强烈体验或频繁换体系，"
            "你更适合固定频率的长期方法：书写、静坐、诵念、身体训练、规律睡眠、周期复盘。"
            "对你来说，稳定本身就是修行。"
        ),
        "",
    ]
    return body


def _section_timing(chart: dict[str, Any]) -> list[str]:
    current_maha = _current_dasha(chart, "current", level=1)
    next_maha = _current_dasha(chart, "next", level=1)
    current_antara = _current_dasha(chart, "current", level=2)
    maha_lord = current_maha["lords"][0]
    antara_lord = current_antara["lords"][-1]
    maha_house = _planet_house(chart, maha_lord)
    antara_house = _planet_house(chart, antara_lord)
    next_lord = next_maha["lords"][0]
    next_house = _planet_house(chart, next_lord)
    return [
        "## 当前阶段与时间窗口",
        "",
        (
            f"你现在走的是 {PLANET_ZH[maha_lord]} 大运，时间从 {current_maha['start_date']} 到 {current_maha['end_date']}。"
            + _period_signature_paragraph(chart, maha_lord, maha_house, mode="main")
        ),
        "",
        (
            f"当前分运是 {PLANET_ZH[antara_lord]} 分运，时间从 {current_antara['start_date']} 到 {current_antara['end_date']}。"
            + _subperiod_signature_paragraph(chart, maha_lord, antara_lord, antara_house)
        ),
        "",
        (
            f"下一步会走向 {PLANET_ZH[next_lord]} 大运。因为它落在第 {next_house} 宫，"
            + _period_signature_paragraph(chart, next_lord, next_house, mode="next")
        ),
        "",
    ]


def _section_past_present_future(chart: dict[str, Any]) -> list[str]:
    periods = chart.get("dasha_timeline", {}).get("mahadasha", [])
    if not periods:
        return []
    current_index = 0
    current_label = chart["chart_summary"]["current_mahadasha"]
    for index, item in enumerate(periods):
        if item["label"] == current_label:
            current_index = index
            break
    past_periods = periods[max(0, current_index - 2):current_index]
    current_period = periods[current_index]
    future_periods = periods[current_index + 1:current_index + 3]

    lines = [
        "## 过去、现在、未来",
        "",
        "下面这部分不是随便猜测，而是按大运主线把你的生命节奏拆开来看。",
        "",
        "### 过去已经走过的阶段",
    ]
    if past_periods:
        for period in past_periods:
            lines.extend(_timeline_block(chart, period, tense="past"))
    else:
        lines.append("- 当前没有足够早期大运数据可展示。")
    lines.extend(["", "### 你现在正在走的阶段"])
    lines.extend(_timeline_block(chart, current_period, tense="present"))
    lines.extend(["", "### 你接下来会进入的阶段"])
    if future_periods:
        for period in future_periods:
            lines.extend(_timeline_block(chart, period, tense="future"))
    else:
        lines.append("- 当前没有更多未来大运数据。")
    lines.append("")
    return lines


def _section_validation(reading: dict[str, Any]) -> list[str]:
    lines = [
        "## 请你重点核验这些句子",
        "",
        "你在看这份报告时，最值得核验的不是形容词，而是下面这些生活事实：",
    ]
    for item in reading.get("identity_checks", []):
        lines.append(f"- {item['question']}")
    lines.extend(
        [
            "",
            "如果你要反馈准确性，最有价值的方式是：",
            "- 标成 `准`：明显贴中你的长期事实。",
            "- 标成 `半准`：方向对，但轻重或表现方式不完全一样。",
            "- 标成 `不准`：与你的真实经历明显相反。",
            "",
        ]
    )
    return lines


def _section_appendix(
    *,
    birth: dict[str, Any],
    reference_date: date,
    chart: dict[str, Any],
    quality_score: dict[str, Any],
    accuracy_profile: dict[str, Any],
    cross_validation: dict[str, Any],
    missing_capabilities: list[str],
) -> list[str]:
    lines = [
        "## 技术附录",
        "",
        f"- 出生资料：{birth['date']} {birth['time']}，{birth['location_name']}，UTC{birth['timezone_offset']:+g}",
        f"- 参考日期：{reference_date.isoformat()}",
        f"- 主引擎：PyJHora ({chart['engine_config']['ayanamsa_mode']})",
        f"- 内部产品质量分：`{quality_score['total_score']}/100`",
        f"- 命理准确度画像：`{accuracy_profile['total_score']}/100`",
        f"- 盘面计算准确度：`{_dimension_score(accuracy_profile, 'chart_calculation_accuracy')}/100`",
        f"- 解读可追溯性：`{_dimension_score(accuracy_profile, 'interpretation_traceability')}/100`",
        f"- 实证验证成熟度：`{_dimension_score(accuracy_profile, 'empirical_validation_maturity')}/100`",
        f"- 双引擎验证分：`{cross_validation['validation_score']}/100`",
        f"- major diff：`{len(cross_validation.get('major_diffs', []))}`",
        f"- minor diff：`{len(cross_validation.get('minor_diffs', []))}`",
    ]
    if cross_validation.get("minor_diffs"):
        lines.append("- 仍需注意的差异：")
        for diff in cross_validation["minor_diffs"]:
            lines.append(f"  - {diff['field']}：delta={diff['delta']}")
    if missing_capabilities:
        lines.append("- 能力边界：")
        for item in missing_capabilities:
            lines.append(f"  - {item}")
    lines.append("- 名字边界：")
    lines.append("  - 当前系统不能诚实推出父母、伴侣、对象或过去相识者的真实姓名。")
    lines.append("  - 若未来接入真实叶片语料、姓名音节索引和人工校对，才有资格研究这一层。")
    lines.append("")
    return lines


def _planet(chart: dict[str, Any], name: str) -> dict[str, Any]:
    for item in chart.get("planets", []):
        if item["name"] == name:
            return item
    raise KeyError(name)


def _planet_house(chart: dict[str, Any], name: str) -> int:
    return int(_planet(chart, name)["house_from_lagna"])


def _house_lord(chart: dict[str, Any], house_number: int) -> str:
    lagna = chart["chart_summary"]["lagna"]
    sign_name = house_sign_name(lagna, house_number)
    return sign_lord_name(sign_name)


def _planet_rulerships(chart: dict[str, Any], planet: str) -> list[int]:
    houses: list[int] = []
    for house_number in range(1, 13):
        if _house_lord(chart, house_number) == planet:
            houses.append(house_number)
    return houses


def _rulership_text(houses: list[int]) -> str:
    if not houses:
        return "其他宫位主题"
    parts = [f"第 {house} 宫（{HOUSE_ARENAS[house]}）" for house in houses]
    return "、".join(parts)


def _companions(chart: dict[str, Any], name: str) -> list[str]:
    house = _planet_house(chart, name)
    return [planet for planet in PLANET_ORDER if planet != name and _planet_house(chart, planet) == house]


def _placement_sentence(chart: dict[str, Any], planet: str) -> str:
    data = _planet(chart, planet)
    sentence = (
        f"{PLANET_ZH[planet]}在{_sign_zh(data['sign'])}第 {data['house_from_lagna']} 宫，"
        f"把 {PLANET_ESSENCE[planet]} 放进了 {HOUSE_ARENAS[int(data['house_from_lagna'])]}。"
    )
    dignity = _dignity_phrase(chart, planet)
    companions = _companions(chart, planet)
    if dignity or companions:
        sentence += " "
    if dignity:
        sentence += dignity
    if companions:
        sentence += _conjunction_phrase(chart, planet)
    return sentence


def _dignity_phrase(chart: dict[str, Any], planet: str) -> str:
    sign = _planet(chart, planet)["sign"]
    if planet in EXALTATION_SIGNS and sign == EXALTATION_SIGNS[planet]:
        return f"{PLANET_ZH[planet]}在这里入旺，力量表达比较直接。"
    if planet in DEBILITATION_SIGNS and sign == DEBILITATION_SIGNS[planet]:
        return f"{PLANET_ZH[planet]}在这里偏弱，相关课题往往要先经历拉扯，再学会稳定表达。"
    if sign_lord_name(sign) == planet:
        return f"{PLANET_ZH[planet]}在这里守本位，相关主题会更稳定、更硬核。"
    house = _planet_house(chart, planet)
    if house in DUSTHANA_HOUSES:
        return f"{PLANET_ZH[planet]}落入 dusthana 宫位，相关主题带有修正、耗损、压力或转化色彩。"
    if house in KENDRA_HOUSES:
        return f"{PLANET_ZH[planet]}落在 kendra 宫位，相关主题会被放大到人生主舞台。"
    if house in TRIKONA_HOUSES:
        return f"{PLANET_ZH[planet]}落在 trikona 宫位，相关主题比较容易形成天赋和福报线。"
    if house in UPACHAYA_HOUSES:
        return f"{PLANET_ZH[planet]}落在 upachaya 宫位，越走越成熟，早期通常要先练功。"
    return ""


def _conjunction_phrase(chart: dict[str, Any], planet: str) -> str:
    companions = _companions(chart, planet)
    if not companions:
        return ""
    joined = "、".join(PLANET_ZH[item] for item in companions)
    return f"它又与 {joined} 同宫，所以这几条人生线会被绑在一起运作。"


def _current_maha_lord(chart: dict[str, Any]) -> str:
    label = chart["chart_summary"]["current_mahadasha"]
    return label.split(" / ")[0]


def _current_dasha(chart: dict[str, Any], status: str, *, level: int) -> dict[str, Any]:
    for item in chart.get("dashas", []):
        if item["status"] != status:
            continue
        if len(item.get("lords", [])) == level:
            return item
    raise LookupError(f"dasha not found: status={status}, level={level}")


def _timeline_block(chart: dict[str, Any], period: dict[str, Any], *, tense: str) -> list[str]:
    lord = period["lords"][0]
    house = _planet_house(chart, lord)
    sign = _planet(chart, lord)["sign"]
    lines = [f"- `{period['start_date']} - {period['end_date'] or '以后'}`｜{PLANET_ZH[lord]}大运"]
    if tense == "past":
        lines.append(
            "  "
            + (
                _period_signature_paragraph(chart, lord, house, mode="past")
            )
        )
    elif tense == "present":
        lines.append(
            "  "
            + (
                _period_signature_paragraph(chart, lord, house, mode="present")
            )
        )
    else:
        lines.append(
            "  "
            + (
                _period_signature_paragraph(chart, lord, house, mode="future")
            )
        )
    lines.extend(_period_event_hypotheses(chart, lord, house, tense))
    return lines


def _period_event_hypotheses(chart: dict[str, Any], lord: str, house: int, tense: str) -> list[str]:
    prefix = "  更可能体现成："
    items: list[str] = [prefix]
    if lord == "Mercury" and tense == "past":
        return [
            prefix,
            "  - 学习、考试、比较、被评价、表达能力和技能训练会成为那段时间的底色。",
            "  - 你会比较早地意识到：能力不是抽象天赋，而是要拿得出结果、讲得清楚、经得起比较。",
            "  - 家里或环境里对“有用、有效率、能证明自己”这件事的要求，容易压得比较深。",
            "  - 也更容易形成一种感觉：脑子不差，但总被细节、标准、流程或现实琐事牵住。 ",
        ]
    if lord == "Venus" and tense == "present":
        return [
            prefix,
            "  - 事业不再只是做内容或做能力，而是要进入定价、合作、交付、复购和长期结构。",
            "  - 你会更明显地感到：关系质量、合作公平、身体节律、赚钱方式其实是一体的。",
            "  - 组织内发展和更独立的发展之间，还会继续拉扯，但这次拉扯比以前更现实，不再只是想法。",
            "  - 如果继续含糊地工作、含糊地合作、含糊地收费，这个周期就会不断给你反馈。 ",
        ]
    if house == 6:
        items.extend(
            [
                "  - 项目交付、客户关系、团队协作、效率体系和身体节律会一起被拉上台面。",
                "  - 你会越来越受不了含糊和混乱，逼着自己把能力流程化、产品化、稳定化。",
                "  - 钱和关系问题不会孤立发生，往往会通过合作方式、分工结构或价值交换一起冒出来。",
            ]
        )
    elif house == 7:
        items.extend(
            [
                "  - 伴侣、合作、客户、合同和公开关系会明显增加人生重量。",
                "  - 你会被迫学习如何在关系中保留判断权，而不是只顺着对方或顺着局势走。",
                "  - 很多机会和挑战都来自“你和谁绑定、如何绑定、绑定后谁说了算”。",
            ]
        )
    elif house == 8:
        items.extend(
            [
                "  - 情绪、关系、共享财务、深层心理或突然的切换/重组会更明显。",
                "  - 旧模式会被逼到不能再用，必须做一次真正的内在翻修。",
                "  - 这通常也是接触心理学、疗愈、玄学、宿命感或生死议题更深的一段。",
            ]
        )
    elif house == 9:
        items.extend(
            [
                "  - 信念、远行、导师、父辈关系、学业或世界观会发生重置。",
                "  - 你可能离开旧的价值体系，开始寻找自己的解释框架。",
                "  - 对外看像“方向变化”，对内其实是命运感和意义感在重写。",
            ]
        )
    elif house == 12:
        items.extend(
            [
                "  - 迁移、离开、独处、睡眠、隐退、疗愈或开销问题会明显增加。",
                "  - 你会更需要切断旧环境，或者被现实推着走向边界更松动的新阶段。",
                "  - 这是最不适合自我麻痹的一类周期，因为很多信号会先从身体和情绪里出来。",
            ]
        )
    elif house == 4:
        items.extend(
            [
                "  - 家宅、居住、房产、母亲、内在安全感会成为主线。",
                "  - 看起来像在处理家庭事务，实则在重建自己的根基。",
                "  - 这也是适合积累内功、学习、稳定心性的阶段。",
            ]
        )
    elif house == 10:
        items.extend(
            [
                "  - 职位、名声、责任、公开成绩和角色权威会被明显放大。",
                "  - 这往往是更需要承担、也更容易被看见的一段。",
                "  - 如果前面基础没打稳，这个阶段会同时带来压力和曝光。",
            ]
        )
    elif house == 3:
        items.extend(
            [
                "  - 输出、写作、表达、技能训练、内容生产、短途奔波和自主开路会增加。",
                "  - 这是你更敢试、更想自己做决定的一段。",
                "  - 与兄弟姐妹、同伴或小团队的互动，也更容易成为现实推力。",
            ]
        )
    else:
        items.extend(
            [
                f"  - {PLANET_ZH[lord]}相关课题会被推向 {HOUSE_ARENAS[house]}。",
                f"  - 现实中多半会以 {describe_house(house)} 的具体事件来体现。",
            ]
        )

    if lord == "Ketu":
        items.append("  - 这类阶段通常还伴随抽离感、舍弃感，像是在把旧身份从你身上剥下来。")
    if lord == "Venus":
        items.append("  - 你会更强烈地被价值感、关系质量、合作公平感和金钱交换问题触发。")
    if lord == "Mercury":
        items.append("  - 认知、沟通、学习、交易和信息处理会成为关键变量。")
    if lord == "Sun":
        items.append("  - 角色感、主导权、面子和是否被真正看见，会变成核心议题。")
    if lord == "Moon":
        items.append("  - 这段时间的事件通常更贴身，也更容易直接影响睡眠和情绪体。")

    if tense == "future":
        items.append("  - 现在就提前布局这条线，未来会轻很多。")
    return items


def _current_period_one_liner(chart: dict[str, Any], lord: str, house: int) -> str:
    if lord == "Venus" and house == 6:
        return (
            "当前大运由金星主导，但这颗金星不是轻松享乐型，而是把事业、表达、合作和收入都拉进现实磨炼期。"
            "你眼下最该处理的是如何把能力、关系和价值交换做成长期稳定结构。"
        )
    if lord == "Ketu" and house == 9:
        return (
            "当前大运由计都主导，这会把信念、方向、导师线和旧身份一起拆开重组。"
            "很多看似迷茫的阶段，本质上是在剥离不再适合你的旧路径。"
        )
    if lord == "Sun" and house == 7:
        return (
            "当前大运由太阳主导，会把角色权、公开位置、合作关系和被看见的方式一起推上台面。"
        )
    return (
        f"当前大运由 {PLANET_ZH[lord]} 主导，而它落在第 {house} 宫。"
        f"这意味着你眼下最该处理的是 {HOUSE_ARENAS[house]} 这条线的具体现实。"
    )


def _period_signature_paragraph(chart: dict[str, Any], lord: str, house: int, *, mode: str) -> str:
    rulerships = _planet_rulerships(chart, lord)
    companions = _companions(chart, lord)
    companion_text = ""
    if companions:
        companion_text = "而且它还和 " + "、".join(PLANET_ZH[item] for item in companions) + " 同宫"

    if lord == "Mercury" and house == 6:
        companion_clause = f"{companion_text}，所以认知、沟通和价值交换会一起被现实训练。" if companion_text else "所以认知、沟通和价值交换会被现实训练。"
        return (
            f"这段周期的关键，不只是 {HOUSE_ARENAS[house]}，而是它把你命盘里的财务、收益、技能证明和现实评价绑在一起。"
            "更像是：学习、考试、比较、效率、表达能力、被评价和被要求有用，构成了那段时间的底色。"
            + companion_clause
        )
    if lord == "Ketu" and house == 9:
        return (
            "这不是普通的顺行阶段，而是典型的“旧信念被抽空”的周期。"
            "你更容易离开旧方向、旧老师、旧价值框架，去找新的解释方式；外面看像迷茫或绕路，里面其实是命运感在重写。"
        )
    if lord == "Venus" and house == 6:
        return (
            "这二十年真正的主题，不是简单的辛苦或打工，而是把事业、表达、合作和收入结构一起拉进现实磨炼。"
            "你会更频繁地遇到：项目交付、客户关系、团队配合、价值定价、身体节律、工作边界这些问题。"
            "这不是坏事，它是在逼你把能力从“会做”升级成“能长期稳定兑现”。"
        )
    if lord == "Sun" and house == 7:
        return (
            "这一段不会再允许你只做隐藏的能干者。"
            "你会被拉到关系、合作、公众角色和外部评价里，必须学会在与他人的绑定中，仍然保有自己的判断权和角色中心。"
        )
    if lord == "Moon" and house == 8:
        return (
            "这段时间更像深水区。"
            "共享关系、心理翻修、情绪体、睡眠、金钱纠缠、信任和失控感，都会要求你做更深层的处理。"
        )
    if mode == "next":
        return (
            f"后续人生重心会逐渐转到 {HOUSE_ARENAS[house]}。"
            f"{PLANET_ZH[lord]}同时还管着 { _rulership_text(rulerships) }，"
            "所以最好从现在就开始为这条线铺地基。"
        )
    if mode == "sub":
        return (
            f"这一段更像主运里的聚焦子主题，重点会落在 {HOUSE_ARENAS[house]}。"
            f"{PLANET_ZH[lord]}同时牵动 { _rulership_text(rulerships) }，所以事件不会只在一个领域发生。"
        )
    if mode == "past":
        return (
            f"这段时间更容易把你推向 {HOUSE_ARENAS[house]}。"
            f"{PLANET_ZH[lord]}同时还主 { _rulership_text(rulerships) }，所以过去如果这一段里这些主题被一起搅动，是符合盘面的。"
        )
    if mode == "present":
        return (
            f"你现在正在被 {HOUSE_ARENAS[house]} 这条线重新塑形。"
            f"{PLANET_ZH[lord]}同时还主 { _rulership_text(rulerships) }，所以眼前发生的事通常不是单点问题，而是一整组人生结构在调整。"
        )
    return (
        f"{PLANET_ZH[lord]}落第 {house} 宫，会把 {HOUSE_ARENAS[house]} 放上主舞台。"
    )


def _subperiod_signature_paragraph(chart: dict[str, Any], maha_lord: str, antara_lord: str, antara_house: int) -> str:
    if maha_lord == antara_lord == "Venus":
        return (
            "这是金星大运里的金星分运，所以主旋律会被放大，不会分散。"
            "更像是：事业路径、合作质量、收入结构、身体节律和价值感要在同一个阶段一起被校准。"
        )
    return _period_signature_paragraph(chart, antara_lord, antara_house, mode="sub")


def _dimension_score(scorecard: dict[str, Any], identifier: str) -> int:
    for item in scorecard.get("dimensions", []):
        if item["id"] == identifier:
            return int(item["score"])
    raise KeyError(identifier)


def _sign_zh(sign: str) -> str:
    return f"{SIGN_ZH.get(sign, sign)}（{sign}）"
