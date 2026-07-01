#!/usr/bin/env python3
"""generate downscaled page images + docupipe extraction json for the landing-page benchmark modal."""
import json, os, re, subprocess, glob, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "/Users/urimerhav/Code/docupanda-website/public/benchmarks/docs"
MAX_PAGES = 5
WIDTH = 1000

html = open(os.path.join(ROOT, "docubench-explorer.html"), encoding="utf-8").read()
DATA = json.loads(re.search(r"const DATA = (\{.*?\});", html, re.S).group(1))
DOCS = {d["id"]: d for d in DATA["docs"]}
ids = json.load(open("/tmp/dbids.json"))

os.makedirs(OUT, exist_ok=True)


def sips_to_jpeg(src, dst):
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72",
                    "-Z", str(WIDTH), src, "--out", dst],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def render_pdf(path, outdir):
    with tempfile.TemporaryDirectory() as td:
        prefix = os.path.join(td, "pg")
        subprocess.run(["pdftoppm", "-jpeg", "-r", "110", "-f", "1", "-l", str(MAX_PAGES), path, prefix],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pages = sorted(glob.glob(prefix + "*"))
        for i, p in enumerate(pages, 1):
            sips_to_jpeg(p, os.path.join(outdir, f"p{i}.jpg"))
        return len(pages)


def render_image(path, outdir):
    sips_to_jpeg(path, os.path.join(outdir, "p1.jpg"))
    return 1


def render_quicklook(path, outdir):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["qlmanage", "-t", "-s", "1300", "-o", td, path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pngs = glob.glob(os.path.join(td, "*.png"))
        if not pngs:
            return 0
        sips_to_jpeg(pngs[0], os.path.join(outdir, "p1.jpg"))
        return 1


manifest = {}
for did in ids:
    doc = DOCS[did]
    ext = doc["ftype"]
    src = glob.glob(os.path.join(ROOT, "documents", did + ".*"))
    if not src:
        print("MISSING doc", did); continue
    src = src[0]
    outdir = os.path.join(OUT, did)
    os.makedirs(outdir, exist_ok=True)

    if ext == "pdf":
        n = render_pdf(src, outdir)
    elif ext in ("jpeg", "jpg", "png", "tiff", "tif"):
        n = render_image(src, outdir)
    else:  # csv, xlsx, docx, xml, txt, html
        n = render_quicklook(src, outdir)

    # docupipe high-effort extraction json -> standardization.json (just the data object)
    res_path = os.path.join(ROOT, "results", "docupipe_high", did + ".json")
    res = json.load(open(res_path, encoding="utf-8"))
    json.dump(res.get("data", {}), open(os.path.join(outdir, "standardization.json"), "w", encoding="utf-8"),
              ensure_ascii=False)

    manifest[did] = {
        "pages": n,
        "ftype": ext,
        "origPages": doc["pages"],
        "score": round(res.get("score", 0), 4),
    }
    print(f"{did}: {ext:5s} pages={n} origPages={doc['pages']}")

json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=0)
print("\nmanifest written:", len(manifest), "docs ->", OUT)
