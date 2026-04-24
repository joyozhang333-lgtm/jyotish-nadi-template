from __future__ import annotations

from datetime import date
from typing import Iterable

from .chart_adapter import (
    DUSTHANA_HOUSES,
    HOUSE_TOPICS,
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
    describe_house,
    house_sign_name,
    sign_lord_name,
)
from .models import (
    EvidenceTag,
    FingerprintReading,
    IdentityCheck,
    InputQuality,
    KandamClaim,
    KandamReading,
    ReadingBundle,
    ThemeClaim,
    ThemePack,
    ThemeSection,
    TimingWindow,
)

SUPPORTED_KANDAMS = tuple(range(1, 17))
KANDAM_TITLES = {
    1: "身份总纲",
    2: "财富、家庭、教育与表达",
    3: "兄弟姐妹、胆识与技能",
    4: "家宅与母缘",
    5: "子女、创造力与传承",
    6: "疾病、债务、敌对与阻碍",
    7: "婚姻与关系",
    8: "寿元、风险、危机与转化",
    9: "父缘、福德、导师与远行",
    10: "事业与职责",
    11: "收益、机会、社群与二次关系",
    12: "迁移、开销与灵性",
    13: "Santhi Pariharam：前世业力与补救",
    14: "Deeksha：修法、护持与纪律",
    15: "Aushadha：长期身心健康倾向",
    16: "Dasa Bukthi：大运分运预测",
}


def build_reading_bundle(
    chart: dict,
    requested_chapters: list[int] | None = None,
    requested_theme_packs: list[ThemePack] | None = None,
    fingerprint_reading: FingerprintReading | None = None,
    reference_date: date | None = None,
) -> ReadingBundle:
    if requested_chapters is None:
        requested_chapters = list(SUPPORTED_KANDAMS)
    if requested_theme_packs is None:
        requested_theme_packs = [
            ThemePack.CAREER,
            ThemePack.WEALTH,
            ThemePack.SPIRITUALITY,
        ]

    input_quality = InputQuality(**chart["input_quality"])
    identity_checks = _build_identity_checks(chart, requested_chapters, requested_theme_packs)
    kandam_readings = [_build_kandam(chart, kandam) for kandam in requested_chapters if kandam in SUPPORTED_KANDAMS]
    theme_sections = [_build_theme_section(chart, theme) for theme in requested_theme_packs]
    timing_windows = _build_timing_windows(chart)
    remedies = _build_remedies(chart, requested_theme_packs)
    missing_capabilities = [
        "真实叶片语料库尚未接入，当前仍是纳迪风格解释层。",
        "手印找叶与叶束索引尚未接入，不能宣称真实叶片匹配。",
    ]
    if fingerprint_reading is not None:
        missing_capabilities.append(
            "自动指纹分型目前只支持 loop / whorl / arch 的探索性分类，不等于真实纳迪找叶。"
        )

    return ReadingBundle(
        input_quality=input_quality,
        chart_summary=chart["chart_summary"],
        requested_chapters=requested_chapters,
        requested_theme_packs=requested_theme_packs,
        fingerprint_reading=fingerprint_reading,
        identity_checks=identity_checks,
        kandam_reading=kandam_readings,
        theme_sections=theme_sections,
        timing_windows=timing_windows,
        remedy_candidates=remedies,
        missing_capabilities=missing_capabilities,
    )


def _build_identity_checks(
    chart: dict,
    requested_chapters: list[int],
    requested_theme_packs: list[ThemePack],
) -> list[IdentityCheck]:
    checks: list[IdentityCheck] = []
    if 2 in requested_chapters:
        second_lord = _house_lord(chart, 2)
        checks.append(
            IdentityCheck(
                question="你的赚钱、表达、学习和家庭资源是否经常绑在一起：能力越能被结构化表达，收入越稳定？",
                reason=f"第 2 宫主 {second_lord} 落在第 {_planet_house(chart, second_lord)} 宫，用于核验财富、家庭与表达方式。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            )
        )
    if 3 in requested_chapters:
        third_lord = _house_lord(chart, 3)
        checks.append(
            IdentityCheck(
                question="你的人生是否需要靠自学、输出、表达、短途移动或自己主动开路来打开局面？",
                reason=f"第 3 宫主 {third_lord} 落在第 {_planet_house(chart, third_lord)} 宫，用于核验胆识、技能与同辈协作。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            )
        )
    if 4 in requested_chapters:
        fourth_lord = _house_lord(chart, 4)
        checks.append(
            IdentityCheck(
                question="母亲或家中主要照料者，未必是家里主要财务支柱，但你们之间是否长期带着情绪牵连、照料负担或隐性的责任感？",
                reason=f"第 4 宫主 {fourth_lord} 落在第 {_planet_house(chart, fourth_lord)} 宫，用于核验家宅与母缘主题。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            )
        )
    if 5 in requested_chapters:
        fifth_lord = _house_lord(chart, 5)
        checks.append(
            IdentityCheck(
                question="你的创造力、教学表达、内容输出或对子女/传承的想象，是否比表面看起来更需要长期稳定培养？",
                reason=f"第 5 宫主 {fifth_lord} 落在第 {_planet_house(chart, fifth_lord)} 宫，用于核验创造力、子女与传承主题。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            )
        )
    if 6 in requested_chapters:
        sixth_lord = _house_lord(chart, 6)
        checks.append(
            IdentityCheck(
                question="你是否越在压力、竞争、债务、健康管理或复杂问题处理中，越能练出真正的专业能力？",
                reason=f"第 6 宫主 {sixth_lord} 落在第 {_planet_house(chart, sixth_lord)} 宫，用于核验阻碍、疾病、债务和敌对主题。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            )
        )
    if 7 in requested_chapters:
        seventh_lord = _house_lord(chart, 7)
        checks.append(
            IdentityCheck(
                question="关系里你是不是很难接受纯轻松型伴侣，更看重深度、可靠度和一起面对现实的能力？",
                reason=f"第 7 宫主 {seventh_lord} 与金星所在宫位组合，适合用来核验婚恋样式。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            )
        )
    if 8 in requested_chapters:
        eighth_lord = _house_lord(chart, 8)
        checks.append(
            IdentityCheck(
                question="你的人生是否有几次明显的断裂、危机、心理重组或共享资源压力，反而逼你升级？",
                reason=f"第 8 宫主 {eighth_lord} 落在第 {_planet_house(chart, eighth_lord)} 宫，用于核验危机、寿元边界和转化主题。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            )
        )
    if 9 in requested_chapters:
        ninth_lord = _house_lord(chart, 9)
        checks.append(
            IdentityCheck(
                question="父辈、导师、信念体系、远行或宗教/哲学主题，是否会周期性改变你的方向感？",
                reason=f"第 9 宫主 {ninth_lord} 落在第 {_planet_house(chart, ninth_lord)} 宫，用于核验父缘、福德、导师与远行。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            )
        )
    if 10 in requested_chapters or ThemePack.CAREER in requested_theme_packs:
        tenth_lord = _house_lord(chart, 10)
        checks.append(
            IdentityCheck(
                question="职业前期是否试错较多，但真正起势反而来自长期积累，而不是一次性的爆发机会？",
                reason=f"第 10 宫主 {tenth_lord} 与土星所在宫位强调长期职责线，用于核验事业版本。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            )
        )
    if 11 in requested_chapters:
        eleventh_lord = _house_lord(chart, 11)
        checks.append(
            IdentityCheck(
                question="你的机会和收益是否更依赖平台、圈层、长期合作和复利网络，而不是单点爆发？",
                reason=f"第 11 宫主 {eleventh_lord} 落在第 {_planet_house(chart, eleventh_lord)} 宫，用于核验收益、机会与社群扩张。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            )
        )
    if ThemePack.WEALTH in requested_theme_packs:
        second_lord = _house_lord(chart, 2)
        eleventh_lord = _house_lord(chart, 11)
        checks.append(
            IdentityCheck(
                question="你赚钱的主要方式是否更像技能沉淀、结构化合作或长期资源盘，而不是短期投机？",
                reason=f"第 2 宫主 {second_lord} 与第 11 宫主 {eleventh_lord} 决定财富兑现方式。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            )
        )
    if 12 in requested_chapters or ThemePack.SPIRITUALITY in requested_theme_packs:
        twelfth_lord = _house_lord(chart, 12)
        checks.append(
            IdentityCheck(
                question="你的人生里是否反复出现外地、迁移、隐退、睡眠波动或想离开熟悉圈层重新开始的周期？",
                reason=f"第 12 宫主 {twelfth_lord} 与罗喉/计都落宫适合核验迁移与灵性线。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            )
        )
    if 13 in requested_chapters:
        checks.append(
            IdentityCheck(
                question="你是否反复遇到某类相似的人、关系模式或心理课题，像是同一类功课换形式回来？",
                reason="第 13 章只作为业力主题映射，不等同于已经读到真实叶片中的前世叙事。",
                evidence_tag=EvidenceTag.REQUIRES_CORPUS,
            )
        )
    if 14 in requested_chapters:
        checks.append(
            IdentityCheck(
                question="你是否发现稳定修法、规律生活和长期纪律，比一次性强烈仪式更能改变你的状态？",
                reason="第 14 章涉及 Deeksha 与护持，当前只能给纪律化实践建议，不能承诺神秘保护。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            )
        )
    if 15 in requested_chapters:
        checks.append(
            IdentityCheck(
                question="身体层面是否容易在长期压力、睡眠、消化、炎症或慢性疲劳上给你提醒？若有症状，应以专业医疗为准。",
                reason="第 15 章涉及 Aushadha，当前只能做身心能量倾向提示，不能给药方或诊断。",
                evidence_tag=EvidenceTag.REQUIRES_CORPUS,
            )
        )
    if 16 in requested_chapters:
        checks.append(
            IdentityCheck(
                question="当前大运/分运对应的主题，是否正在通过事业、关系、财务、迁移或内在状态明显变成现实事件？",
                reason="第 16 章按 Dasa-Bukthi 做时间预测，必须结合当前和下一阶段大运分运核验。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            )
        )
    return checks


def _build_kandam(chart: dict, kandam: int) -> KandamReading:
    if kandam == 1:
        lagna = chart["chart_summary"]["lagna"]
        lagna_lord = chart["chart_summary"]["lagna_lord"]
        lagna_lord_house = _planet_house(chart, lagna_lord)
        moon_house = chart["chart_summary"]["moon_house_from_lagna"]
        summary = (
            f"{lagna} 上升把人生主轴放在“{describe_house(lagna_lord_house)}”上，"
            f"内在安全感则被月亮所在的第 {moon_house} 宫持续牵动。"
        )
        claims = [
            KandamClaim(
                text=f"命盘总主轴由上升主 {lagna_lord} 落第 {lagna_lord_house} 宫主导，人生重要转折通常围绕 {describe_house(lagna_lord_house)} 展开。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"月亮落第 {moon_house} 宫，说明你的情绪与安全感并不完全轻松，往往会与 {describe_house(moon_house)} 强绑定。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
            KandamClaim(
                text=f"当前大运走 {chart['chart_summary']['current_mahadasha']}，身份层面的课题更容易被现实事件直接推到台前。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 2:
        second_lord = _house_lord(chart, 2)
        second_lord_house = _planet_house(chart, second_lord)
        mercury_house = _planet_house(chart, "Mercury")
        jupiter_house = _planet_house(chart, "Jupiter")
        summary = (
            f"第 2 章看财富、家庭、教育和表达。第 2 宫主 {second_lord} 落第 {second_lord_house} 宫，"
            f"当前 {chart['chart_summary']['current_mahadasha']} 大运会把金钱、表达和价值积累拉到现实检验中。"
        )
        claims = [
            KandamClaim(
                text=f"第 2 宫主 {second_lord} 落第 {second_lord_house} 宫，财富路径会借由 {describe_house(second_lord_house)} 被塑形。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"水星落第 {mercury_house} 宫，教育、表达、写作、沟通、交易和信息整理会影响收入能力。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"木星落第 {jupiter_house} 宫，长期财富不是只看现金，而要看认知、信誉、资源放大和可持续合作。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 3:
        third_lord = _house_lord(chart, 3)
        third_lord_house = _planet_house(chart, third_lord)
        mars_house = _planet_house(chart, "Mars")
        mercury_house = _planet_house(chart, "Mercury")
        summary = (
            f"第 3 章看兄弟姐妹、胆识、技能、耳朵、短途移动和主动开路能力。"
            f"第 3 宫主 {third_lord} 落第 {third_lord_house} 宫，当前大运会检验你的行动与输出能力。"
        )
        claims = [
            KandamClaim(
                text=f"第 3 宫主 {third_lord} 落第 {third_lord_house} 宫，同辈关系、兄弟姐妹和协作关系会被 {describe_house(third_lord_house)} 牵动。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"火星落第 {mars_house} 宫，决定你如何用行动力、切断力和竞争心推进事情。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"水星落第 {mercury_house} 宫，说明技能、表达、训练和日常输出是打开这章的关键。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 4:
        fourth_lord = _house_lord(chart, 4)
        fourth_lord_house = _planet_house(chart, fourth_lord)
        moon_house = _planet_house(chart, "Moon")
        stable = fourth_lord_house in KENDRA_HOUSES | TRIKONA_HOUSES
        summary = (
            f"第 4 宫由 {fourth_lord} 主导，且它落在第 {fourth_lord_house} 宫，"
            f"{'家宅基础相对可稳住' if stable else '家宅主题带着明显的责任、变动或距离感'}。"
        )
        claims = [
            KandamClaim(
                text=f"第 4 宫主 {fourth_lord} 落第 {fourth_lord_house} 宫，家与母缘不会只是背景，而会直接影响你的人生决策。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"月亮落第 {moon_house} 宫，说明你需要通过调整居住环境、休息和情绪节律，才能真正稳定内在状态。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
            KandamClaim(
                text=f"如果家中长期存在责任分配不均、情绪压抑或空间迁动，这条线和第 4 宫配置是吻合的。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 5:
        fifth_lord = _house_lord(chart, 5)
        fifth_lord_house = _planet_house(chart, fifth_lord)
        jupiter_house = _planet_house(chart, "Jupiter")
        venus_house = _planet_house(chart, "Venus")
        summary = (
            f"第 5 章看子女、创造力、学习成果、恋爱、心智表达和传承。"
            f"第 5 宫主 {fifth_lord} 落第 {fifth_lord_house} 宫，当前大运会让创造与传承主题更具体化。"
        )
        claims = [
            KandamClaim(
                text=f"第 5 宫主 {fifth_lord} 落第 {fifth_lord_house} 宫，创造力和子女/传承线会通过 {describe_house(fifth_lord_house)} 显现。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"木星落第 {jupiter_house} 宫，是判断后代、教育、信念与传承质量的重要辅助信号。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"金星落第 {venus_house} 宫，恋爱、审美、作品和价值交换会影响第 5 章的实际表达。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 6:
        sixth_lord = _house_lord(chart, 6)
        sixth_lord_house = _planet_house(chart, sixth_lord)
        saturn_house = _planet_house(chart, "Saturn")
        mars_house = _planet_house(chart, "Mars")
        summary = (
            f"第 6 章看疾病、债务、敌人、诉讼、竞争和日常阻碍。"
            f"第 6 宫主 {sixth_lord} 落第 {sixth_lord_house} 宫，当前大运适合把问题处理能力制度化。"
        )
        claims = [
            KandamClaim(
                text=f"第 6 宫主 {sixth_lord} 落第 {sixth_lord_house} 宫，疾病、债务、竞争或服务压力会通过 {describe_house(sixth_lord_house)} 呈现。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"土星落第 {saturn_house} 宫，说明长期纪律、边界、作息和责任结构是化解第 6 章问题的关键。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"火星落第 {mars_house} 宫，提醒你处理冲突时要避免一时切断、硬碰硬或把压力压进身体；具体疾病和诉讼不能只凭本系统定论。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 7:
        seventh_lord = _house_lord(chart, 7)
        seventh_lord_house = _planet_house(chart, seventh_lord)
        venus_house = _planet_house(chart, "Venus")
        navamsa_venus = chart["vargas"]["navamsa"]["venus_sign"]
        relationship_intense = seventh_lord_house in DUSTHANA_HOUSES or venus_house in DUSTHANA_HOUSES
        summary = (
            f"关系线由第 7 宫主 {seventh_lord} 与金星共同主导，"
            f"{'更像深度绑定与转化课题' if relationship_intense else '更像成熟合作与共同建设课题'}。"
        )
        claims = [
            KandamClaim(
                text=f"第 7 宫主 {seventh_lord} 落第 {seventh_lord_house} 宫，说明伴侣关系会把你拉进 {describe_house(seventh_lord_house)} 的现实议题。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"金星落第 {venus_house} 宫，亲密关系不只是浪漫需求，也会直接影响你的价值感与人生秩序。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"Navamsa 金星落在 {navamsa_venus}，说明真正长期关系更看重精神契合、价值观与共同修炼，而不只是即时吸引。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 8:
        eighth_lord = _house_lord(chart, 8)
        eighth_lord_house = _planet_house(chart, eighth_lord)
        saturn_house = _planet_house(chart, "Saturn")
        ketu_house = _planet_house(chart, "Ketu")
        summary = (
            f"第 8 章看寿元、事故、风险、慢性问题、共享资源和深层转化。"
            f"第 8 宫主 {eighth_lord} 落第 {eighth_lord_house} 宫；本系统只做风险主题提示，不预测死亡日期。"
        )
        claims = [
            KandamClaim(
                text=f"第 8 宫主 {eighth_lord} 落第 {eighth_lord_house} 宫，危机、共享资源和心理重组会经由 {describe_house(eighth_lord_house)} 触发。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"土星落第 {saturn_house} 宫，说明慢性压力、长期责任和结构性延迟需要被纳入风险管理。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"计都落第 {ketu_house} 宫，增强抽离、旧业和断裂感；寿元、事故、死亡时间必须保留人工伦理边界，不能由当前 skill 断言。",
                evidence_tag=EvidenceTag.REQUIRES_CORPUS,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 9:
        ninth_lord = _house_lord(chart, 9)
        ninth_lord_house = _planet_house(chart, ninth_lord)
        sun_house = _planet_house(chart, "Sun")
        jupiter_house = _planet_house(chart, "Jupiter")
        summary = (
            f"第 9 章看父亲、福德、信念、宗教、导师、寺庙、远行和上层庇护。"
            f"第 9 宫主 {ninth_lord} 落第 {ninth_lord_house} 宫，当前大运会检验你如何重建信念和方向感。"
        )
        claims = [
            KandamClaim(
                text=f"第 9 宫主 {ninth_lord} 落第 {ninth_lord_house} 宫，父缘、导师、远行和信念主题会通过 {describe_house(ninth_lord_house)} 展开。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"太阳落第 {sun_house} 宫，是判断父辈、权威、使命感和人生方向的重要辅助信号。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"木星落第 {jupiter_house} 宫，说明真正的福德不是单纯好运，而是认知、导师、善行和长期正向选择的累积。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 10:
        tenth_lord = _house_lord(chart, 10)
        tenth_lord_house = _planet_house(chart, tenth_lord)
        saturn_house = _planet_house(chart, "Saturn")
        sun_house = _planet_house(chart, "Sun")
        summary = (
            f"事业线由第 10 宫主 {tenth_lord} 落第 {tenth_lord_house} 宫决定主走向，"
            f"而太阳第 {sun_house} 宫、土星第 {saturn_house} 宫决定你如何承接职责和权威。"
        )
        claims = [
            KandamClaim(
                text=f"第 10 宫主 {tenth_lord} 落第 {tenth_lord_house} 宫，职业不适合完全脱离你的人生主轴，而要围绕 {describe_house(tenth_lord_house)} 做长期积累。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"土星落第 {saturn_house} 宫，职业线更怕急于求成；你的抬升通常来自可复利的结构，而不是一次性运气。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"太阳落第 {sun_house} 宫，说明你需要逐步建立自己的判断权和角色权威，否则事业会一直受外部节奏牵引。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 11:
        eleventh_lord = _house_lord(chart, 11)
        eleventh_lord_house = _planet_house(chart, eleventh_lord)
        second_lord = _house_lord(chart, 2)
        second_lord_house = _planet_house(chart, second_lord)
        venus_house = _planet_house(chart, "Venus")
        summary = (
            f"第 11 章看收益、机会、朋友、平台、欲望兑现、社群和二次关系。"
            f"第 11 宫主 {eleventh_lord} 落第 {eleventh_lord_house} 宫，当前大运会检验资源能否被稳定兑现。"
        )
        claims = [
            KandamClaim(
                text=f"第 11 宫主 {eleventh_lord} 落第 {eleventh_lord_house} 宫，收益与机会会通过 {describe_house(eleventh_lord_house)} 得到或受阻。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"第 2 宫主 {second_lord} 落第 {second_lord_house} 宫，说明收入留存能力必须和家庭资源、表达、现金流秩序一起看。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"金星落第 {venus_house} 宫，社交、合作、客户与价值交换会影响你的收益质量；二次关系线不能只凭当前系统下结论。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam != 12:
        return _build_extended_kandam(chart, kandam)

    twelfth_lord = _house_lord(chart, 12)
    twelfth_lord_house = _planet_house(chart, twelfth_lord)
    rahu_house = _planet_house(chart, "Rahu")
    ketu_house = _planet_house(chart, "Ketu")
    navamsa_ketu = chart["vargas"]["navamsa"]["ketu_sign"]
    summary = (
        f"第 12 宫由 {twelfth_lord} 主导并落在第 {twelfth_lord_house} 宫，"
        "这条线会把迁移、开销、隐退与内在修行放进长期人生课题。"
    )
    claims = [
        KandamClaim(
            text=f"第 12 宫主 {twelfth_lord} 落第 {twelfth_lord_house} 宫，开销与迁移不会只是偶发事件，而会周期性触发人生重组。",
            evidence_tag=EvidenceTag.CLASSICAL_RULE,
        ),
        KandamClaim(
            text=f"Rahu 第 {rahu_house} 宫、Ketu 第 {ketu_house} 宫，使你在现实扩张和内在抽离之间会长期摆荡。",
            evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
        ),
        KandamClaim(
            text=f"Navamsa 的 Ketu 落在 {navamsa_ketu}，灵性成长更适合走稳定实践，而不是情绪化地时断时续。",
            evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
        ),
    ]
    return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)


def _build_extended_kandam(chart: dict, kandam: int) -> KandamReading:
    if kandam == 13:
        fifth_lord = _house_lord(chart, 5)
        eighth_lord = _house_lord(chart, 8)
        twelfth_lord = _house_lord(chart, 12)
        ketu_house = _planet_house(chart, "Ketu")
        summary = (
            f"第 13 章看 Santhi Pariharam：前世业力、重复模式和补救方向。"
            f"当前 {chart['chart_summary']['current_mahadasha']} 大运下，只能把它作为业力主题映射，不能伪装成真实叶片叙事。"
        )
        claims = [
            KandamClaim(
                text=f"第 5 宫主 {fifth_lord}、第 8 宫主 {eighth_lord}、第 12 宫主 {twelfth_lord} 共同用于观察旧模式、深层重组和内在耗损。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
            KandamClaim(
                text=f"计都落第 {ketu_house} 宫，说明抽离、旧业、反复出现的心理主题和切断感是这章的重要入口。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text="具体前世人物、地点、罪业叙事和叶片 verse 必须依赖真实语料库与人工校勘；当前系统只能给可执行的修正方向。",
                evidence_tag=EvidenceTag.REQUIRES_CORPUS,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 14:
        ninth_lord = _house_lord(chart, 9)
        twelfth_lord = _house_lord(chart, 12)
        saturn_house = _planet_house(chart, "Saturn")
        summary = (
            f"第 14 章看 Deeksha、mantra、护持、纪律和精神实践。"
            f"第 9 宫主 {ninth_lord} 与第 12 宫主 {twelfth_lord} 是核心，当前大运要求把修法落到日常结构。"
        )
        claims = [
            KandamClaim(
                text=f"第 9 宫主 {ninth_lord} 用于判断信仰、导师、传统和祝福来源，第 12 宫主 {twelfth_lord} 用于判断退隐、修行和内在消耗。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"土星落第 {saturn_house} 宫，说明稳定频率、纪律和长期实践比一次性强烈仪式更有效。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
            KandamClaim(
                text="具体 mantra、护身符、供养对象和仪轨细节需要真实传承或可信文本来源，当前报告只给原则和实践框架。",
                evidence_tag=EvidenceTag.REQUIRES_CORPUS,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 15:
        sixth_lord = _house_lord(chart, 6)
        eighth_lord = _house_lord(chart, 8)
        moon_house = _planet_house(chart, "Moon")
        saturn_house = _planet_house(chart, "Saturn")
        summary = (
            f"第 15 章看 Aushadha：长期疾病倾向、药物和身心调理。"
            f"第 6/8 宫与月亮、土星是观察点；当前系统不提供诊断、药方或替代医疗建议。"
        )
        claims = [
            KandamClaim(
                text=f"第 6 宫主 {sixth_lord} 和第 8 宫主 {eighth_lord} 用于观察日常病灶、慢性压力、复发问题和风险管理。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"月亮落第 {moon_house} 宫、土星落第 {saturn_house} 宫，说明睡眠、情绪、节律和长期压力管理会影响身体状态。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
            KandamClaim(
                text="真实 Aushadha 章节若涉及草药、处方、剂量或医疗判断，必须交给合格医生或传统医学专业人士复核。",
                evidence_tag=EvidenceTag.REQUIRES_CORPUS,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    if kandam == 16:
        current_dasha = next(item for item in chart["dashas"] if item["status"] == "current" and len(item["lords"]) == 1)
        current_sub = next(item for item in chart["dashas"] if item["status"] == "current" and len(item["lords"]) == 2)
        next_dasha = next(item for item in chart["dashas"] if item["status"] == "next" and len(item["lords"]) == 1)
        summary = (
            f"第 16 章看 Dasa Bukthi：大运、分运和未来事件窗口。"
            f"当前主线是 {current_dasha['label']}，分运是 {current_sub['label']}，下一步进入 {next_dasha['label']}。"
        )
        claims = [
            KandamClaim(
                text=f"{current_dasha['start_date']} - {current_dasha['end_date']} 的 {current_dasha['label']} 是当前人生主运，重点看 {_dasha_rationale(chart, current_dasha['lords'])}。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"{current_sub['start_date']} - {current_sub['end_date']} 的 {current_sub['label']} 是当前分运，适合用来判断季度到年度级事件触发。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            KandamClaim(
                text=f"下一主运 {next_dasha['label']} 会改变人生重心；具体月份级事件需要 transit、prashna、真实语料或长期回看样本继续校准。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return KandamReading(kandam=kandam, title=KANDAM_TITLES[kandam], summary=summary, claims=claims)

    raise ValueError(f"Unsupported Kandam: {kandam}")


def _build_theme_section(chart: dict, theme: ThemePack) -> ThemeSection:
    if theme == ThemePack.CAREER:
        tenth_lord = _house_lord(chart, 10)
        tenth_house = _planet_house(chart, tenth_lord)
        saturn_house = _planet_house(chart, "Saturn")
        summary = (
            f"事业版以第 10 宫主 {tenth_lord} 落第 {tenth_house} 宫为核心，"
            f"辅以土星第 {saturn_house} 宫判断职业结构与长期爬坡方式。"
        )
        claims = [
            ThemeClaim(
                text=f"最强事业解法不是追求最快变现，而是围绕 {describe_house(tenth_house)} 建可复利的专业资产。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            ThemeClaim(
                text="若要创业，最好先把方法论、客户结构或作品集积累到足够稳定，再放大独立性。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
            ThemeClaim(
                text=f"当前 {chart['chart_summary']['current_mahadasha']} 大运期间，职业判断要更重视方向校准，而不是只盯短期绩效。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return ThemeSection(theme=theme, summary=summary, claims=claims)

    if theme == ThemePack.WEALTH:
        second_lord = _house_lord(chart, 2)
        eleventh_lord = _house_lord(chart, 11)
        jupiter_house = _planet_house(chart, "Jupiter")
        summary = (
            f"财富版以第 2 宫主 {second_lord}、第 11 宫主 {eleventh_lord} 与木星第 {jupiter_house} 宫联动为核心。"
        )
        claims = [
            ThemeClaim(
                text=f"财富增长更像“把资源慢慢做厚”，适合走长期客户、复购、技能溢价或持续收入结构。",
                evidence_tag=EvidenceTag.CLASSICAL_RULE,
            ),
            ThemeClaim(
                text=f"木星落第 {jupiter_house} 宫，说明金钱与机会往往通过认知升级、关系网络或专业可信度进来。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
            ThemeClaim(
                text="不建议把高波动、高杠杆当成主轴；这张盘更需要可记录、可累积、可回收的财富路径。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            ),
        ]
        return ThemeSection(theme=theme, summary=summary, claims=claims)

    ninth_lord = _house_lord(chart, 9)
    twelfth_lord = _house_lord(chart, 12)
    ketu_house = _planet_house(chart, "Ketu")
    navamsa_lagna = chart["vargas"]["navamsa"]["lagna"]
    summary = (
        f"灵性版以第 9 宫主 {ninth_lord}、第 12 宫主 {twelfth_lord} 与计都第 {ketu_house} 宫为主，"
        f"Navamsa 上升 {navamsa_lagna} 用来判断修行路径的成熟度。"
    )
    claims = [
        ThemeClaim(
            text="灵性成长不适合完全脱离现实生活；真正稳定的路径，是把修行、纪律与现实责任同时安放好。",
            evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
        ),
        ThemeClaim(
            text=f"第 12 宫与 Ketu 被强调时，梦境、独处、抽离感、迁移冲动都可能成为重要的内在信号。",
            evidence_tag=EvidenceTag.CLASSICAL_RULE,
        ),
        ThemeClaim(
            text=f"Navamsa 上升 {navamsa_lagna} 说明灵性并不是逃避现实，而是要求你把关系、价值观和行动统一起来。",
            evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
        ),
    ]
    return ThemeSection(theme=theme, summary=summary, claims=claims)


def _build_timing_windows(chart: dict) -> list[TimingWindow]:
    windows: list[TimingWindow] = []
    for dasha in chart["dashas"]:
        if dasha["status"] not in {"current", "next"}:
            continue
        if dasha["end_date"] is None:
            continue
        windows.append(
            TimingWindow(
                label=f"{dasha['start_date']} - {dasha['end_date']} | {dasha['label']}",
                rationale=_dasha_rationale(chart, dasha["lords"]),
                confidence_note=_timing_confidence_note(chart),
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            )
        )
    return windows[:3]


def _build_remedies(chart: dict, requested_theme_packs: Iterable[ThemePack]) -> list[str]:
    current_mahadasha = chart["chart_summary"]["current_mahadasha"]
    remedies = [
        f"以 {current_mahadasha} 大运为主线做 90 天周期复盘，记录事业、关系与情绪变化，不靠即时感觉下结论。",
        "优先建立稳定作息、睡眠和空间整理习惯，尤其在月亮与第 4/12 宫被触动时，这会直接改善判断质量。",
        "任何 mantra、供养、祈福或修法都只作为辅助，不替代现实决策、医疗建议和财务判断。",
    ]
    if ThemePack.CAREER in requested_theme_packs:
        remedies.append("事业上优先做可复利积累：作品、方法论、长期客户与可复用流程。")
    if ThemePack.WEALTH in requested_theme_packs:
        remedies.append("财富上优先做现金流与储备，不把投机收益当主规划。")
    if ThemePack.SPIRITUALITY in requested_theme_packs:
        remedies.append("灵性上更适合固定频次的静坐、书写或诵念，而不是情绪上来才临时修一下。")
    return remedies


def _dasha_rationale(chart: dict, lords: list[str]) -> str:
    parts = []
    for lord in lords:
        house = _planet_house(chart, lord)
        parts.append(f"{lord} 落第 {house} 宫，主打 {describe_house(house)}")
    return "；".join(parts)


def _timing_confidence_note(chart: dict) -> str:
    warnings = chart["input_quality"]["warnings"]
    if warnings:
        return "；".join(warnings)
    return "当前出生时间已到分钟级，窗口可用于年度到季度级判断。"


def _planet_house(chart: dict, planet_name: str) -> int:
    for planet in chart["planets"]:
        if planet["name"] == planet_name:
            return int(planet["house_from_lagna"])
    raise KeyError(f"Planet not found: {planet_name}")


def _house_lord(chart: dict, house_number: int) -> str:
    lagna = chart["chart_summary"]["lagna"]
    sign_name = house_sign_name(lagna, house_number)
    return sign_lord_name(sign_name)
