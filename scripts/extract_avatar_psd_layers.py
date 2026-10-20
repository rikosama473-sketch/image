#!/usr/bin/env python3
"""Export raster layers in PSDs as transparent full-canvas PNGs with preserved offsets."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_SOURCE=ROOT/"data"/"asset-cache"/"extracted"/"visual-novel-characters"
DEFAULT_OUTPUT=ROOT/"data"/"asset-cache"/"layers"/"visual-novel-characters"
SOURCE_PAGE="https://opengameart.org/node/54368"
LICENSE="CC0 as declared by the original OpenGameArt source page"

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def slug(s:str)->str:
    return (re.sub(r"[^A-Za-z0-9_-]+","-",s.strip()).strip("-_") or "unnamed")[:72]
def group(layer:Any)->bool:
    value=getattr(layer,"is_group",False)
    return bool(value() if callable(value) else value)
def export_psd(psd_path:Path,out_root:Path)->dict[str,Any]:
    try: from psd_tools import PSDImage
    except ImportError as exc: raise RuntimeError("Install requirements-avatar-assets.txt (psd-tools and Pillow).") from exc
    from PIL import Image
    psd=PSDImage.open(psd_path); width,height=int(psd.width),int(psd.height)
    if not (1<=width<=12000 and 1<=height<=12000): raise ValueError(f"Invalid canvas {width}x{height}")
    dest=out_root/slug(psd_path.stem); dest.mkdir(parents=True,exist_ok=True)
    layers=[]; names={}
    for index,layer in enumerate(psd.descendants()):
        if group(layer): continue
        try: im=layer.topil()
        except Exception: im=None
        if im is None: continue
        im=im.convert("RGBA"); left,top=int(layer.left),int(layer.top); right,bottom=left+im.width,top+im.height
        x0,y0=max(0,left),max(0,top); x1,y1=min(width,right),min(height,bottom)
        if x1<=x0 or y1<=y0: continue
        crop=im.crop((x0-left,y0-top,x1-left,y1-top)); canvas=Image.new("RGBA",(width,height),(0,0,0,0)); canvas.alpha_composite(crop,dest=(x0,y0))
        original=str(getattr(layer,"name","") or f"layer-{index+1}"); key=slug(original); names[key]=names.get(key,0)+1
        file=f"{index+1:03d}-{key}-{names[key]:02d}.png"; canvas.save(dest/file,"PNG",optimize=True)
        layers.append({"id":f"{psd_path.stem}:{index+1}:{key}","source_layer_index":index,"source_layer_name":original,"file":file,"canvas":{"width":width,"height":height},"source_offset":{"x":left,"y":top},"source_bounds":{"left":left,"top":top,"right":right,"bottom":bottom},"alignment":"exact source PSD canvas; offset preserved; no tight crop","visible_in_source":bool(getattr(layer,"visible",True)),"status":"extracted_needs_category_and_visual_review"})
    manifest={"schema_version":1,"source_file":psd_path.name,"source_sha256":sha256_file(psd_path),"source_page":SOURCE_PAGE,"license":LICENSE,"canvas":{"width":width,"height":height},"coordinates":"full canvas, top-left origin","layers":layers,"note":"Layer pixels and source offsets are preserved; visual compatibility with another character still requires review."}
    (dest/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"source":psd_path.name,"canvas":[width,height],"layers":len(layers),"output":str(dest)}
def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--source",type=Path,default=DEFAULT_SOURCE);p.add_argument("--output",type=Path,default=DEFAULT_OUTPUT);a=p.parse_args()
    source=a.source.expanduser().resolve(); out=a.output.expanduser().resolve()
    if not source.is_dir(): p.error(f"Source directory missing: {source}. Download/unpack the CC0 visual-novel-character pack first.")
    psds=sorted(source.rglob("*.psd"))
    if not psds: p.error(f"No PSD files found under {source}")
    try:
        for path in psds:
            r=export_psd(path,out); print(f"{r['source']}: {r['layers']} layers on {r['canvas'][0]}x{r['canvas'][1]} -> {r['output']}")
    except (OSError,ValueError,RuntimeError) as exc: print(f"ERROR: {exc}",file=sys.stderr); return 1
    return 0
if __name__=="__main__": raise SystemExit(main())
