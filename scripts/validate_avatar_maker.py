#!/usr/bin/env python3
"""Validate the image-driven avatar maker, asset provenance, and inline JavaScript."""
from __future__ import annotations
import json, re, shutil, subprocess, sys, tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "tools" / "avatar-maker" / "index.html"
CATALOG_PATH = ROOT / "tools" / "avatar-maker" / "assets" / "catalog.json"
LIBRARY_PATH = ROOT / "tools" / "avatar-maker" / "assets" / "image-library.json"
SERVER_PATH = ROOT / "tools" / "avatar-maker" / "ai_edit_server.py"
REQUIRED_IDS = {"nav","canvas","maskOverlay","stage","stageNote","miniLooks","layerTabs","layerList","layerCount","catIcon","catTitle","pills","content","styles","saveBtn","loadBtn","exportBtn","jsonFile","imageFile","comboCount","candidateDialog","cancelCandidate","confirmCandidate","toast"}
REQUIRED_FEATURES = ("async function render(", "function gallery(", "function addMask(", "function importFiles(", "function save(", "function load(", "function exportPng(", "pending_visual_review", "character-layers/pibara", "image/png", "IMAGE Character Creator", "function aiWorkspace(root)", "function runAIEdit()", "/api/ai-edit", "OPENAI_API_KEY", "ai_result", "function createAIMaskDataUrl()", "aiMaskStrokes", "mask_data_url", "function anatomyWorkspace(root)", "function requestAnatomyGuide(type)", "function createCutoutLayer()", "function exportSelectedLayerPng()", "function libraryWorkspace(root)", "function useLibraryAsset(id)", "image-library.json")
class Inspector(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.ids=[]; self.inline=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"): self.ids.append(a["id"])
        if tag.lower()=="script" and "src" not in a: self.inline+=1

def main():
    if not HTML_PATH.is_file() or not CATALOG_PATH.is_file() or not LIBRARY_PATH.is_file() or not SERVER_PATH.is_file():
        print("Missing avatar maker HTML/catalog/library/AI bridge.",file=sys.stderr); return 1
    html=HTML_PATH.read_text(encoding="utf-8"); parser=Inspector(); parser.feed(html)
    dup=sorted({x for x in parser.ids if parser.ids.count(x)>1}); missing=sorted(REQUIRED_IDS-set(parser.ids))
    absent=[x for x in REQUIRED_FEATURES if x not in html]
    server=SERVER_PATH.read_text(encoding="utf-8")
    server_required=("def validate_mask_data_url(", 'payload["mask"] = mask_payload', "OPENAI_API_KEY")
    absent.extend("server: "+x for x in server_required if x not in server)
    if re.search(r"<\s*svg\b|renderSvg\s*\(",html,re.I): absent.append("No geometrically drawn SVG avatar is allowed")
    if dup or missing or absent:
        if dup: print("Duplicate IDs: "+", ".join(dup),file=sys.stderr)
        if missing: print("Missing IDs: "+", ".join(missing),file=sys.stderr)
        if absent: print("Required image-driven features missing: "+", ".join(absent),file=sys.stderr)
        return 1
    try: catalog=json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc: print(f"Invalid catalog JSON: {exc}",file=sys.stderr); return 1
    if catalog.get("schema_version")!=2: print("Unsupported catalog schema.",file=sys.stderr); return 1
    for asset in catalog.get("base_illustrations",[])+catalog.get("candidate_layers",[]):
        path=asset.get("repo_path")
        if not path or not (ROOT/path).is_file(): print(f"Missing catalog asset: {path}",file=sys.stderr); return 1
        if asset.get("kind")=="semantic_mask_candidate" and asset.get("status")!="pending_visual_review": print(f"Unreviewed mask incorrectly marked approved: {asset.get('id')}",file=sys.stderr); return 1
    try: library=json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc: print(f"Invalid image library JSON: {exc}",file=sys.stderr); return 1
    assets=library.get("assets",[]) if isinstance(library,dict) else []
    if library.get("schema_version")!=1 or not isinstance(assets,list):
        print("Unsupported or invalid image library schema.",file=sys.stderr); return 1
    if library.get("asset_count")!=len(assets) or len(assets)<1:
        print("Image library asset_count does not match its assets array.",file=sys.stderr); return 1
    for asset in assets:
        relative=asset.get("path","") if isinstance(asset,dict) else ""
        path=Path(relative)
        if not relative or path.is_absolute() or ".." in path.parts or not (ROOT/path).is_file():
            print(f"Unsafe or missing image-library path: {relative}",file=sys.stderr); return 1
        if not str(asset.get("src","")).startswith("../../"):
            print(f"Invalid local thumbnail source: {relative}",file=sys.stderr); return 1
    for source in catalog.get("external_libraries",[]):
        if "CC0" not in source.get("license",""): print(f"License note absent: {source.get('id')}",file=sys.stderr); return 1
        for key in ("source_page","download_url"):
            value=source.get(key,"")
            if not value.startswith("https://") or value.split("/",3)[2]!="opengameart.org": print(f"Unexpected source link: {source.get('id')}",file=sys.stderr); return 1
    scripts=re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script\s*>",html,re.I); js="\n".join(x for x in scripts if x.strip())
    node=shutil.which("node")
    if not js or not parser.inline: print("Inline JavaScript missing.",file=sys.stderr); return 1
    if not node: print("Node.js required for syntax validation.",file=sys.stderr); return 2
    with tempfile.TemporaryDirectory(prefix="image-avatar-maker-") as temp:
        f=Path(temp)/"app.js"; f.write_text(js,encoding="utf-8"); p=subprocess.run([node,"--check",str(f)],capture_output=True,text=True)
    if p.returncode: print(p.stdout+p.stderr,file=sys.stderr); return p.returncode
    print(f"PASS: image-based avatar maker; {len(parser.ids)} IDs; {len(catalog['base_illustrations'])} base illustrations; {len(catalog['candidate_layers'])} pending masks; {len(assets)} indexed library images; JS syntax valid.")
    return 0
if __name__=="__main__": raise SystemExit(main())
