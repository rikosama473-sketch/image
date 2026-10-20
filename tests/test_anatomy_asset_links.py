import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
README_FILES = [ROOT / "README.md", ROOT / "tools" / "avatar-maker" / "README.md"]
EXPECTED_RUN = "run-39496066089"
EXPECTED_ASSET_DIR = Path("generated/character-assets/pibara/2026-10-20") / EXPECTED_RUN


class AnatomyAssetLinkTests(unittest.TestCase):
    def test_immutable_github_links_point_to_real_repository_files(self):
        pattern = re.compile(
            r"https://github\.com/rikosama473-sketch/image/blob/([0-9a-f]{40})/"
            r"(generated/character-assets/pibara/[^)\s]+)"
        )
        matches = []
        for markdown in README_FILES:
            text = markdown.read_text(encoding="utf-8")
            self.assertNotIn("2026-10-10/" + EXPECTED_RUN, text, f"bad date in {markdown}")
            matches.extend(pattern.findall(text))

        paths = {Path(path) for _sha, path in matches}
        expected = {
            EXPECTED_ASSET_DIR / "renders" / "01-full-body-anatomy-a-pose.png",
            EXPECTED_ASSET_DIR / "transparent" / "01-full-body-anatomy-a-pose.png",
            EXPECTED_ASSET_DIR / "contact-sheet.jpg",
            EXPECTED_ASSET_DIR / "manifest.json",
            EXPECTED_ASSET_DIR / "PROMPTS.md",
        }
        self.assertTrue(expected.issubset(paths), f"Missing README links: {sorted(str(p) for p in expected - paths)}")
        for relative in expected:
            with self.subTest(path=str(relative)):
                self.assertTrue((ROOT / relative).is_file(), f"Broken anatomy link: {relative}")

    def test_library_anatomy_entry_points_to_existing_reviewed_status_asset(self):
        library_path = ROOT / "tools" / "avatar-maker" / "assets" / "image-library.json"
        library = json.loads(library_path.read_text(encoding="utf-8"))
        entry = next(
            item for item in library["assets"]
            if item.get("id") == "generated-pibara-anatomy-guide-1-full-body-anatomy-a-pose-f3777be4"
        )
        asset_path = ROOT / entry["path"]
        self.assertTrue(asset_path.is_file(), f"Missing indexed anatomy PNG: {entry['path']}")
        self.assertEqual(entry.get("visual_review"), "needs_visual_identity_review")
        self.assertTrue(entry.get("review_note"))

    def test_queued_batch_trigger_is_scoped_to_the_work_branch(self):
        workflow = (ROOT / ".github" / "workflows" / "generate-character-assets-free.yml").read_text(encoding="utf-8")
        queue_path = ROOT / "data" / "anatomy-generation-queue.json"
        self.assertTrue(queue_path.is_file(), "The one-time branch queue marker should exist.")
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        self.assertEqual(queue.get("character_id"), "pibara")
        self.assertEqual(queue.get("asset_pack"), "anatomy-sheet-4")
        self.assertEqual(queue.get("reference_image"), "from-PixAI-2034984086876227343-0.png")
        self.assertRegex(workflow, r"(?s)on:\s+push:\s+branches:\s+- work/easy-avatar-maker-2026-10\s+paths:\s+- data/anatomy-generation-queue\.json")
        self.assertIn("asset_pack=anatomy-sheet-4", workflow)
        self.assertNotIn("- main", workflow)

    def test_partial_anatomy_batch_files_and_links_exist(self):
        run_dir = Path("generated/character-assets/pibara/2026-10-20/run-39500149462")
        manifest_path = ROOT / run_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("pack"), "anatomy-sheet-4")
        self.assertEqual(manifest.get("pack_status"), "partial")
        self.assertEqual(len(manifest.get("completed_asset_ids", [])), 3)
        self.assertEqual(len(manifest.get("required_asset_ids", [])), 4)
        self.assertIn("ZeroGPU runs limit", manifest.get("last_error", ""))
        self.assertIn("front view", manifest.get("warning", "").lower() or manifest.get("visual_review_notes", "").lower())

        required = [
            run_dir / "renders" / "01-batch-front-a-pose.png",
            run_dir / "transparent" / "01-batch-front-a-pose.png",
            run_dir / "renders" / "02-batch-side-profile.png",
            run_dir / "transparent" / "02-batch-side-profile.png",
            run_dir / "renders" / "03-batch-back-view.png",
            run_dir / "transparent" / "03-batch-back-view.png",
            run_dir / "contact-sheet.jpg",
            run_dir / "PROMPTS.md",
            run_dir / "manifest.json",
        ]
        for relative in required:
            with self.subTest(path=str(relative)):
                self.assertTrue((ROOT / relative).is_file(), f"Missing generated batch file: {relative}")

        immutable_commit = "745404b7e5d516434ef9c5782cc1ba893631a828"
        for markdown in README_FILES:
            content = markdown.read_text(encoding="utf-8")
            for relative in required:
                with self.subTest(markdown=str(markdown), path=str(relative)):
                    self.assertIn(
                        f"https://github.com/rikosama473-sketch/image/blob/{immutable_commit}/{relative.as_posix()}",
                        content,
                        f"Missing working immutable link for {relative} in {markdown}",
                    )

        library = json.loads((ROOT / "tools" / "avatar-maker" / "assets" / "image-library.json").read_text(encoding="utf-8"))
        entries = [a for a in library["assets"] if a.get("path", "").startswith(run_dir.as_posix() + "/transparent/")]
        self.assertEqual(len(entries), 3)
        self.assertTrue(all(a.get("visual_review") == "needs_visual_identity_review" and a.get("review_note") for a in entries))

    def test_anatomy_gallery_embeds_existing_relative_images(self):
        gallery = ROOT / "generated" / "character-assets" / "pibara" / "2026-10-20" / "run-39500149462" / "ANATOMY-GALLERY.md"
        self.assertTrue(gallery.is_file())
        content = gallery.read_text(encoding="utf-8")
        for relative in (
            "contact-sheet.jpg",
            "renders/01-batch-front-a-pose.png",
            "transparent/01-batch-front-a-pose.png",
            "renders/02-batch-side-profile.png",
            "transparent/02-batch-side-profile.png",
            "renders/03-batch-back-view.png",
            "transparent/03-batch-back-view.png",
            "manifest.json",
            "PROMPTS.md",
        ):
            with self.subTest(path=relative):
                self.assertTrue((gallery.parent / relative).is_file())
                self.assertIn(f"]({relative})", content)
        gallery_url = "https://github.com/rikosama473-sketch/image/blob/daac2bf07e295bb7aac1484618b277312e25861f/generated/character-assets/pibara/2026-10-20/run-39500149462/ANATOMY-GALLERY.md"
        for markdown in README_FILES:
            with self.subTest(markdown=str(markdown)):
                self.assertIn(gallery_url, markdown.read_text(encoding="utf-8"))

    def test_manifest_links_match_generated_files(self):
        manifest_path = ROOT / EXPECTED_ASSET_DIR / "manifest.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["pack"], "anatomy-guide-1")
        self.assertEqual(manifest["pack_status"], "complete")
        for variant in manifest["variants"]:
            for field in ("render", "transparent_layer"):
                asset = variant.get(field)
                if not asset:
                    continue
                with self.subTest(field=field):
                    self.assertTrue((ROOT / asset["file"]).is_file(), f"Missing manifest asset: {asset['file']}")


if __name__ == "__main__":
    unittest.main()
