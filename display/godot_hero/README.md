# Terrarium Godot hero art gate

This is a deliberately isolated visual decision experiment. It is **not** a renderer migration and does not read or write canonical Terrarium state.

The scene re-authors only the window + sleeping/reading nook + rug edge as a higher-craft hero slice. Godot composes engine-neutral PNG art, Moss frames, and a foreground occlusion layer at a fixed 400×240 logical surface with exact integer/nearest-neighbor presentation.

## Controls

- `1`: spring/day
- `2`: rain
- `3`: winter warm night
- `Space`: cycle idle → walk → inspect

## Run

```bash
GODOT_BIN=/path/to/godot scripts/run_godot_hero_gate.sh
```

Deterministic capture example:

```bash
xvfb-run -a env LIBGL_ALWAYS_SOFTWARE=1 GODOT_BIN=/path/to/godot \
  scripts/run_godot_hero_gate.sh \
  --variant spring_day --motion idle --manual-ms 540 \
  --capture /tmp/terrarium-hero-spring.png
```

The helper regenerates the deterministic art and performs the required Godot import scan before launch. The generated art source is `tools/generate_hero_art.py`; its output manifest lists the authored detail vocabulary. The existing Canvas renderer and the earlier Godot POC are untouched comparison evidence.

## Visual comparison review

From the OptiPlex host:

```bash
./scripts/run_godot_hero_review_lan.sh
```

Open the printed LAN URL. The page compares the closest existing Canvas crop with the exact layered art/coordinates used by this Godot hero scene, shows all three required environment variants, and presents representative Moss motion frames. Godot engine output was separately validated at 800×480 in the isolated Lab before accepting the page as review evidence.

## Moss character pass

The first hero-slice Moss diverged too far from the accepted Terrarium character identity. The current pilot re-bases Moss on the accepted authored Canvas silhouette and action poses from `display/art/moss/`, then adds only bounded higher-craft detail for the Godot presentation: warmer multi-value fur clusters, eye/brow readability, brighter cream blaze/muzzle/chest, inner-ear separation, paw accents, and a warm tail-tip accent. Idle remains planted with no time-driven bob. The environment is unchanged by this pass.
