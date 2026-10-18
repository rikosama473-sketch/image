from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_FIELDS = {"base_model_identifier", "lora_identifiers", "lora_weights_or_settings"}


class ModelLoraProvenanceSchemaTests(unittest.TestCase):
    def test_manifest_has_model_and_lora_fields_without_auto_approval(self) -> None:
        with (ROOT / "data" / "training-labels.csv").open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            self.assertTrue(PROVENANCE_FIELDS.issubset(set(reader.fieldnames or [])))
            rows = list(reader)
        self.assertEqual(len(rows), 759)
        self.assertTrue(all(row["training_permission"] == "unreviewed" for row in rows))
        self.assertTrue(all(not row["lora_identifiers"] for row in rows))

    def test_local_reviewer_and_sync_preserve_provenance_fields(self) -> None:
        reviewer = (ROOT / "tools" / "dataset-reviewer" / "app.js").read_text(encoding="utf-8")
        sync = (ROOT / "scripts" / "sync_training_labels.py").read_text(encoding="utf-8")
        for field in PROVENANCE_FIELDS:
            self.assertIn(field, reviewer)
            self.assertIn(field, sync)


if __name__ == "__main__":
    unittest.main()
