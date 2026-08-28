from __future__ import annotations

import argparse
import json
import tempfile
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from terrarium.engine import Simulation, WorldEngine
from terrarium.models import (
    RULES_VERSION, SEASONAL_CLOCK_SCHEMA, SEASON_DAYS, SEASON_STAGE_DAYS, SEASONS, SEASON_STAGES,
    canonical_json, initial_state, normalize_seasonal_clock, seasonal_clock_for, sha256_json,
)
from terrarium.replay import assert_exact_replay
from terrarium.store import WorldStore
from tools.build_temporal_fixture_pack import build as build_fixtures

CREATED_AT = "2026-01-01T00:00:00Z"
FIRST_OBSERVED = "2026-08-28T15:00:00Z"


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _legacy_state() -> dict[str, Any]:
    state = initial_state(1701, created_at=CREATED_AT)
    state["rules_version"] = "terrarium-rules-v7-object-identity"
    state["habitat"].pop("seasonal_clock", None)
    # Representative persisted identity/history that seasonal migration must not rewrite.
    state["habitat"]["path_wear"]["window"] = 37
    state["habitat"]["activity_aftermath"]["window_watches"] = 11
    state["objects"][0]["times_moved"] = 9
    state["objects"][0]["interaction_state"] = "rolled"
    state["creature"]["habit_profile"]["experience_count"] = 222
    return state


def _seed_legacy_store(root: str) -> WorldStore:
    store = WorldStore(root)
    state = _legacy_state()
    store.conn.execute("BEGIN IMMEDIATE")
    try:
        store.conn.execute("INSERT INTO meta(key,value) VALUES('state',?)", (canonical_json(state),))
        store.conn.execute("INSERT INTO meta(key,value) VALUES('seed',?)", (str(state["seed"]),))
        store.conn.execute(
            "INSERT INTO snapshots(seq,tick,created_at,state_json,state_hash) VALUES(0,0,?,?,?)",
            (CREATED_AT, canonical_json(state), sha256_json(state)),
        )
        store.conn.execute("COMMIT")
    except Exception:
        store.conn.execute("ROLLBACK")
        store.close()
        raise
    return store


def _run_history(root: str, observations: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    store = _seed_legacy_store(root)
    engine = WorldEngine(store, seed=999999, snapshot_every=2)
    events = [engine.step(observed_at_utc=stamp) for stamp in observations]
    state = engine.current_state()
    replay = assert_exact_replay(store)
    store.close()
    reopened = WorldStore(root)
    restart_state = reopened.load_state()
    reopened.close()
    return state, events, {"replay": replay, "restart_exact": canonical_json(restart_state) == canonical_json(state)}


def _without_season(state: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(state)
    value["habitat"].pop("seasonal_clock", None)
    return value


def evaluate() -> dict[str, Any]:
    migration_before = _legacy_state()
    migration_after = deepcopy(migration_before)
    normalize_seasonal_clock(migration_after, observed_at_utc=FIRST_OBSERVED)
    preserved_before = _without_season(migration_before)
    preserved_after = _without_season(migration_after)

    start = datetime.fromisoformat(FIRST_OBSERVED.replace("Z", "+00:00")).astimezone(timezone.utc)
    observations = [_iso(start + timedelta(days=days)) for days in (0, 7, 14, 21, 42, 63, 84)]
    with tempfile.TemporaryDirectory(prefix="terrarium-season-a-") as a, tempfile.TemporaryDirectory(prefix="terrarium-season-b-") as b:
        state_a, events_a, integrity_a = _run_history(a, observations)
        state_b, events_b, integrity_b = _run_history(b, observations)

    transition_states = []
    # Reconstruct the intended compact cadence directly from the epoch; this is independent of renderer uptime.
    for days in (0, 7, 14, 21, 42, 63, 84):
        transition_states.append(seasonal_clock_for(FIRST_OBSERVED, _iso(start + timedelta(days=days)), migration_origin="eval"))

    # Iteration 9 may use prior seasonal context only when a stored consequence becomes a later opportunity.
    # Before any consequence can become eligible, contrasting seasons must leave ordinary behavior/state identical.
    spring_state = initial_state(1701, created_at=CREATED_AT)
    winter_state = deepcopy(spring_state)
    spring_state["habitat"]["seasonal_clock"] = seasonal_clock_for(CREATED_AT, _iso(datetime(2026, 1, 3, tzinfo=timezone.utc)), migration_origin="eval")
    winter_state["habitat"]["seasonal_clock"] = seasonal_clock_for(CREATED_AT, _iso(datetime(2026, 3, 8, tzinfo=timezone.utc)), migration_origin="eval")
    spring_obs = datetime.fromisoformat(spring_state["habitat"]["seasonal_clock"]["observed_at_utc"].replace("Z", "+00:00"))
    winter_obs = datetime.fromisoformat(winter_state["habitat"]["seasonal_clock"]["observed_at_utc"].replace("Z", "+00:00"))
    sim = Simulation()
    for i in range(60):
        _, _, _, spring_state = sim.step(spring_state, observed_at_utc=_iso(spring_obs + timedelta(seconds=3 * (i + 1))))
        _, _, _, winter_state = sim.step(winter_state, observed_at_utc=_iso(winter_obs + timedelta(seconds=3 * (i + 1))))

    fixtures = build_fixtures()
    seasonal_review = fixtures.get("seasonal_review", {})
    manifest = json.loads((ROOT / "display/art/manifest.json").read_text(encoding="utf-8"))
    palette = json.loads((ROOT / "display/art/palettes/materials.json").read_text(encoding="utf-8"))
    js = (ROOT / "display/web/app.js").read_text(encoding="utf-8")
    ids = {entry["id"] for entry in manifest["assets"]}
    required_assets = {
        "environment.window-spring-blossom", "environment.window-summer-canopy", "environment.window-autumn-leaves",
        "environment.window-winter-view", "environment.window-winter-branches",
    }
    expected_cadence = [
        ("spring", "early", 0), ("spring", "full", 0), ("spring", "late", 0),
        ("summer", "early", 0), ("autumn", "early", 0), ("winter", "early", 0), ("spring", "early", 1),
    ]
    actual_cadence = [(c["season"], c["stage"], c["cycle_index"]) for c in transition_states]
    checks = {
        "canonical_schema_present": state_a["habitat"]["seasonal_clock"]["schema"] == SEASONAL_CLOCK_SCHEMA,
        "production_cadence_21_days": SEASON_DAYS == 21 and state_a["habitat"]["seasonal_clock"]["cadence_days_per_season"] == 21,
        "three_discrete_7_day_stages": SEASON_STAGE_DAYS == 7 and tuple(SEASON_STAGES) == ("early", "full", "late"),
        "cadence_boundaries_exact": actual_cadence == expected_cadence,
        "migration_starts_at_first_observation": migration_after["habitat"]["seasonal_clock"]["epoch_utc"] == FIRST_OBSERVED and migration_after["habitat"]["seasonal_clock"]["season"] == "spring" and migration_after["habitat"]["seasonal_clock"]["stage"] == "early",
        "migration_preserves_existing_world": canonical_json(preserved_before) == canonical_json(preserved_after),
        "replay_exact_after_migration": integrity_a["replay"]["ok"],
        "restart_exact_after_migration": integrity_a["restart_exact"],
        "equivalent_seed_history_exact": canonical_json(state_a) == canonical_json(state_b) and canonical_json(events_a) == canonical_json(events_b) and integrity_b["replay"]["ok"],
        "renderer_uptime_not_authority": transition_states[-1]["cycle_index"] == 1 and "performance.now" not in (ROOT / "terrarium/models.py").read_text(encoding="utf-8"),
        "weather_authority_unchanged": "def weather_for(world_minutes: int, seed: int)" in (ROOT / "terrarium/models.py").read_text(encoding="utf-8"),
        "base_behavior_unaffected_before_consequence_eligibility": (
            canonical_json({k: v for k, v in _without_season(spring_state).items() if k != "habitat"} | {"habitat": {k: v for k, v in _without_season(spring_state)["habitat"].items() if k != "consequence_memory"}})
            == canonical_json({k: v for k, v in _without_season(winter_state).items() if k != "habitat"} | {"habitat": {k: v for k, v in _without_season(winter_state)["habitat"].items() if k != "consequence_memory"}})
        ),
        "all_four_visual_seasons_fixture_backed": all(f"season_{name}_day" in fixtures["scenarios"] for name in SEASONS),
        "seasonal_review_is_broad": len(set(seasonal_review.values())) >= 20,
        "seasonal_assets_authored": required_assets <= ids,
        "seasonal_palette_treatments_present": set(palette.get("season_treatments", {})) == set(SEASONS),
        "renderer_uses_canonical_season": "seasonalState(f)" in js and "seasonPaletteName" in js and "frame.season" in js,
        "missing_authority_stays_neutral": "const raw=f?.season;" in js and "?raw.name:null" in js and "if(!season)return weatherPaletteName(baseName,weather)" in js,
        "winter_uses_sparse_authored_view": "environment.window-winter-view" in js and "environment.window-winter-branches" in js,
        "no_renderer_randomness_or_soft_filters": all(token not in js for token in ("Math.random", "createLinearGradient", "createRadialGradient", "shadowBlur", "ctx.filter", "displayCtx.filter", "rgba(")),
    }
    return {
        "schema": "terrarium.seasonal-evaluation.v1",
        "passed": all(checks.values()),
        "checks": checks,
        "cadence": {"days_per_season": SEASON_DAYS, "stage_days": SEASON_STAGE_DAYS, "seasons": list(SEASONS), "stages": list(SEASON_STAGES)},
        "boundary_states": transition_states,
        "seasonal_review": seasonal_review,
        "authored_asset_count": len(manifest["assets"]),
        "rules_version": RULES_VERSION,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="artifacts/pixel-art-overhaul-iteration8f-seasons.json")
    args = parser.parse_args()
    result = evaluate()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
