from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def reduce_grid(raster: dict[str, Any], *, block_x: int = 2, block_y: int = 2) -> dict[str, Any]:
    w = int(raster["luma_grid_width"])
    h = int(raster["luma_grid_height"])
    grid = [float(x) for x in raster["luma_grid"]]
    if w % block_x or h % block_y or len(grid) != w * h:
        raise ValueError("luma grid cannot be reduced by requested block size")
    out: list[float] = []
    for gy in range(0, h, block_y):
        for gx in range(0, w, block_x):
            values = [grid[(gy + oy) * w + gx + ox] for oy in range(block_y) for ox in range(block_x)]
            out.append(round(sum(values) / len(values), 3))
    return {
        "width": int(raster.get("width", 800)),
        "height": int(raster.get("height", 480)),
        "pixel_hash": raster.get("pixel_hash"),
        "luma_grid_width": w // block_x,
        "luma_grid_height": h // block_y,
        "luma_grid": out,
    }


def compact(payload: dict[str, Any], *, block_x: int = 2, block_y: int = 2) -> dict[str, Any]:
    schema = payload.get("schema")
    if schema == "terrarium.raf-probe.v1":
        return {
            "mode": "raf",
            "raf_intervals_ms": payload["intervals_ms"],
            "provenance": {"scenario": payload.get("scenario"), "source_schema": schema},
        }
    if schema != "terrarium.temporal-capture.v1":
        raise ValueError(f"unsupported evidence schema: {schema}")
    keep = {
        "requested_timestamp_ms", "source_tick", "target_tick", "semantic_x", "semantic_y",
        "source_x", "source_y", "rendered_x", "rendered_y", "rendered_base_y",
        "interpolation_progress", "interpolation_ease", "semantic_distance", "moving",
        "facing", "pose", "activity", "carrying", "carried_rendered_x", "carried_rendered_y",
        "carried_relative_x", "carried_relative_y", "ambient_classes",
    }
    samples = []
    for sample in payload["samples"]:
        row = {key: sample.get(key) for key in keep}
        row["raster"] = reduce_grid(sample["raster"], block_x=block_x, block_y=block_y)
        samples.append(row)
    return {
        "mode": "sequence",
        "samples": samples,
        "provenance": {
            "scenario": payload.get("scenario"),
            "easing": payload.get("easing"),
            "source_schema": schema,
            "semantic_event": payload.get("semantic_event"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--block-x", type=int, default=2)
    parser.add_argument("--block-y", type=int, default=2)
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out = compact(payload, block_x=args.block_x, block_y=args.block_y)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "bytes": path.stat().st_size, "mode": out["mode"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
