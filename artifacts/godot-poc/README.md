# Godot presentation POC evidence

This directory contains review evidence for the presentation-only Godot vertical slice. Canonical simulation, persistence, replay, and event history remain in Python; Godot consumes `terrarium.frame.v1`.

## Accepted Canvas baseline

- `canvas-spring-clear.png`
- SHA-256: `bfb55ecac559edccd7e8a5d9e2c6063feca9081c78bf5436f492cd2ade1c84b0`
- `display/web/app.js` remained byte-identical at `df5afe734eb2b367f1cfc28201ea9338ebad86cc155cb93136f14ed4381dadc5`.

## Final Godot Lab capture matrix

Godot 4.7.2, Xvfb + Mesa software rendering, 400x240 art surface presented at exact 2x to 800x480. Every capture was verified with a standard-library PNG decoder to have zero non-identical 2x blocks.

| Scenario | manual_ms | SHA-256 |
| --- | ---: | --- |
| spring_clear_idle | 1300 | `617cb6eb2518ef67dab7a36091b4199d29805a7afb2d7a0081b3ad8a1dae6e20` |
| spring_rain_idle | 1300 | `aa84ffaa40f6f0664d2397529d07ebd1d5bd618c5cf33a1a98810894694314d4` |
| winter_warm_night | 1300 | `cc51c3109ac97de834edfafc4bfd5fb81c00405c94bc87dd04841831d1e9db9b` |
| walk_to_window | 1300 | `dfce521b2635ccc732b564415e22cca64340f298147e3034294d6399bae8cebb` |
| inspect_red_thread | 700 | `76cb318ee0754d1507c7dc522aecd41aa5f8954603d43b4d70731381d63eef4e` |
| pickup_red_thread | 1300 | `8ddfc473333284d579c2be3bd03f4f10b022060f053d5628cf5f8bff4407baf5` |
| carry_walk | 1300 | `733e5e7fc732fe8f4f599ed99ca98ad919a621bfab6e3c34593718335f037686` |
| red_thread_rumpled | 1300 | `f181af285f0851c803d76525a236abd3caf7efc3969695bcf25af773dd057f77` |
| red_thread_nested | 1300 | `a83134b3a1b3864bfa0722a8164e5e755efa0f9eee1feb066d4e1ad473d40953` |

Two independent final `spring_clear_idle` captures were byte-identical. The Lab capture files are ephemeral verification outputs; reproducible inputs are kept under `display/godot/`, `presentation/`, and `tools/build_godot_vertical_slice_fixtures.py`.

## Decision gate

The POC passes the technical renderer gate: deterministic fixture rendering, integer scaling, weather/lighting variants, animation/action states, stateful object visuals, foreground occlusion, and Y/depth sorting all work without moving canonical state into Godot. Visual review should determine whether the authored art direction is strong enough to authorize the next migration phase.
