"""Move likely Everdell result-screen images into ``everdell_results``."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher
from io import TextIOWrapper
from itertools import pairwise
from pathlib import Path

import tessdata
from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError
from tesserocr import PSM, PyTessBaseAPI

RESULTS_DIRECTORY = "everdell_results"
SUPPORTED_EXTENSIONS = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}
RESULT_HEADINGS = ("VICTORY", "DEFEAT")
RANK_ALIASES = {
    1: ("1ST", "IST"),
    2: ("2ND", "2NO", "2N0", "2NOD", "QNOD", "JNO"),
    3: ("3RD", "3RO", "3R0", "38RD", "BRO", "SRO", "SRD"),
    4: ("4TH", "4IH", "ATH"),
}
MIN_HEADING_SIMILARITY = 0.8
MIN_RANK_LABELS = 2


@dataclass(frozen=True, slots=True)
class ScreenDetection:
    is_result_screen: bool
    confidence: float
    reason: str


def _normalized_word(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper()).replace("0", "O").replace("1", "I")


def _heading_match(text: str) -> tuple[str, float] | None:
    words = re.findall(r"[A-Z0-9]+", text.upper())
    candidates = words + [left + right for left, right in pairwise(words)]
    matches = [
        (SequenceMatcher(None, _normalized_word(word), heading).ratio(), heading)
        for word in candidates
        if 4 <= len(word) <= 10
        for heading in RESULT_HEADINGS
    ]
    if not matches:
        return None

    similarity, heading = max(matches)
    if similarity < MIN_HEADING_SIMILARITY:
        return None
    return heading, similarity


def _rank_labels(text: str) -> set[int]:
    labels: set[int] = set()
    for word in re.findall(r"[A-Z0-9]+", text.upper()):
        normalized = _normalized_word(word)
        if len(normalized) < 3:
            continue

        for rank, aliases in RANK_ALIASES.items():
            if normalized in aliases or any(
                SequenceMatcher(None, normalized, alias).ratio() >= 0.8
                for alias in aliases
            ):
                labels.add(rank)
                break
    return labels


def _prepare_for_ocr(
    image: Image.Image,
    max_scale: float = 1.5,
    max_dimension: int = 2400,
) -> Image.Image:
    grayscale = ImageOps.autocontrast(image.convert("L"), cutoff=1)
    scale = min(max_scale, max_dimension / max(image.size))
    if scale != 1.0:
        grayscale = grayscale.resize(
            (round(image.width * scale), round(image.height * scale)),
            Image.Resampling.LANCZOS,
        )
    return ImageEnhance.Contrast(grayscale).enhance(1.6)


def _recognize_text(
    image: Image.Image, ocr: PyTessBaseAPI, page_segmentation_mode: PSM
) -> str:
    ocr.SetPageSegMode(page_segmentation_mode)
    ocr.SetImage(image)
    return ocr.GetUTF8Text() or ""


def _detection_from_text(
    text: str, image_width: int, image_height: int
) -> ScreenDetection | None:
    heading = _heading_match(text)
    if heading is None:
        return None

    heading_text, similarity = heading
    rank_count = len(_rank_labels(text))
    confidence = round(0.7 * similarity + 0.3 * min(rank_count / 2, 1.0), 2)
    return ScreenDetection(
        True,
        confidence,
        f"{heading_text} heading and {rank_count} placement labels "
        f"({image_width}x{image_height})",
    )


def classify_image(image: Image.Image, ocr: PyTessBaseAPI) -> ScreenDetection:
    """Find result headings, using placement labels to recover difficult OCR."""
    image_width, image_height = image.size
    prepared_image = _prepare_for_ocr(image)
    first_pass_text = _recognize_text(prepared_image, ocr, PSM.SPARSE_TEXT)
    detection = _detection_from_text(first_pass_text, image_width, image_height)
    if detection is not None:
        return detection

    rank_labels = _rank_labels(first_pass_text)
    if len(rank_labels) < MIN_RANK_LABELS:
        return ScreenDetection(False, 0.0, "VICTORY or DEFEAT heading not found")

    high_resolution_image = _prepare_for_ocr(image, max_scale=3.0, max_dimension=3200)
    recognized_text = [
        first_pass_text,
        _recognize_text(high_resolution_image, ocr, PSM.SPARSE_TEXT),
    ]
    combined_text = "\n".join(recognized_text)
    detection = _detection_from_text(combined_text, image_width, image_height)
    if detection is not None:
        return detection

    recognized_text.append(_recognize_text(high_resolution_image, ocr, PSM.AUTO))
    combined_text = "\n".join(recognized_text)
    detection = _detection_from_text(combined_text, image_width, image_height)
    if detection is not None:
        return detection

    header_and_rows = high_resolution_image.crop(
        (0, 0, high_resolution_image.width, round(high_resolution_image.height * 0.65))
    )
    recognized_text.append(_recognize_text(header_and_rows, ocr, PSM.SPARSE_TEXT))
    combined_text = "\n".join(recognized_text)
    detection = _detection_from_text(combined_text, image_width, image_height)
    if detection is not None:
        return detection

    return ScreenDetection(False, 0.0, "VICTORY or DEFEAT heading not found")


def _load_image(path: Path) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.exif_transpose(source).convert("RGB")


def _iter_images(root: Path, results_directory: Path) -> list[Path]:
    image_paths: list[Path] = []

    def report_walk_error(error: OSError) -> None:
        print(
            f"Warning: could not read directory {error.filename}: {error}",
            file=sys.stderr,
        )

    for current_directory, directory_names, file_names in os.walk(
        root, topdown=True, followlinks=False, onerror=report_walk_error
    ):
        current_path = Path(current_directory)
        directory_names[:] = sorted(
            name
            for name in directory_names
            if (current_path / name) != results_directory
            and not (current_path / name).is_symlink()
        )

        for file_name in sorted(file_names):
            path = current_path / file_name
            if path.suffix.casefold() in SUPPORTED_EXTENSIONS and not path.is_symlink():
                image_paths.append(path)

    return image_paths


def _available_target(directory: Path, source: Path) -> Path:
    candidate = directory / source.name
    counter = 2
    while candidate.exists():
        candidate = directory / f"{source.stem}__{counter}{source.suffix}"
        counter += 1
    return candidate


def filter_images(source_directory: Path) -> tuple[int, int]:
    results_directory = source_directory / RESULTS_DIRECTORY
    results_directory.mkdir(exist_ok=True)

    image_paths = _iter_images(source_directory, results_directory)
    if not image_paths:
        print("No supported images found.")
        return 0, 0

    print(f"Images to process: {len(image_paths)}.")
    matches: list[tuple[Path, ScreenDetection]] = []
    with PyTessBaseAPI(path=tessdata.data_path(), lang="eng", psm=PSM.AUTO) as ocr:
        for path in image_paths:
            try:
                detection = classify_image(_load_image(path), ocr)
            except (
                OSError,
                UnidentifiedImageError,
                Image.DecompressionBombError,
            ) as error:
                print(f"Warning: skipping {path}: {error}", file=sys.stderr)
                continue
            except (RuntimeError, ValueError) as error:
                print(
                    f"Warning: OCR failed for {path}: {error}",
                    file=sys.stderr,
                )
                continue

            if detection.is_result_screen:
                matches.append((path, detection))

    moved_count = 0
    for path, detection in matches:
        target = _available_target(results_directory, path)
        try:
            shutil.move(str(path), str(target))
        except OSError as error:
            print(f"Move failed for {path}: {error}", file=sys.stderr)
            continue

        moved_count += 1
        relative_target = target.relative_to(source_directory)
        print(
            f"Matched ({detection.confidence:.0%}): "
            f"{path.relative_to(source_directory)} -> {relative_target}"
            f" - {detection.reason}"
        )

    print(
        f"Scanned images: {len(image_paths)}; result screenshots found: "
        f"{len(matches)}; moved: {moved_count}."
    )
    print(f"Results folder: {results_directory}")
    return len(image_paths), moved_count


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description=(
            "Recursively find Everdell result-screen screenshots and move "
            "them into an everdell_results subfolder."
        )
    )
    parser.add_argument(
        "folder", type=Path, help="folder containing photos and other files"
    )
    args = parser.parse_args(argv)

    source_directory = args.folder.expanduser().resolve()
    if not source_directory.is_dir():
        parser.error(f"path is not a folder: {source_directory}")

    try:
        filter_images(source_directory)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Failed to start filter: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
