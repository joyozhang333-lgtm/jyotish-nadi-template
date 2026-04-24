from __future__ import annotations

from typing import Any


TRUE_RATINGS = {"true", "准"}
PARTIAL_RATINGS = {"partial", "half_true", "半准"}


def build_guidance_profile(chart: dict[str, Any], feedback_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    feedback_profile = feedback_profile or {}
    validated_anchors = _validated_anchors(feedback_profile)
    current_maha = chart["chart_summary"]["current_mahadasha"]
    current_antara = chart["chart_summary"]["current_antardasha"]

    guidance_items = [
        {
            "priority": 1,
            "title": "把能力从“能做”推进到“稳定交付”",
            "timeframe": _current_antara_window(chart) or "当前分运",
            "why": "事业和财富类判断应优先落到可交付能力、合作质量和复利资产上；当前大运/分运也会提示价值交换和交付质量的主轴。",
            "practice": "把当前能力拆成固定产品、固定流程、固定报价、固定复盘周期，避免只靠状态和灵感交付。",
            "avoid": "避免继续用含糊合作、含糊收费、含糊边界来换短期机会。",
        },
        {
            "priority": 2,
            "title": "把组织和独立之间的拉扯做成双轨结构",
            "timeframe": "2025-2029",
            "why": "如果盘面或反馈显示组织路径与独立路径之间存在拉扯，报告应把重点放在可迁移能力资产，而不是简单给出上班或创业二选一。",
            "practice": "一条轨道保留稳定现金流和现实反馈，另一条轨道沉淀个人方法论、案例库、内容资产或客户池。",
            "avoid": "避免在基础还没稳时用一次性冲动替代结构迁移。",
        },
        {
            "priority": 3,
            "title": "把灵性实践降到可执行频率",
            "timeframe": "持续执行，尤其在抽离感或迁移冲动变强时",
            "why": "当第 9、12 宫或 Ketu 相关线索被强调时，灵性、深层心理、迁移和抽离感需要落到稳定实践，否则容易变成阶段性兴奋或逃离冲动。",
            "practice": "固定书写、静坐、诵念、身体训练、睡眠复盘中的两项，先做 90 天，不频繁换体系。",
            "avoid": "避免把强烈体验误当长期路径，也避免用修行绕开现实责任。",
        },
        {
            "priority": 4,
            "title": "关系筛选看深度和可靠，不主动追求高压",
            "timeframe": "当前及金星大运前期",
            "why": "关系章不应把深度需求误写成高压关系偏好；更稳妥的判断边界是可靠度、现实沟通、边界处理和共建能力。",
            "practice": "看对方是否能谈现实问题、处理边界、共同复盘，而不是只看情绪浓度或精神共鸣。",
            "avoid": "避免把沉重感误判为深度，也避免把轻松感一概判成不可靠。",
        },
        {
            "priority": 5,
            "title": "把家庭财务拆成来源、管理和给付三层",
            "timeframe": "作为后续核验修正项",
            "why": "家宅、父母和家族资源不能写成固定家庭剧本；收入来源、资金管理者、实际给付者和情绪责任必须分别核验。",
            "practice": "以后家宅章按三层写：谁提供主要资源、谁管理资源、谁实际给付或决策；情绪责任另列一层。",
            "avoid": "避免把第 4 宫母亲线、第 9 宫父亲线、第 2 宫家庭财务线混成一句模糊判断。",
        },
    ]

    return {
        "source": "feedback_calibrated_guidance_v1",
        "current_dasha": current_maha,
        "current_antardasha": current_antara,
        "validated_anchors": validated_anchors,
        "guidance_items": guidance_items,
        "precision_rule": "优先放大使用者已验证为准的主题；半准主题只保留方向，不继续扩写成强结论。",
    }


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
