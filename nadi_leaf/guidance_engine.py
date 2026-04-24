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
            "why": "你已确认事业早期试错、长期积累起势、技能沉淀赚钱这两条判断成立；当前金星大运也把价值交换、合作和交付质量放到主轴。",
            "practice": "把当前能力拆成固定产品、固定流程、固定报价、固定复盘周期，避免只靠状态和灵感交付。",
            "avoid": "避免继续用含糊合作、含糊收费、含糊边界来换短期机会。",
        },
        {
            "priority": 2,
            "title": "把组织和独立之间的拉扯做成双轨结构",
            "timeframe": "2025-2029",
            "why": "你对“组织与独立之间摆荡”有反馈共鸣，这说明事业不是简单选择上班或创业，而是要先建立可迁移的能力资产。",
            "practice": "一条轨道保留稳定现金流和现实反馈，另一条轨道沉淀个人方法论、案例库、内容资产或客户池。",
            "avoid": "避免在基础还没稳时用一次性冲动替代结构迁移。",
        },
        {
            "priority": 3,
            "title": "把灵性实践降到可执行频率",
            "timeframe": "持续执行，尤其在抽离感或迁移冲动变强时",
            "why": "你对灵性、玄学、深层心理、迁移和抽离感的判断有收获；这条线如果没有稳定实践，容易变成阶段性兴奋或逃离冲动。",
            "practice": "固定书写、静坐、诵念、身体训练、睡眠复盘中的两项，先做 90 天，不频繁换体系。",
            "avoid": "避免把强烈体验误当长期路径，也避免用修行绕开现实责任。",
        },
        {
            "priority": 4,
            "title": "关系筛选看深度和可靠，不主动追求高压",
            "timeframe": "当前及金星大运前期",
            "why": "你确认难接受纯轻松型伴侣，但不确定是否会被高责任或高压力的人吸引，所以系统应收窄为深度、可靠度和现实共建能力。",
            "practice": "看对方是否能谈现实问题、处理边界、共同复盘，而不是只看情绪浓度或精神共鸣。",
            "avoid": "避免把沉重感误判为深度，也避免把轻松感一概判成不可靠。",
        },
        {
            "priority": 5,
            "title": "把家庭财务拆成来源、管理和给付三层",
            "timeframe": "作为后续核验修正项",
            "why": "你进一步校准了家庭财务流：父亲是主要收入来源，母亲掌管钱并直接给付，较大的给付会和父亲商量；因此后续报告不能简单说“靠父亲”或“靠母亲”。",
            "practice": "以后家宅章按三层写：父亲负责主要收入来源，母亲负责资金管理和直接给付，父母共同参与重大给付决策；情绪责任另列一层。",
            "avoid": "避免把第 4 宫母亲线、第 9 宫父亲线、第 2 宫家庭财务线混成一句模糊判断。",
        },
    ]

    return {
        "source": "feedback_calibrated_guidance_v1",
        "current_dasha": current_maha,
        "current_antardasha": current_antara,
        "validated_anchors": validated_anchors,
        "guidance_items": guidance_items,
        "precision_rule": "优先放大用户已验证为准的主题；半准主题只保留方向，不继续扩写成强结论。",
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
