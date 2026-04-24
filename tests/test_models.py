from nadi_leaf.models import (
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


def test_reading_bundle_serialization_uses_string_tags() -> None:
    bundle = ReadingBundle(
        input_quality=InputQuality(
            birth_time_precision="minute",
            location_precision="city",
            warnings=["time zone inferred from city"],
        ),
        chart_summary={
            "lagna": "Virgo",
            "moon_sign": "Capricorn",
            "nakshatra": "Shravana",
        },
        requested_chapters=[1, 10, 12],
        requested_theme_packs=[ThemePack.CAREER, ThemePack.WEALTH],
        fingerprint_reading=FingerprintReading(
            image_quality="good",
            classification="loop",
            confidence=0.72,
            method="orientation-field-singularity-v1",
            detected_cores=1,
            detected_deltas=1,
            note="当前只作为探索性指纹分类，不能视为真实叶片匹配。",
            evidence_tag=EvidenceTag.REQUIRES_CORPUS,
        ),
        identity_checks=[
            IdentityCheck(
                question="父亲在人生中是否是强势或决定性人物？",
                reason="用于验证 9 宫与父缘线索。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            )
        ],
        kandam_reading=[
            KandamReading(
                kandam=10,
                title="事业与职责",
                summary="职业路径以责任、结构和长期积累为核心。",
                claims=[
                    KandamClaim(
                        text="事业发展更像慢热积累，而不是一次性暴冲。",
                        evidence_tag=EvidenceTag.CLASSICAL_RULE,
                    )
                ],
            )
        ],
        theme_sections=[
            ThemeSection(
                theme=ThemePack.CAREER,
                summary="事业发展以稳态积累和角色升级为主。",
                claims=[
                    ThemeClaim(
                        text="适合在结构明确的体系中先积累声望，再决定是否独立发展。",
                        evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
                    )
                ],
            )
        ],
        timing_windows=[
            TimingWindow(
                label="2027-2028 事业转轨窗口",
                rationale="基于 dasha 和职业相关宫位强调。",
                confidence_note="需要精确出生时间以缩窄月份级判断。",
                evidence_tag=EvidenceTag.INTERPRETIVE_MAPPING,
            )
        ],
        remedy_candidates=["规律修行与长期主义职业策略"],
        missing_capabilities=["真实叶片语料库尚未接入"],
    )

    data = bundle.to_dict()

    assert data["requested_chapters"] == [1, 10, 12]
    assert data["requested_theme_packs"] == ["career", "wealth"]
    assert data["fingerprint_reading"]["classification"] == "loop"
    assert data["fingerprint_reading"]["confidence"] == 0.72
    assert data["fingerprint_reading"]["method"] == "orientation-field-singularity-v1"
    assert data["fingerprint_reading"]["detected_cores"] == 1
    assert data["fingerprint_reading"]["detected_deltas"] == 1
    assert data["fingerprint_reading"]["evidence_tag"] == "requires_corpus"
    assert data["identity_checks"][0]["evidence_tag"] == "interpretive_mapping"
    assert data["kandam_reading"][0]["claims"][0]["evidence_tag"] == "classical_rule"
    assert data["theme_sections"][0]["theme"] == "career"
    assert data["theme_sections"][0]["claims"][0]["evidence_tag"] == "interpretive_mapping"
    assert data["timing_windows"][0]["evidence_tag"] == "interpretive_mapping"
    assert data["missing_capabilities"] == ["真实叶片语料库尚未接入"]
