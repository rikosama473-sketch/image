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
CUTOUT_REQUIREMENTS_PATH = ROOT / "requirements-avatar-cutout.txt"
REQUIRED_IDS = {"internetModeToggle","internetModeLabel","internetModeStatus","nav","canvas","maskOverlay","stage","stageNote","miniLooks","layerTabs","layerList","layerCount","catIcon","catTitle","pills","content","styles","saveBtn","loadBtn","exportBtn","jsonFile","imageFile","comboCount","candidateDialog","cancelCandidate","confirmCandidate","toast","baseToggleBtn"}
REQUIRED_FEATURES = ('sourceCategory:part.sourceCategory||"anatomy"', 'const categoryLabels={hair:"Cabello",eyes:"Ojos / cejas",face:"Rostro",body:"Cuerpo",clothes:"Ropa",accessories:"Accesorios"}', 'id="anatomyPieceType"', 'const allowedCategories=["hair","eyes","face","body","clothes","accessories"]', "if(!allowedCategories.includes(category))", "name:safeName,category,sourceCategory,character:", "function syncInternetUI()", "async function checkInternetConnection()", "function setInternetMode(enabled)", "navigator.onLine", "isLoopbackHost=host=>", "internet-blocked", "https://api.github.com/repos/rikosama473-sketch/image", 'id="internetModeToggle"', 'data-requires-internet="true" id="aiRun"', "async function render(", "function gallery(", "function addMask(", "function importFiles(", "function save(", "function load(", "function exportPng(", "pending_visual_review", "function currentBaseFilter()", "baseSource:activeLook().src", "character-layers/pibara", "image/png", "IMAGE Character Creator", "function starterWorkspace(root)", "function runStarterSmokeTest(id)", "function addLibraryAssetAsTestLayer(id)", "shownStarterCount=24", "allStarterSamples=all.filter", "starterMore", "AI_CUTOUT_TARGETS", "function startAICutout(targetId)", "function aiCutoutPromptForUser(text)", "function baseImageDataUrl()", "pending_ai_cutout_review", "ai-cutout-hair", "generate-hairstyle-variants.yml", "internal_test_overlay", "function useLibraryAsset(id,returnCategory=", "function aiWorkspace(root)", "function runAIEdit()", "function syncAIQuality()", "ai-variant-strip", "data-ai-result-index", "aiVariants", "variants:aiSettings.variants", "/api/ai-edit", "OPENAI_API_KEY", "ai_result", "function createAIMaskDataUrl()", "aiMaskStrokes", "mask_data_url", "function anatomyWorkspace(root)", "function requestAnatomyGuide(type)", "function createCutoutLayer()", "function exportSelectedLayerPng()", "function libraryWorkspace(root)", "image-library.json", "full_illustration", "data-local-cutout", "startLocalAnimeCutout", "localCutoutModel", "/api/remove-background", "function syncBaseToggle()", "state.baseVisible=d.baseVisible!==false", "baseVisible:state.baseVisible!==false", "meta.targetId===\"background\"", "function openLibraryAssetForExtraction(id)", "data-ai-free-extract-id", "const LOCAL_PARTS_DB=\"image-local-parts-v1\"", "function persistLocalPart(record)", "async function saveSelectedLayerToLocalLibrary()", "async function addLocalPartToCanvas(id)", "async function renderLocalParts()", "indexedDB.open(LOCAL_PARTS_DB,1)", "anatomySavePiece", "localPartsGrid")
class Inspector(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.ids=[]; self.inline=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"): self.ids.append(a["id"])
        if tag.lower()=="script" and "src" not in a: self.inline+=1

def main():
    if not HTML_PATH.is_file() or not CATALOG_PATH.is_file() or not LIBRARY_PATH.is_file() or not SERVER_PATH.is_file() or not CUTOUT_REQUIREMENTS_PATH.is_file():
        print("Missing avatar maker HTML/catalog/library/AI bridge.",file=sys.stderr); return 1
    html=HTML_PATH.read_text(encoding="utf-8"); parser=Inspector(); parser.feed(html)
    dup=sorted({x for x in parser.ids if parser.ids.count(x)>1}); missing=sorted(REQUIRED_IDS-set(parser.ids))
    absent=[x for x in REQUIRED_FEATURES if x not in html]
    server=SERVER_PATH.read_text(encoding="utf-8")
    server_required=("def validate_mask_data_url(", "def validate_quality(", "def validate_variants(", "def validate_cutout_model(", "def do_remove_background(", "ALLOWED_CUTOUT_MODELS", "_CUTOUT_SESSIONS", 'payload["mask"] = mask_payload', '"n": variants', "OPENAI_API_KEY", "rembg-local")
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
    requirements = CUTOUT_REQUIREMENTS_PATH.read_text(encoding="utf-8")
    if "rembg[cpu]==2.0.85" not in requirements:
        print("Local anime-cutout dependency is missing or not pinned.", file=sys.stderr); return 1
    full_illustrations = sum(1 for item in assets if isinstance(item, dict) and item.get("kind") == "full_illustration")
    if full_illustrations < 24:
        print(f"Expected at least 24 full illustration samples, found {full_illustrations}.", file=sys.stderr); return 1
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
    print(f"PASS: image-based avatar maker; {len(parser.ids)} IDs; {len(catalog['base_illustrations'])} base illustrations; {len(catalog['candidate_layers'])} pending masks; {full_illustrations} full illustrations; {len(assets)} indexed library images; local anime cutout dependency pinned; JS syntax valid.")
    return 0
if __name__=="__main__": raise SystemExit(main())
