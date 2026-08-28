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


def sha_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


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


def _smooth01(value: float) -> float:
    t = max(0.0, min(1.0, float(value)))
    return t * t * (3.0 - 2.0 * t)


def _emergence(value: float, start: float, span: float) -> float:
    return _smooth01((float(value) - float(start)) / max(0.001, float(span)))


def preview_svg(frame: dict) -> str:
    # Lightweight Git preview only. The real Canvas renderer remains authority.
    colors = {
        "day": ("#a48b6a", "#785638", "#7eaaa6"),
        "dawn": ("#967b69", "#684b37", "#b77b70"),
        "dusk": ("#78645f", "#604331", "#865d78"),
        "night": ("#3e4650", "#49382f", "#1d2a43"),
    }
    wall, floor, sky = colors.get(frame["lighting"], colors["day"])
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240" width="800" height="480" shape-rendering="crispEdges">',
        f'<rect width="400" height="158" fill="{wall}"/><rect y="158" width="400" height="82" fill="{floor}"/>',
        '<rect x="22" y="23" width="121" height="91" fill="#352519"/>',
        f'<rect x="31" y="30" width="103" height="75" fill="{sky}"/><rect x="81" y="30" width="4" height="75" fill="#557c7e"/><rect x="31" y="65" width="103" height="4" fill="#557c7e"/>',
        '<rect x="20" y="31" width="9" height="68" fill="#e5cf9f"/><rect x="139" y="32" width="7" height="66" fill="#e5cf9f"/>',
        '<rect x="23" y="177" width="111" height="40" fill="#352519"/><rect x="31" y="181" width="95" height="28" fill="#c3aa7d"/><rect x="76" y="183" width="48" height="22" fill="#668399"/>',
        '<rect x="149" y="177" width="102" height="28" fill="#66754e"/><rect x="157" y="173" width="86" height="36" fill="#66754e"/>',
        '<rect x="298" y="29" width="79" height="10" fill="#533824"/><rect x="301" y="39" width="5" height="79" fill="#352519"/><rect x="369" y="39" width="5" height="79" fill="#352519"/>',
        '<rect x="295" y="175" width="73" height="7" fill="#765236"/><rect x="302" y="182" width="5" height="25" fill="#352519"/><rect x="356" y="182" width="5" height="25" fill="#352519"/>',
    ]
    object_colors = {"stone":"#668399","leaf":"#d39a4a","seed":"#765236","shell":"#e5cf9f","thread":"#a85c4d","trinket":"#d7c493"}
    for obj in frame["objects"]:
        if obj["state"] == "carried":
            continue
        x, y = round(obj["x"] / 2), round(obj["y"] / 2)
        color = object_colors.get(obj["kind"], "#e5cf9f")
        parts += [f'<rect x="{x-4}" y="{y-2}" width="8" height="5" fill="{color}"/>', f'<rect x="{x-2}" y="{y-3}" width="4" height="1" fill="#e5cf9f"/>']
    c = frame["creature"]; x, y = round(c["x"] / 2), round(c["y"] / 2)
    if c["pose"] == "sleep" or c["activity"] == "sleep":
        parts += [f'<rect x="{x-13}" y="{y-3}" width="25" height="9" fill="#8b5d3b"/>', f'<rect x="{x+2}" y="{y-9}" width="12" height="10" fill="#b47c50"/>', f'<rect x="{x+8}" y="{y-7}" width="6" height="6" fill="#d9bd8d"/>']
    else:
        flip = -1 if c.get("facing") == "left" else 1
        hx = x + 5 * flip
        parts += [f'<rect x="{x-13}" y="{y-8}" width="23" height="13" fill="#8b5d3b"/>', f'<rect x="{hx-7}" y="{y-19}" width="14" height="12" fill="#8b5d3b"/>', f'<rect x="{hx-10}" y="{y-17}" width="5" height="8" fill="#5f3c29"/>', f'<rect x="{hx+5}" y="{y-18}" width="5" height="8" fill="#5f3c29"/>', f'<rect x="{hx+2}" y="{y-14}" width="8" height="5" fill="#d9bd8d"/>']
    if frame.get("weather") == "rain":
        for i in range(18):
            xx = 34 + (i * 17) % 96; yy = 31 + (i * 13) % 68
            parts.append(f'<rect x="{xx}" y="{yy}" width="1" height="4" fill="#b0c7c0"/>')
    parts.append('</svg>')
    return ''.join(parts) + '\n'


def rebuild_snapshot_readme(index: dict) -> None:
    lines = ["# Terrarium development snapshots", "", "Git-friendly visual milestones. The SVG is a lightweight capture-time thumbnail; run Terrarium and open `/snapshots/` for the same stored frame through the real Canvas renderer.", ""]
    for item in reversed(index.get("snapshots", [])):
        lines += [f"## {item['snapshot_id']}", "", item["note"], "", f"![{item['snapshot_id']}](dev/{item['snapshot_id']}/preview.svg)", "", f"Deterministic tick `{item['tick']}` · renderer `{item['renderer_sha256'][:12]}`", ""]
    (ROOT / "snapshots" / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    preview_path = out / "preview.svg"
    preview_path.write_text(preview_svg(frame), encoding="utf-8")
    source_hashes = {
        "renderer_js": sha_file(ROOT / "display/web/app.js"),
        "renderer_css": sha_file(ROOT / "display/web/style.css"),
        "authored_art": sha_tree(ROOT / "display/art"),
        "frame_contract": sha_file(ROOT / "terrarium/frame.py"),
        "engine": sha_file(ROOT / "terrarium/engine.py"),
    }
    meta = {
        "schema": "terrarium.dev-snapshot.v1",
        "snapshot_id": snapshot_id,
        "captured_at": utc_now(),
        "note": args.note,
        "preview": {"path": f"dev/{snapshot_id}/preview.svg", "sha256": sha_file(preview_path)},
        "art_surface": {"width": 400, "height": 240, "integer_scale": 2, "smoothing": False},
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
        f"- authored-art SHA256: `{source_hashes['authored_art']}`\n"
        f"- frame SHA256: `{meta['frame']['sha256']}`\n"
        f"- GitHub-friendly preview: `preview.svg`\n"
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
        "preview_path": f"/snapshots/dev/{snapshot_id}/preview.svg",
    })
    INDEX.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rebuild_snapshot_readme(index)
    print(json.dumps({"snapshot_id": snapshot_id, "directory": str(out.relative_to(ROOT)), "frame_sha256": meta["frame"]["sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
