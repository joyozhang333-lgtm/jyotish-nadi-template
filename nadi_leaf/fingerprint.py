from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage import measure

from .models import EvidenceTag, FingerprintReading

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".heic"}
BLOCK_SIZE = 16
MIN_CLASSIFIABLE_QUALITY = 0.2


def assess_fingerprint(image_path: str | None) -> FingerprintReading | None:
    if not image_path:
        return None

    path = Path(image_path).expanduser()
    if not path.exists():
        return FingerprintReading(
            image_quality="missing",
            classification="unavailable",
            confidence=None,
            method="orientation-field-singularity-v1",
            detected_cores=0,
            detected_deltas=0,
            note="指纹图片路径不存在，当前版本无法做图片质量判断或探索性分类。",
            evidence_tag=EvidenceTag.REQUIRES_CORPUS,
        )

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return FingerprintReading(
            image_quality="unsupported",
            classification="unavailable",
            confidence=None,
            method="orientation-field-singularity-v1",
            detected_cores=0,
            detected_deltas=0,
            note="当前版本只接受常见图片格式，暂不支持该指纹文件类型。",
            evidence_tag=EvidenceTag.REQUIRES_CORPUS,
        )

    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return FingerprintReading(
            image_quality="unreadable",
            classification="manual_review_required",
            confidence=None,
            method="orientation-field-singularity-v1",
            detected_cores=0,
            detected_deltas=0,
            note="图片无法被当前运行时稳定读取，指纹纹型需要人工复核。",
            evidence_tag=EvidenceTag.REQUIRES_CORPUS,
        )

    return _analyze_fingerprint_image(image)


def _analyze_fingerprint_image(image: np.ndarray) -> FingerprintReading:
    height, width = image.shape[:2]
    shortest = min(width, height)
    image_quality = _classify_image_quality(width, height)

    normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(normalized)
    roi_mask = _estimate_roi_mask(enhanced)
    coverage = float(np.mean(roi_mask)) if roi_mask.size else 0.0
    contrast = float(np.std(enhanced) / 255.0)
    if coverage < 0.1 or contrast < 0.04:
        return FingerprintReading(
            image_quality=image_quality,
            classification="manual_review_required",
            confidence=round(max(coverage, contrast), 2),
            method="orientation-field-singularity-v1",
            detected_cores=0,
            detected_deltas=0,
            note="有效纹线区域过少或对比度过低，当前图像不足以稳定判断 loop / whorl / arch。",
            evidence_tag=EvidenceTag.REQUIRES_CORPUS,
        )

    orientation_field, coherence_field, field_mask = _estimate_orientation_field(enhanced, roi_mask)
    cores, deltas = _detect_singularities(orientation_field, field_mask)
    quality_score = _quality_score(coverage, contrast, coherence_field, field_mask)
    classification, confidence = _classify_pattern_from_singularities(len(cores), len(deltas), quality_score)
    evidence_tag = EvidenceTag.INTERPRETIVE_MAPPING if classification in {"loop", "whorl", "arch"} else EvidenceTag.REQUIRES_CORPUS
    note = (
        f"基于方向场奇点检测得到 {len(cores)} 个 core、{len(deltas)} 个 delta；"
        "这只是自动纹型分类，不等于真实纳迪叶匹配。"
    )
    if quality_score < MIN_CLASSIFIABLE_QUALITY:
        classification = "manual_review_required"
        evidence_tag = EvidenceTag.REQUIRES_CORPUS
        note = "图像质量或方向场一致性偏低，自动分型只可作弱参考，建议人工复核。"

    return FingerprintReading(
        image_quality=image_quality,
        classification=classification,
        confidence=round(confidence, 2),
        method="orientation-field-singularity-v1",
        detected_cores=len(cores),
        detected_deltas=len(deltas),
        note=note,
        evidence_tag=evidence_tag,
    )


def _classify_image_quality(width: int, height: int) -> str:
    shortest = min(width, height)
    if shortest >= 1200:
        return "good"
    if shortest >= 700:
        return "usable"
    return "low"


def _estimate_roi_mask(image: np.ndarray) -> np.ndarray:
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    gx = cv2.Sobel(blurred, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(blurred, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(gx, gy)
    kernel = np.ones((BLOCK_SIZE, BLOCK_SIZE), np.float32) / float(BLOCK_SIZE * BLOCK_SIZE)
    energy = cv2.filter2D(magnitude, -1, kernel)
    threshold = float(np.percentile(energy, 60))
    mask = (energy > threshold).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    labels = measure.label(mask, connectivity=2)
    if labels.max() <= 0:
        return mask.astype(bool)
    props = measure.regionprops(labels)
    largest = max(props, key=lambda prop: prop.area)
    return labels == largest.label


def _estimate_orientation_field(image: np.ndarray, roi_mask: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    gx = cv2.Sobel(image, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(image, cv2.CV_32F, 0, 1, ksize=3)
    rows = image.shape[0] // BLOCK_SIZE
    cols = image.shape[1] // BLOCK_SIZE
    orientation = np.zeros((rows, cols), dtype=np.float32)
    coherence = np.zeros((rows, cols), dtype=np.float32)
    mask = np.zeros((rows, cols), dtype=bool)

    for row in range(rows):
        for col in range(cols):
            r0 = row * BLOCK_SIZE
            r1 = r0 + BLOCK_SIZE
            c0 = col * BLOCK_SIZE
            c1 = c0 + BLOCK_SIZE
            roi_block = roi_mask[r0:r1, c0:c1]
            if np.mean(roi_block) < 0.5:
                continue
            gx_block = gx[r0:r1, c0:c1]
            gy_block = gy[r0:r1, c0:c1]
            v_x = 2.0 * np.sum(gx_block * gy_block)
            v_y = np.sum(gx_block * gx_block - gy_block * gy_block)
            denom = np.sum(gx_block * gx_block + gy_block * gy_block) + 1e-6
            orientation[row, col] = 0.5 * np.arctan2(v_x, v_y)
            coherence[row, col] = np.sqrt(v_x * v_x + v_y * v_y) / denom
            mask[row, col] = True

    smoothed_orientation = _smooth_orientation_field(orientation, mask)
    return smoothed_orientation, coherence, mask


def _smooth_orientation_field(orientation: np.ndarray, mask: np.ndarray) -> np.ndarray:
    cos2 = np.cos(2.0 * orientation) * mask
    sin2 = np.sin(2.0 * orientation) * mask
    smoothed_cos2 = gaussian_filter(cos2, sigma=1.0)
    smoothed_sin2 = gaussian_filter(sin2, sigma=1.0)
    return 0.5 * np.arctan2(smoothed_sin2, smoothed_cos2)


def _detect_singularities(orientation: np.ndarray, mask: np.ndarray) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    cores: list[tuple[int, int]] = []
    deltas: list[tuple[int, int]] = []
    ring_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]

    for row in range(1, orientation.shape[0] - 1):
        for col in range(1, orientation.shape[1] - 1):
            if not mask[row, col]:
                continue
            if not all(mask[row + dr, col + dc] for dr, dc in ring_offsets):
                continue
            neighborhood = [orientation[row + dr, col + dc] for dr, dc in ring_offsets]
            total = 0.0
            for index in range(len(neighborhood)):
                current = neighborhood[index]
                next_value = neighborhood[(index + 1) % len(neighborhood)]
                total += _normalize_orientation_diff(next_value - current)
            poincare_index = total / (2.0 * np.pi)
            if poincare_index > 0.35:
                cores.append((row, col))
            elif poincare_index < -0.35:
                deltas.append((row, col))

    return _dedupe_points(cores), _dedupe_points(deltas)


def _dedupe_points(points: list[tuple[int, int]], min_distance: int = 2) -> list[tuple[int, int]]:
    deduped: list[tuple[int, int]] = []
    for point in points:
        if all(abs(point[0] - other[0]) > min_distance or abs(point[1] - other[1]) > min_distance for other in deduped):
            deduped.append(point)
    return deduped


def _normalize_orientation_diff(value: float) -> float:
    while value > np.pi / 2:
        value -= np.pi
    while value < -np.pi / 2:
        value += np.pi
    return value


def _quality_score(coverage: float, contrast: float, coherence: np.ndarray, mask: np.ndarray) -> float:
    coherence_mean = float(np.mean(coherence[mask])) if np.any(mask) else 0.0
    raw_score = (coverage * 0.35) + (contrast * 0.25) + (coherence_mean * 0.4)
    return float(max(0.0, min(1.0, raw_score)))


def _classify_pattern_from_singularities(core_count: int, delta_count: int, quality_score: float) -> tuple[str, float]:
    if quality_score < MIN_CLASSIFIABLE_QUALITY:
        return "manual_review_required", quality_score
    if core_count >= 2 or delta_count >= 2 or (core_count >= 1 and delta_count >= 2):
        return "whorl", min(0.95, 0.55 + quality_score * 0.35)
    if core_count >= 1 and delta_count >= 1:
        return "loop", min(0.92, 0.5 + quality_score * 0.35)
    if core_count == 0 and delta_count == 0:
        return "arch", min(0.88, 0.45 + quality_score * 0.35)
    return "manual_review_required", max(0.2, quality_score)
