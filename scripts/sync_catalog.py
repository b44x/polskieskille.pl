#!/usr/bin/env python3
"""Copy the skill registry and demo from a local ai-polish-skills checkout."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--source", type=Path, default=root.parent / "ai-polish-skills")
    parser.add_argument("--catalog-only", action="store_true", help="Keep the current demo assets")
    args = parser.parse_args()
    registry = json.loads((args.source / "registry/registry.min.json").read_text(encoding="utf-8"))
    skills = registry.get("skills", [])
    if not skills or registry.get("skills_count") != len(skills):
        parser.error("Registry is empty or its skill count is inconsistent")
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "registry.min.json").write_text(json.dumps(registry, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(root / "scripts/build_seo.py")], check=True)
    if not args.catalog_only:
        demo = args.source / "docs/demo/demo.mp4"
        # Extract the poster before replacing the site's current video.
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "6", "-i", str(demo), "-frames:v", "1", "-update", "1", "-q:v", "2", str(assets / "demo-poster.jpg")], check=True)
        shutil.copyfile(demo, assets / "demo.mp4")
    print("Synced {} skills{}".format(len(skills), "" if args.catalog_only else " and demo assets"))


if __name__ == "__main__":
    main()
