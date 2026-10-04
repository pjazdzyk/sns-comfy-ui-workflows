"""Download every model the workflows need. Stdlib only, resumable, no Hugging Face login.

The model list is read from the workflows themselves (each loader node carries
properties.models = [{name, url, directory}]), so it always matches the JSON files.

Usage:
  python download_models.py --models-dir "C:/path/to/ComfyUI/models"              # everything
  python download_models.py --models-dir ... --workflows 01 07                     # only some workflows
  python download_models.py --list                                                 # show what would be downloaded
  python download_models.py --check                                                # verify every URL is reachable
"""
import argparse, glob, json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WF_DIR = os.path.join(HERE, "..", "workflows")


def collect(prefixes=None):
    models = {}  # (directory, name) -> {url, workflows}
    for f in sorted(glob.glob(os.path.join(WF_DIR, "*.json"))):
        wf = os.path.basename(f)
        if prefixes and not any(wf.startswith(p) for p in prefixes):
            continue
        d = json.load(open(f, encoding="utf-8"))
        for g in [d] + d.get("definitions", {}).get("subgraphs", []):
            for n in g.get("nodes", []):
                if n.get("mode") in (2, 4):
                    continue
                for m in (n.get("properties") or {}).get("models", []) or []:
                    key = (m["directory"], m["name"])
                    models.setdefault(key, {"url": m["url"], "workflows": set()})["workflows"].add(wf.split("_")[0])
    return models


def remote_size(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "sns-comfy-ui-workflows"})
    r = urllib.request.urlopen(req, timeout=60)
    return int(r.headers.get("x-linked-size") or r.headers.get("content-length") or 0)


def download(url, dst, size):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    part = dst + ".part"
    for attempt in range(8):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        if size and have >= size:
            break
        req = urllib.request.Request(url, headers={"User-Agent": "sns-comfy-ui-workflows", "Range": f"bytes={have}-"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r, open(part, "ab") as out:
                t0, done = time.time(), 0
                while True:
                    chunk = r.read(8 << 20)
                    if not chunk:
                        break
                    out.write(chunk); done += len(chunk)
                    pct = 100 * (have + done) / size if size else 0
                    mbs = done / 1e6 / max(time.time() - t0, 1e-3)
                    print(f"\r    {pct:5.1f}%  {(have + done) / 1e9:6.2f} GB  {mbs:6.1f} MB/s", end="", flush=True)
            print()
        except Exception as e:
            print(f"\n    retry {attempt + 1}: {e}")
            time.sleep(5)
    if size and os.path.getsize(part) != size:
        raise RuntimeError(f"incomplete download: {dst}")
    os.replace(part, dst)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models-dir", help="your ComfyUI 'models' folder")
    ap.add_argument("--workflows", nargs="*", help="workflow number prefixes, e.g. 01 03d 07 (default: all)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true", help="HEAD-check every URL (no download)")
    a = ap.parse_args()

    models = collect(a.workflows)
    if a.list or a.check:
        total = 0
        for (d, n), m in sorted(models.items()):
            s = ""
            if a.check:
                try:
                    sz = remote_size(m["url"]); total += sz; s = f"{sz / 1e9:7.2f} GB OK "
                except Exception as e:
                    s = f"   FAILED ({e}) "
            print(f"{s}{d}/{n}   [{', '.join(sorted(m['workflows']))}]")
        print(f"\n{len(models)} files" + (f", {total / 1e9:.1f} GB total" if a.check else ""))
        return
    if not a.models_dir:
        ap.error("--models-dir is required (or use --list / --check)")

    for i, ((d, n), m) in enumerate(sorted(models.items()), 1):
        dst = os.path.join(a.models_dir, d, n)
        size = remote_size(m["url"])
        if os.path.exists(dst) and (not size or os.path.getsize(dst) == size):
            print(f"[{i}/{len(models)}] ok      {d}/{n}")
            continue
        print(f"[{i}/{len(models)}] get     {d}/{n}  ({size / 1e9:.2f} GB)")
        download(m["url"], dst, size)
    print("\nAll models present.")


if __name__ == "__main__":
    main()
