# Pixel-Art Overhaul — Iteration 8E: Atmospheric World

**Status: ACCEPTED**

Iteration 8E makes the habitat feel temporally alive while Moss is still. It is intentionally a **renderer/art/tooling-only** checkpoint: authoritative `terrarium/` simulation source did not change, no ambient behavior command or persistent animation state was added, and the accepted seed-1701/tick-10080 semantic frame remains byte-identical to Iteration 8D.

## Starting point

Accepted 8D checkpoint:

- commit: `c0ada09` — `Give Terrarium objects stateful identities`;
- snapshot: `20260828T112207258140Z-pixel-art-overhaul-iteration8d`;
- semantic frame SHA256: `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`;
- renderer JS SHA256: `f8e12181a18c2616fdeb8dae1ee5a0453fab6ba3a5ab88912782e497e35cb701`;
- authored-art tree SHA256: `ed1fee4cd060519267d131837ab45772754108c1c2eaa4c9a9c65322bce08d9a`;
- 73 authored assets: 46 Moss / 13 object-state.

Repository state and live runtime were inspected before implementation. Canonical Moss at `${XDG_STATE_HOME:-$HOME/.local/state}/terrarium/live` was not reset, replaced, or used as a destructive fixture. Browser/development UAT used isolated `/tmp` state.

## Visual/system audit

The accepted renderer already exposed the correct authority inputs for atmosphere: canonical `world_minutes`, lighting, weather, world-event state, object state, history, deterministic timing helpers, and the declarative scene queue. No new world schema was required.

The principal visual gaps were:

- the window was mostly one static exterior asset plus sparse weather marks;
- ambient motion was limited to generic motes/rain and did not establish depth or local character;
- decorative timing did not have an explicit authored phase/period system;
- rain/mist did not sufficiently influence whole-room mood;
- night lacked a strong pixel-native warm-shelter/cool-room composition;
- existing temporal fixtures were optimized for short action transitions rather than 30–60 second passive observation.

That audit justified a renderer-local solution rather than new behavior/environment state.

## Atmospheric systems added

Five authored `terrarium.pixel-asset.v1` environment assets were added:

- `environment.window-foliage-far`;
- `environment.window-foliage-mid`;
- `environment.window-foliage-near`;
- `environment.window-curtain-motion`;
- `environment.nook-sconce`.

The authored manifest is now **78 assets total**, preserving **46 Moss assets** and **13 object-state assets**.

Renderer presentation now includes:

- three exterior foliage depth layers with distinct held-step periods and phases;
- restrained curtain edge movement on an independent period;
- rain pane traces with multiple per-trace periods and slow hard-edged runoff;
- discrete mist drift;
- sparse localized daylight motes;
- slowly moving hard-edged branch-shadow shapes;
- infrequent water-bowl shimmer;
- hard-edged warm local night treatment around the sleeping nook and activity/desk area;
- whole-scene finite rain/mist palette treatments in addition to local glass effects.

Ambient timing derives from canonical `world_minutes`. Development temporal fixtures may add their explicit deterministic fixture timestamp to that clock only inside temporal UAT. Production behavior does not gain a second simulation clock.

## Pixel-native lighting/weather law

The night treatment uses finite palette substitution and hard-edged one-pixel/stepped floor highlights. It does **not** use gradients, bloom, blur, Gaussian masks, radial lights, alpha fog, or modern soft compositing.

Rain and mist now alter the perceived palette/value balance of the room as well as the window treatment. Canonical weather remains the sole weather fact; the renderer only chooses deterministic presentation derived from it.

## Deliberately rejected / deferred

The following were considered but not accepted into 8E because the smaller system already met the artistic goal and additional motion risked screensaver noise:

- a drifting-leaf particle field;
- looping ambient distant birds/insects;
- snow before a stronger seasonal authority exists;
- fireplace/flame animation;
- full-room random sparkle or generic motes;
- smooth gradients, bloom, blur, or fog masks.

Stillness remains valid. Ambient effects remain subordinate to Moss and major situational events.

## UAT defect fixed

Long-observation UAT exposed a pre-existing renderer telemetry/contact issue: absent canonical target/contact coordinates were coerced through `Number(null)` and appeared as `(0,0)`. Target extraction now distinguishes absent values correctly. This did not change world authority or behavior; it removed false presentation/telemetry semantics.

## Temporal evaluation

The deterministic temporal fixture pack now includes explicit atmosphere scenarios for:

- quiet clear day;
- quiet clear night;
- night with warm local lighting;
- rain;
- mist;
- window-focused atmosphere;
- stationary Moss with environmental life;
- walking Moss with atmosphere subordinate;
- situational-event + ambient coexistence;
- sleep;
- object interaction with atmosphere active.

Atmosphere scenarios use long review timestamps:

`0, 1500, 4200, 7800, 12500, 19000, 28000, 41000, 56000 ms`.

A dedicated `evaluate_atmosphere.py` rejects missing contexts, non-deterministic fixture construction, synchronized single-loop timing, insufficient rain-period variety, behavior-authority leakage, random/sine motion, soft modern compositing, or layer promotion above actors.

## Browser / temporal UAT

Final UAT used the production renderer at **800×480** with isolated `/tmp/terrarium-iteration8e-final` state. Canonical Moss was never used as the test fixture.

Results:

- clear-day long sequence: **exact deterministic repeat**;
- all ten required atmosphere contexts: **7–9 distinct rasters across 9 samples**;
- every captured sample: exact **400×240 → 800×480 2× nearest-neighbor** with **0 scale-error blocks**;
- continuity probe: **0 px** jump;
- browser console errors: **0**; the same benign dev temporal-fixture warning seen in prior accepted checkpoints remains;
- scene hierarchy remains `BACK / STRUCTURE / SURFACE / WORLD / ACTORS / FRONT`; ambient presentation is never promoted to `ALWAYS_FRONT`;
- RAF probe: **182 frames / 3016.6 ms**, p50 **16.7 ms**, p95/max **16.8 ms**, zero intervals above 34 ms or 50 ms.

Representative clear-day, warm-night, and rain frames were inspected from the actual production renderer. No implemented effect required removal during the final taste pass.

## Regression matrix

All inherited product gates pass:

- pytest: **51/51 PASS**;
- Python 3.10 grammar: **37 sources PASS**;
- `node --check display/web/app.js`: **PASS**;
- authored-art validation: **78/78 PASS**;
- dedicated 8E atmosphere evaluation: **PASS**;
- technical evaluator at **10,080 events**: append-only SQLite, event hash chain, JSONL parity, restart persistence, semantic frame contract, and exact snapshot+event replay **PASS**;
- behavior, spatial, coherence, habits: seeds **1701 / 1702 / 42 / 999**, **10,080 steps each**, all **PASS**;
- Iteration-6 repertoire regression: **PASS**;
- Iteration-7 situational regression: **PASS**;
- Iteration-8D object-affordance regression: **PASS**;
- deterministic production-browser UAT: **PASS**;
- combined Iteration-8E regression matrix: **PASS**.

An independent seed-1701/tick-10080 reconstruction produced semantic frame SHA256:

`e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`

This exactly matches accepted 8D. `git diff -- terrarium` was empty at acceptance, proving 8E did not modify authoritative simulation source.

## Accepted checkpoint

Exactly one accepted deterministic development snapshot was captured after the gates passed:

- snapshot: `20260828T123835255741Z-pixel-art-overhaul-iteration8e`;
- deterministic seed/tick: **1701 / 10080**;
- semantic frame SHA256: `e191850f3c454b926e9b4fe4355298be3ff5eb4ea351be6975fe7d45ab010f9d`;
- renderer JS SHA256: `c46cc4722cade0585f7ef4af122e4801debaa50c6c8eddf054e511118f307b85`;
- authored-art tree SHA256: `5daacbe022e34b807d2008ee37037bef998b99abe77d8eafde157bcf599faae4`.

Acceptance evidence:

- `artifacts/pixel-art-overhaul-iteration8e.json`;
- `artifacts/pixel-art-overhaul-iteration8e-regression-matrix.json`;
- `artifacts/pixel-art-overhaul-iteration8e-browser-uat.json`;
- `artifacts/pixel-art-overhaul-iteration8e-atmosphere.json`;
- `artifacts/iteration8e-art-direction-matrix.json`;
- browser evidence under `artifacts/iteration8e-browser-evidence/`.

## SBC / Gen18 decision

The existing authored-art pipeline, palette system, scene queue, deterministic fixture framework, browser temporal evidence path, evaluator tooling, and Optiplex/SBC capabilities were sufficient. No reusable platform deficiency was exposed. Self-Building Computer, Capability Forge, and the frozen Optiplex MCP surface were not modified.

**Gen18: NO**

## Next

**Iteration 8F — Seasonal Terrarium.** Add a canonical deterministic seasonal timescale substantially slower than the accelerated day, then coordinate long-horizon palette, exterior foliage, lighting, weather/particles, ambient life, and selected interior accents while preserving the familiar room, canonical history/replay/migration, and renderer/world authority boundary.
