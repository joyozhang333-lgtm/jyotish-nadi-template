from __future__ import annotations

from typing import Any


FORBIDDEN_BOUNDARY_PHRASES = (
    "真实叶片已经找到",
    "已找到你的叶片",
    "真实纳迪认证",
    "指纹已匹配叶片",
)
ACCURACY_PROFILE_WEIGHTS = {
    "chart_calculation_accuracy": 0.45,
    "interpretation_traceability": 0.25,
    "empirical_validation_maturity": 0.30,
}


def score_product_quality(
    chart: dict[str, Any],
    reading: dict[str, Any],
    cross_validation: dict[str, Any] | None = None,
    corpus_case: dict[str, Any] | None = None,
) -> dict[str, Any]:
    dimensions = [
        _score_chart_correctness(chart, cross_validation, corpus_case),
        _score_chapter_completeness(reading),
        _score_interpretation_consistency(chart, reading),
        _score_boundary_discipline(reading),
        _score_evidence_and_review_readiness(reading, cross_validation, corpus_case),
    ]
    total = sum(item["score"] for item in dimensions)
    return {
        "total_score": total,
        "max_score": 100,
        "dimensions": dimensions,
        "grade": _grade(total),
    }


def score_accuracy_profile(
    chart: dict[str, Any],
    reading: dict[str, Any],
    cross_validation: dict[str, Any] | None = None,
    corpus_case: dict[str, Any] | None = None,
) -> dict[str, Any]:
    dimensions = [
        _score_chart_calculation_accuracy(chart, cross_validation, corpus_case),
        _score_interpretation_traceability(chart, reading),
        _score_empirical_validation_maturity(chart, cross_validation, corpus_case),
    ]
    weighted_total = sum(
        item["score"] * ACCURACY_PROFILE_WEIGHTS[item["id"]]
        for item in dimensions
    )
    total = int(round(weighted_total))
    return {
        "total_score": total,
        "max_score": 100,
        "dimensions": dimensions,
        "grade": _grade(total),
        "claim_boundary": _accuracy_claim_boundary(total),
    }


def score_feedback_alignment(feedback_profile: dict[str, Any] | None) -> dict[str, Any]:
    if not feedback_profile:
        return {
            "total_score": None,
            "max_score": 100,
            "sample_count": 0,
            "grade": "N/A",
            "claim_boundary": "还没有用户反馈样本，不能评估实际贴合度。",
            "rating_counts": {},
        }

    weights = {
        "准": 1.0,
        "true": 1.0,
        "correct": 1.0,
        "半准": 0.5,
        "partial": 0.5,
        "half_true": 0.5,
        "有启发但不确定": 0.4,
        "uncertain": 0.4,
        "不准": 0.0,
        "false": 0.0,
        "incorrect": 0.0,
    }
    checks = feedback_profile.get("checks", [])
    if not checks:
        return {
            "total_score": None,
            "max_score": 100,
            "sample_count": 0,
            "grade": "N/A",
            "claim_boundary": "反馈文件没有可评分 checks。",
            "rating_counts": {},
        }

    total = 0.0
    rated_count = 0
    rating_counts: dict[str, int] = {}
    for item in checks:
        rating = str(item.get("rating", "")).strip()
        if rating not in weights:
            continue
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
        total += weights[rating]
        rated_count += 1

    if rated_count == 0:
        return {
            "total_score": None,
            "max_score": 100,
            "sample_count": 0,
            "grade": "N/A",
            "claim_boundary": "反馈文件没有可识别的评分标签。",
            "rating_counts": rating_counts,
        }

    score = int(round(total / rated_count * 100))
    return {
        "total_score": score,
        "max_score": 100,
        "sample_count": rated_count,
        "grade": _grade(score),
        "claim_boundary": _feedback_claim_boundary(score, rated_count),
        "rating_counts": rating_counts,
    }


def _score_chart_correctness(
    chart: dict[str, Any],
    cross_validation: dict[str, Any] | None,
    corpus_case: dict[str, Any] | None,
) -> dict[str, Any]:
    score = 12
    notes: list[str] = ["当前没有外部专家复核时，盘面正确性先按结构和交叉验证结果评分。"]
    if cross_validation is not None:
        score = max(0, 20 - (len(cross_validation.get("major_diffs", [])) * 4) - (len(cross_validation.get("minor_diffs", []))))
        notes.append(
            f"多引擎交叉验证得到 {len(cross_validation.get('major_diffs', []))} 个 major diff、"
            f"{len(cross_validation.get('minor_diffs', []))} 个 minor diff。"
        )
    if corpus_case is not None:
        expected = corpus_case.get("expected_chart_summary", {})
        mismatches = 0
        for key, expected_value in expected.items():
            if chart.get("chart_summary", {}).get(key) != expected_value:
                mismatches += 1
        if mismatches:
            score = max(0, score - (mismatches * 2))
            notes.append(f"与样例 case 的 chart_summary 预期有 {mismatches} 个字段不一致。")
        else:
            notes.append("与样例 case 的 chart_summary 预期一致。")
    return _dimension("chart_correctness", "盘面正确性", score, notes)


def _score_chart_calculation_accuracy(
    chart: dict[str, Any],
    cross_validation: dict[str, Any] | None,
    corpus_case: dict[str, Any] | None,
) -> dict[str, Any]:
    score = 72
    notes: list[str] = ["当前分数衡量的是排盘和大运计算的可靠度，不等于最终命理命中率。"]
    if cross_validation is not None:
        major_diffs = len(cross_validation.get("major_diffs", []))
        minor_diffs = len(cross_validation.get("minor_diffs", []))
        score = max(0, 100 - (major_diffs * 15) - (minor_diffs * 2))
        notes.append(
            f"双引擎对比得到 {major_diffs} 个 major diff、{minor_diffs} 个 minor diff。"
        )
        if major_diffs == 0:
            notes.append("关键盘面字段当前没有 major diff。")
    else:
        notes.append("当前没有第二引擎对照，因此只能给保守分。")

    if corpus_case is not None:
        expected = corpus_case.get("expected_chart_summary", {})
        mismatches = 0
        for key, expected_value in expected.items():
            if chart.get("chart_summary", {}).get(key) != expected_value:
                mismatches += 1
        if mismatches:
            score = max(0, score - (mismatches * 5))
            notes.append(f"固定 benchmark case 中有 {mismatches} 个 chart_summary 字段不匹配。")
        else:
            notes.append("固定 benchmark case 的主字段全部匹配。")

    return _dimension_100("chart_calculation_accuracy", "盘面计算准确度", score, notes)


def _score_chapter_completeness(reading: dict[str, Any]) -> dict[str, Any]:
    requested_chapters = reading.get("requested_chapters", [])
    requested_themes = reading.get("requested_theme_packs", [])
    kandams = reading.get("kandam_reading", [])
    themes = reading.get("theme_sections", [])
    score = 20
    notes: list[str] = []

    kandam_map = {item["kandam"]: item for item in kandams}
    for chapter in requested_chapters:
        item = kandam_map.get(chapter)
        if item is None:
            score -= 4
            notes.append(f"Kandam {chapter} 缺失。")
            continue
        if not item.get("summary"):
            score -= 2
            notes.append(f"Kandam {chapter} summary 为空。")
        claims = item.get("claims", [])
        if len(claims) < 2:
            score -= 2
            notes.append(f"Kandam {chapter} claims 数量不足。")
        if any("evidence_tag" not in claim for claim in claims):
            score -= 1
            notes.append(f"Kandam {chapter} 存在未标 evidence_tag 的 claim。")

    theme_map = {item["theme"]: item for item in themes}
    for theme in requested_themes:
        item = theme_map.get(theme)
        if item is None:
            score -= 3
            notes.append(f"专题 {theme} 缺失。")
            continue
        if not item.get("summary"):
            score -= 1
            notes.append(f"专题 {theme} summary 为空。")
        if not item.get("claims"):
            score -= 1
            notes.append(f"专题 {theme} 缺少 claims。")

    if not notes:
        notes.append("请求的章节和专题都已覆盖，且结构字段完整。")
    return _dimension("chapter_completeness", "章节完整度", max(0, score), notes)


def _score_interpretation_consistency(chart: dict[str, Any], reading: dict[str, Any]) -> dict[str, Any]:
    score = 20
    notes: list[str] = []
    if len(reading.get("timing_windows", [])) < 2:
        score -= 4
        notes.append("timing windows 少于 2 个。")
    if len(reading.get("remedy_candidates", [])) < 2:
        score -= 3
        notes.append("remedy 候选过少。")
    if len(reading.get("identity_checks", [])) < 3:
        score -= 3
        notes.append("身份核验问题数量不足。")
    current_mahadasha = chart.get("chart_summary", {}).get("current_mahadasha")
    kandam_text = " ".join(item.get("summary", "") for item in reading.get("kandam_reading", []))
    if current_mahadasha and current_mahadasha not in kandam_text:
        score -= 2
        notes.append("章节摘要没有明显引用当前大运上下文。")
    if not notes:
        notes.append("章节、时间窗口和 remedy 之间没有发现明显结构缺口。")
    return _dimension("interpretation_consistency", "解释一致性", max(0, score), notes)


def _score_interpretation_traceability(chart: dict[str, Any], reading: dict[str, Any]) -> dict[str, Any]:
    score = 100
    notes: list[str] = ["当前分数衡量的是解读是否完整、可追溯、前后一致，不等于真实人生事件命中率。"]

    requested_chapters = reading.get("requested_chapters", [])
    requested_themes = reading.get("requested_theme_packs", [])
    kandams = reading.get("kandam_reading", [])
    themes = reading.get("theme_sections", [])
    kandam_map = {item["kandam"]: item for item in kandams}
    theme_map = {item["theme"]: item for item in themes}

    for chapter in requested_chapters:
        item = kandam_map.get(chapter)
        if item is None:
            score -= 10
            notes.append(f"Kandam {chapter} 缺失。")
            continue
        if not item.get("summary"):
            score -= 5
            notes.append(f"Kandam {chapter} summary 为空。")
        claims = item.get("claims", [])
        if len(claims) < 2:
            score -= 5
            notes.append(f"Kandam {chapter} claims 少于 2 条。")
        if any("evidence_tag" not in claim for claim in claims):
            score -= 3
            notes.append(f"Kandam {chapter} 存在缺少 evidence_tag 的 claim。")

    for theme in requested_themes:
        item = theme_map.get(theme)
        if item is None:
            score -= 8
            notes.append(f"专题 {theme} 缺失。")
            continue
        if not item.get("summary"):
            score -= 3
            notes.append(f"专题 {theme} summary 为空。")
        if not item.get("claims"):
            score -= 3
            notes.append(f"专题 {theme} 缺少 claims。")

    if len(reading.get("identity_checks", [])) < 3:
        score -= 8
        notes.append("身份核验问题数量不足。")
    if len(reading.get("timing_windows", [])) < 2:
        score -= 8
        notes.append("timing windows 少于 2 个。")
    if len(reading.get("remedy_candidates", [])) < 2:
        score -= 6
        notes.append("remedy 候选少于 2 个。")

    tag_ratio = _evidence_tag_ratio(reading)
    if tag_ratio < 1.0:
        penalty = int(round((1.0 - tag_ratio) * 20))
        score -= penalty
        notes.append(f"evidence_tag 覆盖率不是 100%，当前为 {tag_ratio:.0%}。")

    current_mahadasha = chart.get("chart_summary", {}).get("current_mahadasha")
    kandam_text = " ".join(item.get("summary", "") for item in reading.get("kandam_reading", []))
    if current_mahadasha and current_mahadasha not in kandam_text:
        score -= 4
        notes.append("章节摘要没有明显引用当前大运上下文。")

    if len(notes) == 1:
        notes.append("当前章节、专题、时间窗口、evidence tag 和大运上下文基本一致。")
    return _dimension_100("interpretation_traceability", "解读可追溯性", max(0, score), notes)


def _score_boundary_discipline(reading: dict[str, Any]) -> dict[str, Any]:
    score = 20
    notes: list[str] = []
    combined_text_parts = []
    for kandam in reading.get("kandam_reading", []):
        combined_text_parts.append(kandam.get("summary", ""))
        combined_text_parts.extend(claim.get("text", "") for claim in kandam.get("claims", []))
    for theme in reading.get("theme_sections", []):
        combined_text_parts.append(theme.get("summary", ""))
        combined_text_parts.extend(claim.get("text", "") for claim in theme.get("claims", []))
    if reading.get("fingerprint_reading"):
        combined_text_parts.append(reading["fingerprint_reading"].get("note", ""))
    combined_text_parts.extend(reading.get("missing_capabilities", []))
    combined_text = " ".join(combined_text_parts)

    if "真实叶片" not in combined_text:
        score -= 5
        notes.append("输出没有清楚暴露真实叶片语料缺口。")
    if reading.get("fingerprint_reading") and "指纹" not in combined_text:
        score -= 3
        notes.append("输出没有清楚暴露指纹模块边界。")
    for phrase in FORBIDDEN_BOUNDARY_PHRASES:
        if phrase in combined_text:
            score -= 8
            notes.append(f"发现越界表达：{phrase}")
    if not notes:
        notes.append("边界表达清楚，没有发现把 skill 包装成真实找叶系统的表述。")
    return _dimension("boundary_discipline", "产品边界纪律", max(0, score), notes)


def _score_evidence_and_review_readiness(
    reading: dict[str, Any],
    cross_validation: dict[str, Any] | None,
    corpus_case: dict[str, Any] | None,
) -> dict[str, Any]:
    tag_ratio = _evidence_tag_ratio(reading)
    score = int(round(tag_ratio * 12))
    notes = [f"evidence_tag 覆盖率为 {tag_ratio:.0%}。"]
    if cross_validation is not None:
        score += 4
        notes.append("已接入多引擎交叉验证。")
    if corpus_case is not None:
        score += 4
        notes.append("已接入样例 case 评测。")
    else:
        notes.append("真实语料评测目前还是框架和样例阶段。")
    return _dimension("evidence_and_review_readiness", "证据与评测准备度", min(20, score), notes)


def _score_empirical_validation_maturity(
    chart: dict[str, Any],
    cross_validation: dict[str, Any] | None,
    corpus_case: dict[str, Any] | None,
) -> dict[str, Any]:
    score = 0
    notes: list[str] = ["这个分数衡量的是你能不能对外声称“命理准确度很高”，而不是排盘引擎本身跑得多稳。"]

    if cross_validation is not None:
        score += 20
        notes.append("已接入第二引擎交叉验证。")
        if len(cross_validation.get("major_diffs", [])) == 0:
            score += 10
            notes.append("当前 benchmark 没有 major diff。")

    if corpus_case is not None:
        score += 10
        notes.append("已接入固定 benchmark case。")
        expected = corpus_case.get("expected_chart_summary", {})
        matched = 0
        for key, expected_value in expected.items():
            if chart.get("chart_summary", {}).get(key) == expected_value:
                matched += 1
        if expected:
            score += int(round((matched / len(expected)) * 5))
            notes.append(f"固定 case 主字段匹配 {matched}/{len(expected)}。")

        validation_meta = corpus_case.get("validation_meta", {})
        benchmark_case_count = int(validation_meta.get("benchmark_case_count", 1))
        expert_review_count = int(validation_meta.get("expert_review_count", 0))
        longitudinal_follow_up_count = int(validation_meta.get("longitudinal_follow_up_count", 0))
        score += int(round(min(benchmark_case_count, 20) / 20 * 15))
        score += int(round(min(expert_review_count, 10) / 10 * 20))
        score += int(round(min(longitudinal_follow_up_count, 10) / 10 * 20))

        if benchmark_case_count < 20:
            notes.append(f"benchmark case 只有 {benchmark_case_count} 个，离 20 个样例的目标还远。")
        if expert_review_count == 0:
            notes.append("还没有专家复核样本。")
        if longitudinal_follow_up_count == 0:
            notes.append("还没有长期回看样本。")
    else:
        notes.append("当前还没有 case 级验证元数据。")

    return _dimension_100("empirical_validation_maturity", "实证验证成熟度", min(100, score), notes)


def _dimension(identifier: str, title: str, score: int, notes: list[str]) -> dict[str, Any]:
    return {
        "id": identifier,
        "title": title,
        "score": int(score),
        "max_score": 20,
        "notes": notes,
    }


def _dimension_100(identifier: str, title: str, score: int, notes: list[str]) -> dict[str, Any]:
    return {
        "id": identifier,
        "title": title,
        "score": int(score),
        "max_score": 100,
        "notes": notes,
    }


def _evidence_tag_ratio(reading: dict[str, Any]) -> float:
    tagged_items = 0
    total_items = 0
    for check in reading.get("identity_checks", []):
        total_items += 1
        if check.get("evidence_tag"):
            tagged_items += 1
    for kandam in reading.get("kandam_reading", []):
        for claim in kandam.get("claims", []):
            total_items += 1
            if claim.get("evidence_tag"):
                tagged_items += 1
    for theme in reading.get("theme_sections", []):
        for claim in theme.get("claims", []):
            total_items += 1
            if claim.get("evidence_tag"):
                tagged_items += 1
    for window in reading.get("timing_windows", []):
        total_items += 1
        if window.get("evidence_tag"):
            tagged_items += 1
    return 1.0 if total_items == 0 else tagged_items / total_items


def _grade(total_score: int) -> str:
    if total_score >= 95:
        return "A+"
    if total_score >= 88:
        return "A"
    if total_score >= 80:
        return "B"
    if total_score >= 70:
        return "C"
    return "D"


def _accuracy_claim_boundary(total_score: int) -> str:
    if total_score >= 95:
        return "可以对外表述为高成熟度命理评测系统，但仍不能包装成真实纳迪叶匹配。"
    if total_score >= 88:
        return "可以对外强调盘面可靠和解读稳定，但还不应宣称 95% 以上真实命中率。"
    if total_score >= 80:
        return "当前更适合表述为专业研究型解读系统，而不是高准确率已验证产品。"
    return "当前只能表述为研发中产品，分数主要反映工程和结构质量。"


def _feedback_claim_boundary(total_score: int, sample_count: int) -> str:
    if sample_count < 20:
        return (
            f"当前只有 {sample_count} 条用户反馈，可用于个人校准，不能声称总体准确率。"
        )
    if total_score >= 95:
        return "反馈样本已达到高贴合，但仍需专家复核和长期回看后才能对外声明。"
    if total_score >= 80:
        return "反馈样本显示方向有效，但仍有半准或不确定项，需要继续收敛表达。"
    return "反馈样本显示贴合度不足，需要重新评估规则和叙事。"
