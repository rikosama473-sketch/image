#!/usr/bin/env python3
"""Summarize recovered image-generation metadata without copying prompt text.

The report is local-only by default. It contains coverage counts and observed
model/LoRA identifiers, but deliberately omits positive and negative prompts.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COVERAGE_FIELDS = (
    "prompt",
    "negative_prompt",
    "base_model_identifier",
    "base_model_hash",
    "lora_identifiers",
    "lora_weights_or_settings",
    "sampler",
    "steps",
    "cfg_scale",
    "seed",
)


def summarize(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No metadata rows found in {path}. Run extract_generation_metadata.py first.")

    def nonempty(row: dict[str, str], key: str) -> bool:
        return bool((row.get(key) or "").strip())

    metadata_present = Counter((row.get("metadata_present") or "unknown").strip().lower() for row in rows)
    coverage = {
        field: sum(1 for row in rows if nonempty(row, field))
        for field in COVERAGE_FIELDS
    }
    base_models = Counter((row.get("base_model_identifier") or "").strip() for row in rows)
    base_models.pop("", None)
    base_hashes = Counter((row.get("base_model_hash") or "").strip() for row in rows)
    base_hashes.pop("", None)
    loras = Counter((row.get("lora_identifiers") or "").strip() for row in rows)
    loras.pop("", None)
    image_formats = Counter((row.get("format") or "unknown").strip().upper() for row in rows)
    return {
        "source_csv": str(path),
        "image_count": len(rows),
        "metadata_present": dict(sorted(metadata_present.items())),
        "field_coverage": {
            key: {"present": value, "missing": len(rows) - value}
            for key, value in coverage.items()
        },
        "image_formats": dict(sorted(image_formats.items())),
        "observed_base_model_identifiers": [
            {"identifier": identifier, "image_count": count}
            for identifier, count in sorted(base_models.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
        "observed_base_model_hashes": [
            {"hash": identifier, "image_count": count}
            for identifier, count in sorted(base_hashes.items(), key=lambda item: (-item[1], item[0]))
        ],
        "observed_lora_identifiers": [
            {"identifier": identifier, "image_count": count}
            for identifier, count in sorted(loras.items(), key=lambda item: (-item[1], item[0].casefold()))
        ],
        "model_family_decision": "pending_manual_review",
        "notes": [
            "Names and embedded identifiers are evidence to review, not automatic proof of model-family compatibility.",
            "Prompt and negative-prompt text are intentionally excluded from this summary.",
            "Do not train until image provenance, licence, and training permission are approved.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "cache" / "generation-metadata.csv",
        help="CSV produced by extract_generation_metadata.py",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "cache" / "generation-metadata-summary.json",
        help="Local JSON report; the default path is excluded from Git",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source = args.input.expanduser().resolve()
    if not source.is_file():
        parser.error(
            f"Metadata report not found: {source}. First run: "
            "python scripts/extract_generation_metadata.py --root ."
        )
    try:
        report = summarize(source)
    except (OSError, csv.Error, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    output = args.output.expanduser()
    if not output.is_absolute():
        output = ROOT / output
    output = output.resolve()
    if output == source or (
        output.exists() and source.exists() and output.samefile(source)
    ):
        parser.error("Summary output cannot overwrite the full generation-metadata CSV.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imágenes en el informe: {report['image_count']}")
    print("Cobertura de metadatos:")
    for field, counts in report["field_coverage"].items():
        print(f"  {field}: {counts['present']}/{report['image_count']}")
    print(f"Modelos base observados: {len(report['observed_base_model_identifiers'])}")
    print(f"Identificadores LoRA observados: {len(report['observed_lora_identifiers'])}")
    print(f"Resumen local escrito en: {output}")
    print("La familia del modelo sigue pendiente de revisión; no se copiaron prompts al resumen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
