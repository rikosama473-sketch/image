import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "select_next_character_asset_task.py"
SPEC = importlib.util.spec_from_file_location("character_asset_queue", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CharacterAssetQueueTests(unittest.TestCase):
    def make_root(self, temp):
        root = Path(temp)
        (root / "data").mkdir()
        (root / "from-PixAI-2034984086876227343-0.png").write_bytes(b"pibara-source")
        registry = {
            "characters": [
                {"id": "pibara", "source_images": ["from-PixAI-2034984086876227343-0.png"]},
                {"id": "sunna", "source_images": []},
                {"id": "chie", "source_images": []},
            ]
        }
        (root / "data" / "character-prompt-registry.json").write_text(
            json.dumps(registry), encoding="utf-8"
        )
        return root

    def mark_complete(self, root, pack, character="pibara", reference="from-PixAI-2034984086876227343-0.png"):
        source = root / reference
        sha = MODULE.source_sha256(source)
        run_dir = root / "generated" / "character-assets" / character / ("run-" + pack)
        render_dir = run_dir / "renders"
        render_dir.mkdir(parents=True, exist_ok=True)
        slug = {
            "hair-core-5": "blunt-bob",
            "expressions-core-5": "happy",
            "eyes-4": "eye-catchlights",
            "accessories-4": "ribbon",
            "face-details-4": "freckles",
        }[pack]
        render = render_dir / f"{slug}.png"
        render.write_bytes(b"png-placeholder-for-queue-test")
        manifest = {
            "character_id": character,
            "pack": pack,
            "pack_status": "complete",
            "source": {"path": reference, "sha256": sha},
            "required_asset_ids": [slug],
            "completed_asset_ids": [slug],
            "variants": [{"asset_id": slug, "render": {"file": render.relative_to(root).as_posix()}}],
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_starts_with_first_incomplete_pibara_pack(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            task = MODULE.select_next_task(root)
            self.assertEqual(task["character_id"], "pibara")
            self.assertEqual(task["asset_pack"], "hair-core-5")
            self.assertEqual(task["reference_image"], "from-PixAI-2034984086876227343-0.png")

    def test_moves_to_next_pack_when_hair_pack_is_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            self.mark_complete(root, "hair-core-5")
            task = MODULE.select_next_task(root)
            self.assertEqual(task["asset_pack"], "expressions-core-5")

    def test_moves_to_sunna_only_when_a_reference_is_registered(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            for pack in MODULE.PACK_ORDER:
                self.mark_complete(root, pack)
            (root / "sunna-reference.png").write_bytes(b"sunna-source")
            registry_path = root / "data" / "character-prompt-registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["characters"][1]["source_images"] = ["sunna-reference.png"]
            registry_path.write_text(json.dumps(registry), encoding="utf-8")
            task = MODULE.select_next_task(root)
            self.assertEqual(task["character_id"], "sunna")
            self.assertEqual(task["reference_image"], "sunna-reference.png")

    def test_never_reuses_pibara_reference_for_chie_or_sunna(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            for pack in MODULE.PACK_ORDER:
                self.mark_complete(root, pack)
            registry_path = root / "data" / "character-prompt-registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["characters"][1]["source_images"] = ["from-PixAI-2034984086876227343-0.png"]
            registry_path.write_text(json.dumps(registry), encoding="utf-8")
            self.assertIsNone(MODULE.select_next_task(root))

    def test_returns_none_when_no_confirmed_references_remain(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.make_root(temp)
            for pack in MODULE.PACK_ORDER:
                self.mark_complete(root, pack)
            self.assertIsNone(MODULE.select_next_task(root))


if __name__ == "__main__":
    unittest.main()
