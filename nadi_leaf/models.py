from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class EvidenceTag(str, Enum):
    CLASSICAL_RULE = "classical_rule"
    INTERPRETIVE_MAPPING = "interpretive_mapping"
    REQUIRES_CORPUS = "requires_corpus"


class ThemePack(str, Enum):
    CAREER = "career"
    WEALTH = "wealth"
    SPIRITUALITY = "spirituality"


@dataclass
class InputQuality:
    birth_time_precision: str
    location_precision: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class IdentityCheck:
    question: str
    reason: str
    evidence_tag: EvidenceTag

    def to_dict(self) -> dict:
        data = asdict(self)
        data["evidence_tag"] = self.evidence_tag.value
        return data


@dataclass
class KandamClaim:
    text: str
    evidence_tag: EvidenceTag

    def to_dict(self) -> dict:
        data = asdict(self)
        data["evidence_tag"] = self.evidence_tag.value
        return data


@dataclass
class KandamReading:
    kandam: int
    title: str
    summary: str
    claims: list[KandamClaim] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "kandam": self.kandam,
            "title": self.title,
            "summary": self.summary,
            "claims": [claim.to_dict() for claim in self.claims],
        }


@dataclass
class TimingWindow:
    label: str
    rationale: str
    confidence_note: str
    evidence_tag: EvidenceTag

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "rationale": self.rationale,
            "confidence_note": self.confidence_note,
            "evidence_tag": self.evidence_tag.value,
        }


@dataclass
class ThemeClaim:
    text: str
    evidence_tag: EvidenceTag

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "evidence_tag": self.evidence_tag.value,
        }


@dataclass
class ThemeSection:
    theme: ThemePack
    summary: str
    claims: list[ThemeClaim] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "theme": self.theme.value,
            "summary": self.summary,
            "claims": [claim.to_dict() for claim in self.claims],
        }


@dataclass
class FingerprintReading:
    image_quality: str
    classification: str
    confidence: float | None
    method: str
    detected_cores: int
    detected_deltas: int
    note: str
    evidence_tag: EvidenceTag

    def to_dict(self) -> dict:
        return {
            "image_quality": self.image_quality,
            "classification": self.classification,
            "confidence": self.confidence,
            "method": self.method,
            "detected_cores": self.detected_cores,
            "detected_deltas": self.detected_deltas,
            "note": self.note,
            "evidence_tag": self.evidence_tag.value,
        }


@dataclass
class ReadingBundle:
    input_quality: InputQuality
    chart_summary: dict
    requested_chapters: list[int] = field(default_factory=list)
    requested_theme_packs: list[ThemePack] = field(default_factory=list)
    fingerprint_reading: FingerprintReading | None = None
    identity_checks: list[IdentityCheck] = field(default_factory=list)
    kandam_reading: list[KandamReading] = field(default_factory=list)
    theme_sections: list[ThemeSection] = field(default_factory=list)
    timing_windows: list[TimingWindow] = field(default_factory=list)
    remedy_candidates: list[str] = field(default_factory=list)
    missing_capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "input_quality": self.input_quality.to_dict(),
            "chart_summary": self.chart_summary,
            "requested_chapters": self.requested_chapters,
            "requested_theme_packs": [item.value for item in self.requested_theme_packs],
            "fingerprint_reading": None if self.fingerprint_reading is None else self.fingerprint_reading.to_dict(),
            "identity_checks": [item.to_dict() for item in self.identity_checks],
            "kandam_reading": [item.to_dict() for item in self.kandam_reading],
            "theme_sections": [item.to_dict() for item in self.theme_sections],
            "timing_windows": [item.to_dict() for item in self.timing_windows],
            "remedy_candidates": self.remedy_candidates,
            "missing_capabilities": self.missing_capabilities,
        }
