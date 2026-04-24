from pathlib import Path

import cv2
import numpy as np

from nadi_leaf.fingerprint import _classify_pattern_from_singularities, assess_fingerprint


def test_classify_pattern_from_singularities_maps_basic_patterns() -> None:
    assert _classify_pattern_from_singularities(1, 1, 0.8)[0] == "loop"
    assert _classify_pattern_from_singularities(2, 2, 0.8)[0] == "whorl"
    assert _classify_pattern_from_singularities(0, 0, 0.8)[0] == "arch"
    assert _classify_pattern_from_singularities(1, 0, 0.1)[0] == "manual_review_required"


def test_assess_fingerprint_handles_missing_path() -> None:
    reading = assess_fingerprint("/tmp/definitely-missing-fingerprint-image.png")
    assert reading is not None
    assert reading.image_quality == "missing"
    assert reading.classification == "unavailable"


def test_assess_fingerprint_smoke_test_with_generated_image(tmp_path: Path) -> None:
    image = np.zeros((512, 512), dtype=np.uint8)
    for y in range(30, 480, 22):
        cv2.ellipse(image, (256, y), (180, 18), 0, 0, 180, 255, 2)
    image_path = tmp_path / "synthetic-loopish.png"
    cv2.imwrite(str(image_path), image)

    reading = assess_fingerprint(str(image_path))

    assert reading is not None
    assert reading.image_quality in {"low", "usable", "good"}
    assert reading.classification in {"arch", "loop", "whorl", "manual_review_required"}
    assert reading.method == "orientation-field-singularity-v1"
