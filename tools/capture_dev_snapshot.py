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


def preview_svg(frame: dict) -> str:
    palettes = {
        "night": ("#27313d", "#3b342f", "#162238"),
        "dawn": ("#75665e", "#5b493b", "#c78373"),
        "dusk": ("#665957", "#594438", "#8e5e76"),
        "day": ("#8b806f", "#6e5946", "#82a6a1"),
    }
    wall, floor, sky = palettes.get(frame["lighting"], palettes["day"])
    object_colors = {"stone":"#557487","leaf":"#b8773f","seed":"#87633d","shell":"#d0b6a0","thread":"#9f564b","trinket":"#d8c3a8"}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 480" width="800" height="480">',
        f'<rect width="800" height="315" fill="{wall}"/><rect y="315" width="800" height="165" fill="{floor}"/>',
        '<rect x="54" y="48" width="225" height="172" rx="5" fill="#392f31"/>',
        f'<rect x="65" y="58" width="203" height="151" rx="2" fill="{sky}"/>',
        '<rect x="52" y="353" width="210" height="74" rx="8" fill="#463a34"/><rect x="62" y="362" width="188" height="53" rx="8" fill="#a28c70"/>',
        '<rect x="296" y="333" width="224" height="91" rx="30" fill="#73806a" opacity=".9"/>',
        '<rect x="595" y="61" width="157" height="17" fill="#4c372d"/><rect x="603" y="78" width="8" height="158" fill="#4c372d"/><rect x="736" y="78" width="8" height="158" fill="#4c372d"/>',
        '<rect x="590" y="351" width="145" height="12" fill="#4b352c"/><rect x="604" y="363" width="9" height="48" fill="#4b352c"/><rect x="712" y="363" width="9" height="48" fill="#4b352c"/>',
    ]
    aftermath = frame.get("habitat", {}).get("activity_aftermath") or {}
    sleep_ticks = int(aftermath.get("sleep_nook_ticks", 0))
    sleep_bouts = int(aftermath.get("sleep_nook_bouts", 0))
    window_watches = int(aftermath.get("window_watches", 0))
    corner_uses = int(aftermath.get("activity_corner_uses", 0))
    if sleep_ticks > 0:
        parts.append(f'<ellipse cx="164" cy="389" rx="{45+min(18,sleep_bouts*3)}" ry="{16+min(8,sleep_ticks*.18):.1f}" fill="#4c3a30" opacity="{min(.26,.055+sleep_ticks*.009):.3f}"/>')
        parts.append(f'<rect x="{70+min(13,sleep_bouts*2)}" y="{367+min(4,sleep_bouts)}" width="72" height="29" rx="9" fill="#d0b992"/>')
    if window_watches > 0:
        for i in range(min(5,1+window_watches//4)):
            parts.append(f'<ellipse cx="{102+i*28}" cy="{190-(i%2)*6}" rx="8" ry="4" fill="#e2d8c4" opacity="{min(.18,.035+window_watches*.006):.3f}"/>')
        parts.append(f'<rect x="80" y="215" width="155" height="{3+min(4,window_watches//7)}" fill="#3b2d26" opacity="{min(.20,.035+window_watches*.007):.3f}"/>')
    if corner_uses >= 2:
        for i in range(min(4,1+corner_uses//6)):
            parts.append(f'<rect x="{599+i*24}" y="{332-(i%2)*5}" width="22" height="11" fill="#dac99e" opacity=".88"/>')

    route_paths = {
        "sleeping_nook": "M 405 421 Q 274 408 154 427",
        "window": "M 405 421 Q 286 337 182 306",
        "collection_shelf": "M 405 421 Q 548 333 650 303",
        "activity_corner": "M 405 421 Q 535 408 650 427",
    }
    path_wear = frame.get("habitat", {}).get("path_wear") or {}
    for zone, path_data in route_paths.items():
        wear = int(path_wear.get(zone, 0))
        if wear < 5: continue
        opacity = min(.24, .025 + (wear - 4) * .006)
        width = min(16, 3 + wear * .22)
        parts.append(f'<path d="{path_data}" fill="none" stroke="#2f221b" stroke-width="{width:.2f}" stroke-linecap="round" opacity="{opacity:.3f}"/>')
    for obj in frame["objects"]:
        moved = int(obj.get("times_moved", 0))
        if obj["state"] != "placed" or moved < 2: continue
        opacity = min(.16, .035 + moved * .012)
        rx = 13 + min(7, moved)
        parts.append(f'<ellipse cx="{obj["x"]}" cy="{obj["y"]+7}" rx="{rx}" ry="5" fill="#271d18" opacity="{opacity:.3f}"/>')
    for zone, wear in path_wear.items():
        if wear < 6: continue
        pos = {"sleeping_nook":(118,427),"window":(168,277),"open_space":(405,429),"collection_shelf":(682,246),"activity_corner":(655,427)}.get(zone)
        if pos: parts.append(f'<ellipse cx="{pos[0]}" cy="{pos[1]}" rx="{33+min(18,wear)}" ry="7" fill="#2a1f19" opacity=".18"/>')
    for obj in frame["objects"]:
        if obj["state"] == "carried": continue
        color = object_colors.get(obj["kind"], "#d8c3a8")
        parts.append(f'<circle cx="{obj["x"]}" cy="{obj["y"]}" r="8" fill="{color}" stroke="#302823" stroke-width="2"/>')
    c = frame["creature"]
    parts += [
        f'<ellipse cx="{c["x"]}" cy="{c["y"]+19}" rx="24" ry="7" fill="#1e1614" opacity=".24"/>',
        f'<ellipse cx="{c["x"]-2}" cy="{c["y"]+2}" rx="24" ry="20" fill="#60705a"/>',
        f'<ellipse cx="{c["x"]+9}" cy="{c["y"]-16}" rx="20" ry="18" fill="#718267"/>',
        f'<circle cx="{c["x"]+6}" cy="{c["y"]-20}" r="2.6" fill="#252923"/><circle cx="{c["x"]+23}" cy="{c["y"]-21}" r="2.6" fill="#252923"/>',
    ]
    if frame["weather"] == "rain":
        for i in range(14):
            x = 72 + (i * 14) % 188; y = 68 + (i * 23) % 125
            parts.append(f'<line x1="{x}" y1="{y}" x2="{x-5}" y2="{y+11}" stroke="#bed6da" stroke-width="2" opacity=".55"/>')
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
        "frame_contract": sha_file(ROOT / "terrarium/frame.py"),
        "engine": sha_file(ROOT / "terrarium/engine.py"),
    }
    meta = {
        "schema": "terrarium.dev-snapshot.v1",
        "snapshot_id": snapshot_id,
        "captured_at": utc_now(),
        "note": args.note,
        "preview": {"path": f"dev/{snapshot_id}/preview.svg", "sha256": sha_file(preview_path)},
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
