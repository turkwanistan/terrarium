#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from terrarium.engine import WorldEngine
from terrarium.frame import make_frame
from terrarium.models import canonical_json, utc_now
from terrarium.store import WorldStore

SNAPSHOTS = ROOT / "snapshots" / "dev"
INDEX = ROOT / "snapshots" / "index.json"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_json(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def git_info() -> dict:
    def run(*args: str) -> str | None:
        p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
        return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None
    return {
        "head": run("rev-parse", "HEAD"),
        "branch": run("branch", "--show-current"),
        "dirty": bool(run("status", "--porcelain")),
    }


def deterministic_frame(seed: int, steps: int) -> tuple[dict, dict]:
    with tempfile.TemporaryDirectory(prefix="terrarium-dev-snapshot-") as tmp:
        store = WorldStore(tmp)
        store.initialize(seed, created_at="2026-01-01T00:00:00Z")
        engine = WorldEngine(store, seed=seed)
        engine.run_steps(steps)
        state = engine.current_state()
        frame = make_frame(state, last_event=store.last_event())
        store.close()
        return frame, {"mode": "deterministic", "seed": seed, "steps": steps}


def live_frame(data_dir: str) -> tuple[dict, dict]:
    store = WorldStore(ROOT / data_dir)
    state = store.load_state()
    if state is None:
        raise SystemExit(f"no canonical state in {data_dir}")
    frame = make_frame(state, last_event=store.last_event())
    source = {"mode": "live", "data_dir": data_dir, "seed": state["seed"], "steps": state["tick"]}
    store.close()
    return frame, source


def safe_slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not value:
        raise SystemExit("snapshot slug must contain letters or numbers")
    return value[:64]


def main() -> int:
    p = argparse.ArgumentParser(description="Capture a lightweight, Git-friendly Terrarium development checkpoint.")
    p.add_argument("slug")
    p.add_argument("--note", required=True)
    p.add_argument("--source", choices=["deterministic", "live"], default="deterministic")
    p.add_argument("--seed", type=int, default=1701)
    p.add_argument("--steps", type=int, default=240)
    p.add_argument("--data-dir", default="data/live")
    args = p.parse_args()

    slug = safe_slug(args.slug)
    frame, source = deterministic_frame(args.seed, args.steps) if args.source == "deterministic" else live_frame(args.data_dir)
    stamp = utc_now().replace("-", "").replace(":", "").replace(".", "").replace("Z", "Z")
    snapshot_id = f"{stamp}-{slug}"
    out = SNAPSHOTS / snapshot_id
    out.mkdir(parents=True, exist_ok=False)

    frame_path = out / "frame.json"
    frame_path.write_text(json.dumps(frame, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    source_hashes = {
        "renderer_js": sha_file(ROOT / "display/web/app.js"),
        "renderer_css": sha_file(ROOT / "display/web/style.css"),
        "frame_contract": sha_file(ROOT / "terrarium/frame.py"),
        "engine": sha_file(ROOT / "terrarium/engine.py"),
    }
    meta = {
        "schema": "terrarium.dev-snapshot.v1",
        "snapshot_id": snapshot_id,
        "captured_at": utc_now(),
        "note": args.note,
        "frame": {
            "path": f"dev/{snapshot_id}/frame.json",
            "sha256": sha_json(frame),
            "tick": frame["tick"],
            "logical_width": frame["logical_width"],
            "logical_height": frame["logical_height"],
        },
        "source": source,
        "source_hashes": source_hashes,
        "git": git_info(),
        "view_url": f"/?snapshot=/snapshots/dev/{snapshot_id}/frame.json",
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "README.md").write_text(
        f"# {snapshot_id}\n\n{args.note}\n\n"
        f"- frame: `{source['mode']}` seed `{source.get('seed')}`, step/tick `{frame['tick']}`\n"
        f"- renderer SHA256: `{source_hashes['renderer_js']}`\n"
        f"- frame SHA256: `{meta['frame']['sha256']}`\n"
        f"- local view: `{meta['view_url']}`\n\n"
        "This checkpoint stores semantic frame data, not canonical runtime state. The exact renderer source is pinned by hash and Git history.\n",
        encoding="utf-8",
    )

    try:
        index = json.loads(INDEX.read_text(encoding="utf-8"))
    except FileNotFoundError:
        index = {"schema": "terrarium.dev-snapshot-index.v1", "snapshots": []}
    index["snapshots"].append({
        "snapshot_id": snapshot_id,
        "captured_at": meta["captured_at"],
        "note": args.note,
        "frame_path": f"/snapshots/dev/{snapshot_id}/frame.json",
        "meta_path": f"/snapshots/dev/{snapshot_id}/meta.json",
        "tick": frame["tick"],
        "source": source,
        "renderer_sha256": source_hashes["renderer_js"],
    })
    INDEX.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"snapshot_id": snapshot_id, "directory": str(out.relative_to(ROOT)), "frame_sha256": meta["frame"]["sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
