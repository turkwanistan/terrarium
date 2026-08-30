extends Node2D

const FrameAdapter = preload("res://scripts/frame_adapter.gd")
const AmbientOverlay = preload("res://scripts/ambient_overlay.gd")

const VARIANT_TEXTURES := {
    "spring_day": "res://art/hero_spring_day.png",
    "rain": "res://art/hero_rain.png",
    "winter_warm_night": "res://art/hero_winter_night.png",
}
const MOTION_FRAMES := {
    "idle": ["res://art/moss_idle_0.png"],
    "walk": ["res://art/moss_walk_0.png", "res://art/moss_walk_1.png", "res://art/moss_walk_2.png", "res://art/moss_walk_3.png"],
    "inspect": ["res://art/moss_inspect_0.png", "res://art/moss_inspect_1.png", "res://art/moss_inspect_2.png", "res://art/moss_inspect_3.png"],
    "nudge": ["res://art/moss_nudge_0.png", "res://art/moss_nudge_1.png", "res://art/moss_nudge_2.png", "res://art/moss_nudge_3.png", "res://art/moss_nudge_4.png"],
    "rest": ["res://art/moss_rest_0.png"],
    "loaf": ["res://art/moss_loaf_0.png"],
    "groom": ["res://art/moss_groom_0.png", "res://art/moss_groom_1.png", "res://art/moss_groom_2.png", "res://art/moss_groom_3.png"],
    "stretch": ["res://art/moss_stretch_0.png", "res://art/moss_stretch_1.png", "res://art/moss_stretch_2.png", "res://art/moss_stretch_3.png"],
    "sleep": ["res://art/moss_sleep_0.png", "res://art/moss_sleep_1.png", "res://art/moss_sleep_2.png", "res://art/moss_sleep_3.png", "res://art/moss_sleep_4.png"],
    "wake": ["res://art/moss_wake_0.png", "res://art/moss_wake_1.png", "res://art/moss_wake_2.png", "res://art/moss_wake_3.png"],
    "carry": ["res://art/moss_carry_0.png", "res://art/moss_carry_1.png", "res://art/moss_carry_2.png", "res://art/moss_carry_3.png", "res://art/moss_carry_4.png"],
    "place": ["res://art/moss_place_0.png", "res://art/moss_place_1.png", "res://art/moss_place_2.png", "res://art/moss_place_3.png", "res://art/moss_place_4.png"],
    "look": ["res://art/moss_look_0.png", "res://art/moss_look_1.png"],
    "window_watch": ["res://art/moss_window_watch_0.png", "res://art/moss_window_watch_1.png"],
}
const MOTION_ORDER := ["idle", "walk", "inspect", "nudge", "rest", "loaf", "groom", "stretch", "sleep", "wake", "carry", "place", "look", "window_watch"]
const MOTION_STEP_MS := {
    "walk": 180,
    "inspect": 260,
    "nudge": 420,
    "groom": 575,
    "stretch": 525,
    "sleep": 320,
    "wake": 300,
    "carry": 380,
    "place": 260,
    "look": 650,
    "window_watch": 500,
}

# Explicit presentation mapping for canonical activities. Pickup is intentionally absent: canonical
# `carry` owns object transfer, while its presentation motion stages the authored pickup sequence once.
const CANONICAL_ACTIVITY_TO_MOTION := {
    "idle": "idle",
    "rest": "rest",
    "walk": "walk",
    "explore": "walk",
    "inspect": "inspect",
    "nudge": "nudge",
    "carry": "carry",
    "place": "place",
    "loaf": "loaf",
    "groom": "groom",
    "stretch": "stretch",
    "react": "look",
    "orient": "look",
    "look_outside": "window_watch",
    "window_watch": "window_watch",
    "sleep": "sleep",
    "wake": "wake",
}

# Authored support choreography. Sleep moves from the open-side bed gate onto the mattress; wake
# reverses it and ends at the same visual gate used by canonical sleeping_nook mapping.
const SLEEP_STAGE_POSITIONS := [
    Vector2(123, 139),
    Vector2(95, 108),
    Vector2(82, 100),
    Vector2(72, 105),
    Vector2(72, 105),
]
const WAKE_STAGE_POSITIONS := [
    Vector2(72, 105),
    Vector2(82, 100),
    Vector2(95, 108),
    Vector2(123, 139),
]

# Existing canonical object identities/states mapped to their authored Godot presentation rasters.
# This table chooses visuals only; the frame decides which object is carried/placed and its state.
const LIVE_OBJECT_TEXTURES := {
    "blue_stone": {"settled":"res://art/object_blue_stone_settled.png", "rolled":"res://art/object_blue_stone_rolled.png"},
    "amber_leaf": {"fresh":"res://art/object_amber_leaf_fresh.png", "handled":"res://art/object_amber_leaf_handled.png"},
    "acorn": {"settled":"res://art/object_acorn_settled.png", "rolled":"res://art/object_acorn_rolled.png"},
    "shell": {"handled":"res://art/object_shell_handled.png", "displayed":"res://art/object_shell_displayed.png"},
    "red_thread": {"loose":"res://art/object_red_thread_loose.png", "rumpled":"res://art/object_red_thread_rumpled.png", "nested":"res://art/object_red_thread_nested.png"},
    "glass_star": {"handled":"res://art/object_glass_star_handled.png", "displayed":"res://art/object_glass_star_displayed.png"},
}
const LIVE_OBJECT_DEFAULT_STATES := {
    "blue_stone":"settled", "amber_leaf":"fresh", "acorn":"settled",
    "shell":"handled", "red_thread":"loose", "glass_star":"handled",
}

# Canonical Terrarium uses an 800x480 semantic layout. Reference-v2 intentionally re-authored
# furniture composition, so live coordinates need a presentation-only zone-local transform.
# Canonical zone/position remains authoritative; these anchors only align it to the approved art.
const LIVE_ZONE_CANONICAL_ANCHORS := {
    "sleeping_nook": Vector2(296, 392),
    "window": Vector2(168, 316),
    "open_space": Vector2(405, 378),
    "collection_shelf": Vector2(554, 312),
    "activity_corner": Vector2(554, 372),
}
const LIVE_ZONE_VISUAL_ANCHORS := {
    "sleeping_nook": Vector2(145, 175),
    "window": Vector2(150, 155),
    "open_space": Vector2(225, 190),
    "collection_shelf": Vector2(307, 151),
    "activity_corner": Vector2(286, 151),
}
const LIVE_LOCAL_SCALE := 0.5
const LIVE_TRANSITION_DEFAULT_MS := 2600.0
const LIVE_TRANSITION_MIN_MS := 450.0
const LIVE_TRANSITION_MAX_MS := 2800.0
const LIVE_TRANSITION_INTERVAL_FRACTION := 0.90
const LIVE_SUPPORT_TRANSITION_MS := 450.0
const LIVE_DEBUG_EMIT_MS := 250
const LIVE_MAX_FRAME_STEP_PX := 6.0
const LIVE_VARIANT_CROSSFADE_MS := 4200.0
const LIVE_OBJECT_HALF_SIZE := Vector2(8, 7)
const LIVE_ACTOR_ANCHOR_OFFSET := Vector2(22, 36)
const MOTION_SUSTAIN_LOOPS := {
    "inspect": [1, 2],
    "nudge": [2, 3],
    "groom": [1, 2],
    "stretch": [1, 2],
}
const MOTION_START_FRAME_COUNTS := {
    "inspect": 3,
    "nudge": 4,
    "groom": 3,
    "stretch": 3,
}
const MOTION_RECOVERY_FRAMES := {
    "inspect": 3,
    "nudge": 4,
    "groom": 3,
    "stretch": 3,
}
const MOTION_RECOVERY_MS := 300
const LIVE_NAV_VISUAL_POINTS := {
    "405,378": Vector2(225, 190),
    "300,324": Vector2(165, 170),
    "296,392": Vector2(145, 175),
    "554,326": Vector2(286, 165),
    "168,316": Vector2(150, 155),
    "554,312": Vector2(307, 151),
    "554,372": Vector2(286, 151),
}

var variant := "spring_day"
var motion := "idle"
var manual_ms := -1
var capture_path := ""
var started_ms := 0
var frame_index := -1
var live_mode := false
var api_url := "http://127.0.0.1:8080"
var api_url_explicit := false
var live_position := Vector2.ZERO
var live_facing_left := false
var live_action_object_id := ""
var live_action_object_state := "loose"
var live_frame: Dictionary = {}
var live_route_points: Array = []
var live_transition_started_ms := 0
var live_transition_duration_ms := LIVE_TRANSITION_DEFAULT_MS
var live_motion_started_ms := 0
var live_last_frame_arrival_ms := 0
var live_last_arrival_interval_ms := 0
var live_recovery_motion := ""
var live_recovery_until_ms := 0
var rendered_motion := "idle"
var live_previous_motion := "idle"
var live_motion_entry_actor_position := Vector2.ZERO
var live_debug_enabled := false
var live_poll_seconds := 3.0
var live_debug_last_emit_ms := 0
var live_debug_last_adapter_state: Dictionary = {}
var live_variant_current := ""
var live_variant_from := ""
var live_variant_to := ""
var live_variant_transition_started_ms := 0
var background_blend: Sprite2D
var live_debug_stats := {
    "accepted_frames": 0,
    "motion_changes": 0,
    "motion_continuations": 0,
    "max_accept_jump_px": 0.0,
    "max_accept_jump_tick": -1,
    "max_accept_jump_from_motion": "",
    "max_accept_jump_to_motion": "",
    "max_accept_jump_before": null,
    "max_accept_jump_after": null,
    "max_accept_jump_position_changed": false,
    "max_arrival_target_error_px": 0.0,
    "duplicate_ticks_ignored": 0,
    "older_ticks_ignored": 0,
    "request_overlap_skips": 0,
    "animation_frame_changes": {},
}
var adapter
var action_object: Sprite2D
var bed_occluder: Sprite2D
var ambient_overlay: Node2D
var live_object_sprites: Dictionary = {}

func _ready() -> void:
    _parse_args()
    _configure_web_live_defaults()
    $Foreground.texture = load("res://art/hero_foreground.png")
    action_object = Sprite2D.new()
    action_object.centered = false
    action_object.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    action_object.texture = load("res://art/object_red_thread_loose.png")
    action_object.z_index = 11
    add_child(action_object)
    for object_id in LIVE_OBJECT_TEXTURES:
        var object_sprite := Sprite2D.new()
        object_sprite.centered = false
        object_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        object_sprite.z_index = 6
        object_sprite.visible = false
        live_object_sprites[object_id] = object_sprite
        add_child(object_sprite)
    bed_occluder = Sprite2D.new()
    bed_occluder.centered = false
    bed_occluder.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    bed_occluder.texture = load("res://art/bed_front_lip.png")
    bed_occluder.z_index = 19
    bed_occluder.visible = false
    add_child(bed_occluder)
    background_blend = Sprite2D.new()
    background_blend.centered = false
    background_blend.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    background_blend.z_index = 1
    background_blend.visible = false
    add_child(background_blend)
    ambient_overlay = AmbientOverlay.new()
    ambient_overlay.z_index = 5
    add_child(ambient_overlay)
    live_variant_current = variant
    live_variant_from = variant
    live_variant_to = variant
    $Background.texture = load(VARIANT_TEXTURES[variant])
    $Actor.modulate = _actor_modulate_for_variant(variant)
    started_ms = Time.get_ticks_msec()
    _present(0 if manual_ms < 0 else manual_ms)
    if live_mode:
        adapter = FrameAdapter.new()
        add_child(adapter)
        adapter.frame_ready.connect(_on_live_frame)
        adapter.frame_error.connect(_on_live_error)
        adapter.request_state.connect(_on_adapter_state)
        adapter.start_live(api_url, live_poll_seconds)
    elif not capture_path.is_empty():
        call_deferred("_capture_and_quit")

func _process(_delta: float) -> void:
    var now_ms := Time.get_ticks_msec()
    _update_variant_transition(now_ms)
    if manual_ms >= 0:
        return
    if live_mode:
        if not live_frame.is_empty():
            _present_live(live_frame, now_ms - live_transition_started_ms)
        return
    _present(now_ms - started_ms)

func _input(event: InputEvent) -> void:
    if live_mode:
        return
    if event.is_action_pressed("ui_accept"):
        var idx := (MOTION_ORDER.find(motion) + 1) % MOTION_ORDER.size()
        motion = MOTION_ORDER[idx]
        started_ms = Time.get_ticks_msec()
        frame_index = -1
    elif event is InputEventKey and event.pressed:
        match event.keycode:
            KEY_1:
                variant = "spring_day"
                _apply_variant()
            KEY_2:
                variant = "rain"
                _apply_variant()
            KEY_3:
                variant = "winter_warm_night"
                _apply_variant()

func _parse_args() -> void:
    var args := OS.get_cmdline_user_args()
    var i := 0
    while i < args.size():
        match args[i]:
            "--variant":
                if i + 1 < args.size():
                    variant = args[i + 1]
                    i += 1
            "--motion":
                if i + 1 < args.size():
                    motion = args[i + 1]
                    i += 1
            "--manual-ms":
                if i + 1 < args.size():
                    manual_ms = int(args[i + 1])
                    i += 1
            "--capture":
                if i + 1 < args.size():
                    capture_path = args[i + 1]
                    i += 1
            "--live":
                live_mode = true
            "--api-url":
                if i + 1 < args.size():
                    api_url = args[i + 1]
                    api_url_explicit = true
                    i += 1
        i += 1
    if not VARIANT_TEXTURES.has(variant):
        printerr("TERRARIUM_REFERENCE bad variant: " + variant)
        get_tree().quit(2)
    if not MOTION_FRAMES.has(motion):
        printerr("TERRARIUM_REFERENCE bad motion: " + motion)
        get_tree().quit(2)

func _configure_web_live_defaults() -> void:
    # The exported browser presentation is always a read-only live client. Derive the
    # canonical API origin from the page that served the export so no PC-local Godot
    # install, localhost assumption, or duplicated world configuration is required.
    if not OS.has_feature("web"):
        return
    live_mode = true
    var window = JavaScriptBridge.get_interface("window")
    if window != null:
        live_debug_enabled = str(window.location.search).contains("terrarium_debug=1")
        if live_debug_enabled:
            var requested_poll_ms: float = float(JavaScriptBridge.eval("Number(new URLSearchParams(window.location.search).get('terrarium_poll_ms') || 3000)", true))
            live_poll_seconds = clampf(requested_poll_ms / 1000.0, 0.1, 5.0)
        if not api_url_explicit:
            api_url = str(window.location.origin)

func _apply_variant() -> void:
    if live_variant_current.is_empty():
        live_variant_current = variant
        live_variant_from = variant
        live_variant_to = variant
        $Background.texture = load(VARIANT_TEXTURES[variant])
        $Actor.modulate = _actor_modulate_for_variant(variant)
        return
    if variant == live_variant_to:
        return
    # Start from whichever visual is currently dominant rather than snapping through an
    # intermediate weather/lighting state. The incoming raster crossfades above the existing one.
    live_variant_from = live_variant_current
    live_variant_to = variant
    live_variant_transition_started_ms = Time.get_ticks_msec()
    background_blend.texture = load(VARIANT_TEXTURES[live_variant_to])
    background_blend.modulate = Color(1, 1, 1, 0)
    background_blend.visible = true

func _actor_modulate_for_variant(name: String) -> Color:
    if name == "winter_warm_night":
        return Color(0.95, 0.91, 0.88, 1.0)
    if name == "rain":
        return Color(0.90, 0.96, 0.96, 1.0)
    return Color.WHITE

func _update_variant_transition(now_ms: int) -> void:
    if background_blend == null or not background_blend.visible:
        return
    var elapsed := maxi(0, now_ms - live_variant_transition_started_ms)
    var t := clampf(float(elapsed) / LIVE_VARIANT_CROSSFADE_MS, 0.0, 1.0)
    var eased := t * t * (3.0 - 2.0 * t)
    background_blend.modulate = Color(1, 1, 1, eased)
    $Actor.modulate = _actor_modulate_for_variant(live_variant_from).lerp(_actor_modulate_for_variant(live_variant_to), eased)
    if t >= 1.0:
        $Background.texture = background_blend.texture
        live_variant_current = live_variant_to
        live_variant_from = live_variant_to
        background_blend.visible = false
        background_blend.modulate = Color.WHITE
        $Actor.modulate = _actor_modulate_for_variant(live_variant_current)

func _present(elapsed_ms: int) -> void:
    rendered_motion = motion
    var frames: Array = MOTION_FRAMES[rendered_motion]
    var idx := _frame_for_motion(rendered_motion, elapsed_ms, frames.size())
    if idx != frame_index:
        frame_index = idx
        $Actor.texture = load(frames[idx])
    _place_actor(elapsed_ms)
    _update_support_occlusion()
    _present_action_object()

func _frame_for_motion(motion_name: String, elapsed_ms: int, count: int) -> int:
    if count <= 1:
        return 0
    var step := int(MOTION_STEP_MS.get(motion_name, 240))
    if motion_name == "walk":
        return int(maxi(0, elapsed_ms) / step) % count
    if MOTION_SUSTAIN_LOOPS.has(motion_name):
        var start_count := mini(int(MOTION_START_FRAME_COUNTS[motion_name]), count)
        var start_duration := start_count * step
        if elapsed_ms < start_duration:
            return mini(int(maxi(0, elapsed_ms) / step), start_count - 1)
        var loop_frames: Array = MOTION_SUSTAIN_LOOPS[motion_name]
        if loop_frames.is_empty():
            return start_count - 1
        var loop_index := int((elapsed_ms - start_duration) / step) % loop_frames.size()
        return clampi(int(loop_frames[loop_index]), 0, count - 1)
    # Carry intentionally settles into its stable authored carry pose after pickup; sleep and
    # window-watch intentionally settle into supported quiet holds. These are deliberate holds,
    # not accidental terminal-frame freezes.
    return min(int(maxi(0, elapsed_ms) / step), count - 1)

func _place_actor(elapsed_ms: int) -> void:
    $Actor.flip_h = false
    match motion:
        "walk", "carry":
            var cycle := elapsed_ms % 2600
            var forward := cycle <= 1300
            var t := float(cycle if forward else 2600 - cycle) / 1300.0
            $Actor.position = Vector2(round(145.0 + 116.0 * t), 157)
            $Actor.flip_h = not forward
        "inspect", "nudge", "place":
            $Actor.position = Vector2(244, 157)
        "rest", "loaf":
            $Actor.position = Vector2(184, 161)
        "groom", "stretch":
            $Actor.position = Vector2(204, 157)
        "sleep":
            $Actor.position = SLEEP_STAGE_POSITIONS[clampi(frame_index, 0, SLEEP_STAGE_POSITIONS.size() - 1)]
        "wake":
            $Actor.position = WAKE_STAGE_POSITIONS[clampi(frame_index, 0, WAKE_STAGE_POSITIONS.size() - 1)]
        "window_watch":
            $Actor.position = Vector2(118, 65)
            $Actor.flip_h = true
        "look":
            $Actor.position = Vector2(196, 157)
            $Actor.flip_h = frame_index % 2 == 1
        _:
            $Actor.position = Vector2(196, 157)

func _update_support_occlusion() -> void:
    if bed_occluder != null:
        bed_occluder.visible = rendered_motion in ["sleep", "wake"]

func _sync_live_object_sprites(frame: Dictionary) -> void:
    # Every authoritative persistent object gets its own low-cost sprite. This closes the largest
    # readability gap from first living-world UAT: Moss should approach an object that visibly
    # exists, affect it, and leave it behind in its canonical resulting state.
    for object_id in live_object_sprites:
        live_object_sprites[object_id].visible = false
    for obj in frame.get("objects", []):
        if typeof(obj) != TYPE_DICTIONARY:
            continue
        var object_id := str(obj.get("id", ""))
        if not live_object_sprites.has(object_id) or not LIVE_OBJECT_TEXTURES.has(object_id):
            continue
        var sprite: Sprite2D = live_object_sprites[object_id]
        var state_textures: Dictionary = LIVE_OBJECT_TEXTURES[object_id]
        var fallback_state := str(LIVE_OBJECT_DEFAULT_STATES[object_id])
        var state := str(obj.get("interaction_state", fallback_state))
        var supported_state := state if state_textures.has(state) else fallback_state
        sprite.texture = load(state_textures[supported_state])
        var anchor := _map_semantic_position(float(obj.get("x", 0)), float(obj.get("y", 0)), str(obj.get("zone", "")))
        sprite.position = anchor - LIVE_OBJECT_HALF_SIZE
        sprite.visible = obj.get("carried_by") == null and str(obj.get("state", "placed")) != "carried"

func _refresh_live_object_visibility() -> void:
    if live_frame.is_empty():
        return
    for obj in live_frame.get("objects", []):
        if typeof(obj) != TYPE_DICTIONARY:
            continue
        var object_id := str(obj.get("id", ""))
        if live_object_sprites.has(object_id):
            live_object_sprites[object_id].visible = obj.get("carried_by") == null and str(obj.get("state", "placed")) != "carried"

func _present_action_object() -> void:
    if action_object == null:
        return
    _refresh_live_object_visibility()
    var carrying_now = null
    if live_mode and not live_frame.is_empty():
        var creature = live_frame.get("creature", {})
        if typeof(creature) == TYPE_DICTIONARY:
            carrying_now = creature.get("carrying")
    var interaction_motion := rendered_motion in ["inspect", "nudge", "carry", "place"]
    var attached_travel := rendered_motion == "walk" and (carrying_now != null or motion in ["carry", "place"])
    action_object.visible = interaction_motion or attached_travel
    if live_mode:
        if not LIVE_OBJECT_TEXTURES.has(live_action_object_id):
            action_object.visible = false
        else:
            var state_textures: Dictionary = LIVE_OBJECT_TEXTURES[live_action_object_id]
            var fallback_state := str(LIVE_OBJECT_DEFAULT_STATES[live_action_object_id])
            var supported_state := live_action_object_state if state_textures.has(live_action_object_state) else fallback_state
            action_object.texture = load(state_textures[supported_state])
    if not action_object.visible:
        return
    if live_object_sprites.has(live_action_object_id):
        live_object_sprites[live_action_object_id].visible = false

    var object_anchor := _live_object_anchor(live_action_object_id)
    var attached_position: Vector2 = $Actor.position + (Vector2(5, 27) if $Actor.flip_h else Vector2(45, 27))
    if rendered_motion == "inspect":
        # Inspection never changes authoritative object position; show the actual target beside Moss.
        action_object.position = object_anchor - LIVE_OBJECT_HALF_SIZE
    elif rendered_motion == "nudge":
        # Nudge frames visibly carry the canonical object from event target/contact toward its
        # authoritative post-action result instead of leaving the object implied in the background.
        var event = live_frame.get("last_event", {})
        var start_anchor := object_anchor
        var end_anchor := object_anchor
        if typeof(event) == TYPE_DICTIONARY:
            var zone := str(event.get("to_zone", event.get("from_zone", "")))
            if event.get("target_x") != null and event.get("target_y") != null:
                start_anchor = _map_semantic_position(float(event.get("target_x")), float(event.get("target_y")), zone)
            if event.get("result_x") != null and event.get("result_y") != null:
                end_anchor = _map_semantic_position(float(event.get("result_x")), float(event.get("result_y")), zone)
        var nudge_t := clampf(float(maxi(0, Time.get_ticks_msec() - live_motion_started_ms)) / 1450.0, 0.0, 1.0)
        var nudge_eased := nudge_t * nudge_t * (3.0 - 2.0 * nudge_t)
        action_object.position = start_anchor.lerp(end_anchor, nudge_eased) - LIVE_OBJECT_HALF_SIZE
    elif rendered_motion == "carry":
        # Canonical carry frames already mark the object as attached, so use the event's original
        # target position as the pickup origin; otherwise the first authored reach would start with
        # the object mysteriously already under Moss.
        var pickup_origin := object_anchor
        var event = live_frame.get("last_event", {})
        if typeof(event) == TYPE_DICTIONARY and event.get("target_x") != null and event.get("target_y") != null:
            pickup_origin = _map_semantic_position(float(event.get("target_x")), float(event.get("target_y")), str(event.get("from_zone", "")))
        var pickup_t := clampf(float(frame_index) / 3.0, 0.0, 1.0)
        action_object.position = (pickup_origin - LIVE_OBJECT_HALF_SIZE).lerp(attached_position, pickup_t)
    elif rendered_motion == "place":
        # Placement is the inverse: begin attached, then lower/release into canonical world position.
        var place_t := clampf(float(frame_index) / 3.0, 0.0, 1.0)
        action_object.position = attached_position.lerp(object_anchor - LIVE_OBJECT_HALF_SIZE, place_t)
    elif attached_travel:
        action_object.position = attached_position

func _live_object_anchor(object_id: String) -> Vector2:
    if object_id.is_empty() or live_frame.is_empty():
        return _current_rendered_anchor()
    for obj in live_frame.get("objects", []):
        if typeof(obj) == TYPE_DICTIONARY and str(obj.get("id", "")) == object_id:
            return _map_semantic_position(float(obj.get("x", 0)), float(obj.get("y", 0)), str(obj.get("zone", "")))
    var event = live_frame.get("last_event", {})
    if typeof(event) == TYPE_DICTIONARY and event.get("target_x") != null and event.get("target_y") != null:
        return _map_semantic_position(float(event.get("target_x")), float(event.get("target_y")), str(event.get("from_zone", "")))
    return _current_rendered_anchor()

func _on_live_frame(_previous_frame, frame: Dictionary) -> void:
    var creature: Dictionary = frame.get("creature", {})
    var now_ms := Time.get_ticks_msec()
    var had_live_frame := not live_frame.is_empty()
    var rendered_before := _current_rendered_anchor() if had_live_frame else _map_live_position(creature)
    var actor_before: Vector2 = $Actor.position
    var previous_motion := motion
    var next_motion := _motion_from_creature(creature)
    var motion_changed := live_motion_started_ms <= 0 or next_motion != previous_motion
    var next_position := _map_live_position(creature)
    var position_changed := not had_live_frame or next_position.distance_to(live_position) > 0.01

    if live_last_frame_arrival_ms > 0:
        live_last_arrival_interval_ms = maxi(1, now_ms - live_last_frame_arrival_ms)
    else:
        live_last_arrival_interval_ms = 0
    if not had_live_frame:
        live_transition_duration_ms = LIVE_TRANSITION_DEFAULT_MS
    elif position_changed:
        live_transition_duration_ms = _transition_duration_for_interval(live_last_arrival_interval_ms)
    live_last_frame_arrival_ms = now_ms

    live_recovery_motion = ""
    live_recovery_until_ms = 0
    if motion_changed:
        live_previous_motion = previous_motion
        live_motion_entry_actor_position = actor_before
        if had_live_frame and position_changed and next_motion not in ["walk", "carry"]:
            # The canonical action already happened, but authored anticipation begins only after
            # presentation catches up to the authoritative interaction/support point.
            live_motion_started_ms = now_ms + int(live_transition_duration_ms)
        elif had_live_frame and MOTION_RECOVERY_FRAMES.has(previous_motion):
            live_recovery_motion = previous_motion
            live_recovery_until_ms = now_ms + MOTION_RECOVERY_MS
            live_motion_started_ms = live_recovery_until_ms
        else:
            live_motion_started_ms = now_ms
        frame_index = -1
        live_debug_stats["motion_changes"] = int(live_debug_stats["motion_changes"]) + 1
    else:
        live_debug_stats["motion_continuations"] = int(live_debug_stats["motion_continuations"]) + 1

    motion = next_motion
    variant = _variant_from_frame(frame)
    _read_live_action_object(frame, creature)
    _sync_live_object_sprites(frame)
    live_position = next_position
    live_facing_left = str(creature.get("facing", "right")) == "left"
    if not had_live_frame:
        live_route_points = _build_live_route(frame, rendered_before, false, next_motion)
        live_transition_started_ms = now_ms
    elif position_changed:
        live_route_points = _build_live_route(frame, rendered_before, true, next_motion)
        live_transition_started_ms = now_ms
    # Same-position continuation heartbeats intentionally leave route and transition clock
    # untouched. Reconstructing the canonical route on every heartbeat made Moss repeatedly
    # retrace route segments that were already being presented.
    live_frame = frame
    live_debug_stats["accepted_frames"] = int(live_debug_stats["accepted_frames"]) + 1
    _apply_variant()
    if ambient_overlay != null:
        ambient_overlay.present(frame)

    # First live frame snaps only from the non-authoritative startup placeholder. Every later
    # accepted frame must preserve the actor's actual rendered position exactly.
    var present_elapsed := int(live_transition_duration_ms) if (not had_live_frame or not capture_path.is_empty()) else maxi(0, now_ms - live_transition_started_ms)
    _present_live(frame, present_elapsed)
    if had_live_frame:
        var accept_jump: float = actor_before.distance_to($Actor.position)
        if accept_jump > float(live_debug_stats["max_accept_jump_px"]):
            live_debug_stats["max_accept_jump_px"] = accept_jump
            live_debug_stats["max_accept_jump_tick"] = int(frame.get("tick", -1))
            live_debug_stats["max_accept_jump_from_motion"] = previous_motion
            live_debug_stats["max_accept_jump_to_motion"] = next_motion
            live_debug_stats["max_accept_jump_before"] = _vector_payload(actor_before)
            live_debug_stats["max_accept_jump_after"] = _vector_payload($Actor.position)
            live_debug_stats["max_accept_jump_position_changed"] = position_changed
    _emit_live_debug(true)
    if not capture_path.is_empty():
        call_deferred("_capture_and_quit")

func _transition_duration_for_interval(interval_ms: int) -> float:
    if interval_ms <= 0:
        return LIVE_TRANSITION_DEFAULT_MS
    return clampf(
        float(interval_ms) * LIVE_TRANSITION_INTERVAL_FRACTION,
        LIVE_TRANSITION_MIN_MS,
        LIVE_TRANSITION_MAX_MS
    )

func _current_rendered_anchor() -> Vector2:
    return $Actor.position + LIVE_ACTOR_ANCHOR_OFFSET

func _read_live_action_object(frame: Dictionary, creature: Dictionary) -> void:
    live_action_object_id = ""
    live_action_object_state = "loose"
    var carrying = creature.get("carrying")
    if carrying != null:
        live_action_object_id = str(carrying)
    else:
        var target_object = creature.get("target_object_id")
        if target_object != null:
            live_action_object_id = str(target_object)
        if live_action_object_id.is_empty():
            var event = frame.get("last_event", {})
            if typeof(event) == TYPE_DICTIONARY:
                var event_object = event.get("object_id")
                if event_object != null:
                    live_action_object_id = str(event_object)
    if LIVE_OBJECT_TEXTURES.has(live_action_object_id):
        live_action_object_state = str(LIVE_OBJECT_DEFAULT_STATES[live_action_object_id])
        for obj in frame.get("objects", []):
            if typeof(obj) == TYPE_DICTIONARY and str(obj.get("id", "")) == live_action_object_id:
                live_action_object_state = str(obj.get("interaction_state", live_action_object_state))
                break

func _present_live(_frame: Dictionary, _elapsed_ms: int) -> void:
    var now_ms := Time.get_ticks_msec()
    var actor_before: Vector2 = $Actor.position
    var previous_rendered_motion := rendered_motion
    var transition_elapsed_ms := maxi(0, now_ms - live_transition_started_ms)
    if _elapsed_ms >= int(live_transition_duration_ms):
        transition_elapsed_ms = maxi(transition_elapsed_ms, int(live_transition_duration_ms))
    var travel_active := live_route_points.size() >= 2 and transition_elapsed_ms < live_transition_duration_ms
    rendered_motion = motion
    var rendered_elapsed_ms := maxi(0, now_ms - live_motion_started_ms)
    var forced_recovery_index := -1
    if travel_active and motion != "walk":
        # Travel is a renderer-owned phase of the canonical action. It does not invent a new
        # commitment: it presents the authoritative route before action anticipation.
        rendered_motion = "walk"
        rendered_elapsed_ms = transition_elapsed_ms
    elif not live_recovery_motion.is_empty() and now_ms < live_recovery_until_ms:
        rendered_motion = live_recovery_motion
        forced_recovery_index = int(MOTION_RECOVERY_FRAMES.get(rendered_motion, 0))

    var frames: Array = MOTION_FRAMES[rendered_motion]
    var idx := forced_recovery_index if forced_recovery_index >= 0 else _frame_for_motion(rendered_motion, rendered_elapsed_ms, frames.size())
    idx = clampi(idx, 0, frames.size() - 1)
    $Actor.texture = load(frames[idx])
    if idx != frame_index or rendered_motion != previous_rendered_motion:
        _record_animation_frame(rendered_motion, idx)
    frame_index = idx

    var creature: Dictionary = _frame.get("creature", {})
    var zone := str(creature.get("zone", ""))
    if travel_active:
        var t: float = clampf(float(transition_elapsed_ms) / maxf(live_transition_duration_ms, 1.0), 0.0, 1.0)
        var eased := t * t * t * (t * (t * 6.0 - 15.0) + 10.0)
        var actor_base := _route_position(live_route_points, eased)
        var earlier := _route_position(live_route_points, maxf(0.0, eased - 0.02))
        var facing_left := live_facing_left
        if absf(actor_base.x - earlier.x) >= 0.5:
            facing_left = actor_base.x < earlier.x
        $Actor.position = Vector2(round(actor_base.x - LIVE_ACTOR_ANCHOR_OFFSET.x), round(actor_base.y - LIVE_ACTOR_ANCHOR_OFFSET.y))
        $Actor.flip_h = facing_left
    # Action-specific support/perch staging remains presentation-only. Sleep travel stops at the
    # canonical bed gate, so authored sleep frame 0 begins at the exact same rendered position.
    elif rendered_motion == "sleep" and zone == "sleeping_nook":
        $Actor.position = SLEEP_STAGE_POSITIONS[clampi(idx, 0, SLEEP_STAGE_POSITIONS.size() - 1)]
        $Actor.flip_h = live_facing_left
    elif rendered_motion == "wake" and zone == "sleeping_nook":
        $Actor.position = WAKE_STAGE_POSITIONS[clampi(idx, 0, WAKE_STAGE_POSITIONS.size() - 1)]
        $Actor.flip_h = live_facing_left
    elif rendered_motion == "window_watch" and zone == "window":
        var perch := Vector2(118, 65)
        if live_previous_motion != "window_watch" and rendered_elapsed_ms < LIVE_SUPPORT_TRANSITION_MS:
            var support_t := clampf(float(rendered_elapsed_ms) / LIVE_SUPPORT_TRANSITION_MS, 0.0, 1.0)
            var support_eased := support_t * support_t * (3.0 - 2.0 * support_t)
            var support_position := live_motion_entry_actor_position.lerp(perch, support_eased)
            $Actor.position = Vector2(round(support_position.x), round(support_position.y))
        else:
            $Actor.position = perch
        $Actor.flip_h = true
    elif live_previous_motion == "window_watch" and motion != "window_watch" and rendered_elapsed_ms < LIVE_SUPPORT_TRANSITION_MS:
        var floor_actor := Vector2(round(live_position.x - LIVE_ACTOR_ANCHOR_OFFSET.x), round(live_position.y - LIVE_ACTOR_ANCHOR_OFFSET.y))
        var exit_t := clampf(float(rendered_elapsed_ms) / LIVE_SUPPORT_TRANSITION_MS, 0.0, 1.0)
        var exit_eased := exit_t * exit_t * (3.0 - 2.0 * exit_t)
        var exit_position := live_motion_entry_actor_position.lerp(floor_actor, exit_eased)
        $Actor.position = Vector2(round(exit_position.x), round(exit_position.y))
        $Actor.flip_h = live_facing_left
    else:
        var actor_base := live_position
        $Actor.position = Vector2(round(actor_base.x - LIVE_ACTOR_ANCHOR_OFFSET.x), round(actor_base.y - LIVE_ACTOR_ANCHOR_OFFSET.y))
        $Actor.flip_h = live_facing_left
        if transition_elapsed_ms >= live_transition_duration_ms:
            var target_error := _current_rendered_anchor().distance_to(live_position)
            live_debug_stats["max_arrival_target_error_px"] = maxf(float(live_debug_stats["max_arrival_target_error_px"]), target_error)

    _limit_live_render_step(actor_before)
    _update_support_occlusion()
    _present_action_object()
    _emit_live_debug(false)


func _limit_live_render_step(actor_before: Vector2) -> void:
    # Time-based interpolation is normally sub-pixel-to-a-few-pixels per rendered frame. If a
    # browser frame stalls, never let the next draw consume the entire elapsed interval as one
    # visible jump; subsequent frames catch up smoothly and future canonical heartbeats rebase
    # from the actual rendered anchor. First-frame startup and deterministic captures may snap.
    if not live_mode or int(live_debug_stats.get("accepted_frames", 0)) <= 1 or not capture_path.is_empty():
        return
    var delta: Vector2 = $Actor.position - actor_before
    var distance: float = delta.length()
    if distance > LIVE_MAX_FRAME_STEP_PX:
        $Actor.position = actor_before + delta / distance * LIVE_MAX_FRAME_STEP_PX

func _record_animation_frame(motion_name: String, idx: int) -> void:
    var changes: Dictionary = live_debug_stats["animation_frame_changes"]
    var key := "%s:%d" % [motion_name, idx]
    changes[key] = int(changes.get(key, 0)) + 1
    live_debug_stats["animation_frame_changes"] = changes

func _build_live_route(frame: Dictionary, rendered_start: Vector2, use_rendered_start: bool, motion_name: String) -> Array:
    var result: Array = []
    if use_rendered_start:
        result.append(rendered_start)
    var event = frame.get("last_event", {})
    var route_items: Array = []
    if typeof(event) == TYPE_DICTIONARY and typeof(event.get("route", [])) == TYPE_ARRAY:
        route_items = event.get("route", [])
        var route_limit := route_items.size()
        # Canonical sleep routes end inside the bed. The penultimate route point is the authored
        # open-side bed gate; the sleep action itself presents the final supported move inward.
        if motion_name == "sleep" and route_limit >= 2:
            route_limit -= 1
        for i in range(route_limit):
            var route_item = route_items[i]
            if typeof(route_item) == TYPE_DICTIONARY:
                result.append(_map_live_route_point(route_item))
    var target := _map_live_position(frame.get("creature", {}))
    if motion_name == "sleep" and route_items.size() >= 2:
        var support_gate = route_items[route_items.size() - 2]
        if typeof(support_gate) == TYPE_DICTIONARY:
            target = _map_live_route_point(support_gate)
    if result.is_empty() or result[-1].distance_to(target) > 0.01:
        result.append(target)
    var deduped: Array = []
    for point in result:
        if deduped.is_empty() or deduped[-1].distance_to(point) > 0.01:
            deduped.append(point)
    return deduped

func _map_live_route_point(item: Dictionary) -> Vector2:
    var semantic := Vector2(float(item.get("x", 0)), float(item.get("y", 0)))
    var key := "%d,%d" % [int(round(semantic.x)), int(round(semantic.y))]
    if LIVE_NAV_VISUAL_POINTS.has(key):
        return LIVE_NAV_VISUAL_POINTS[key]
    var best_zone := ""
    var best_distance := INF
    for zone in LIVE_ZONE_CANONICAL_ANCHORS:
        var canonical_anchor: Vector2 = LIVE_ZONE_CANONICAL_ANCHORS[zone]
        var distance: float = semantic.distance_squared_to(canonical_anchor)
        if distance < best_distance:
            best_distance = distance
            best_zone = str(zone)
    if not best_zone.is_empty():
        var canonical_anchor: Vector2 = LIVE_ZONE_CANONICAL_ANCHORS[best_zone]
        var visual_anchor: Vector2 = LIVE_ZONE_VISUAL_ANCHORS[best_zone]
        return visual_anchor + (semantic - canonical_anchor) * LIVE_LOCAL_SCALE
    return semantic * 0.5

func _route_position(points: Array, t: float) -> Vector2:
    if points.size() < 2:
        return points[0] if not points.is_empty() else live_position
    var lengths: Array = []
    var total: float = 0.0
    for i in range(points.size() - 1):
        var length: float = points[i].distance_to(points[i + 1])
        lengths.append(length)
        total += length
    if total <= 0.001:
        return points[-1]
    var wanted: float = total * clampf(t, 0.0, 1.0)
    var traversed: float = 0.0
    for i in range(lengths.size()):
        var segment_length: float = float(lengths[i])
        if wanted <= traversed + segment_length:
            var local_t: float = (wanted - traversed) / maxf(segment_length, 0.001)
            return points[i].lerp(points[i + 1], local_t)
        traversed += segment_length
    return points[-1]

func _map_semantic_position(x: float, y: float, zone: String) -> Vector2:
    var semantic := Vector2(x, y)
    if LIVE_ZONE_CANONICAL_ANCHORS.has(zone) and LIVE_ZONE_VISUAL_ANCHORS.has(zone):
        var canonical_anchor: Vector2 = LIVE_ZONE_CANONICAL_ANCHORS[zone]
        var visual_anchor: Vector2 = LIVE_ZONE_VISUAL_ANCHORS[zone]
        var local_offset := (semantic - canonical_anchor) * LIVE_LOCAL_SCALE
        return Vector2(round(visual_anchor.x + local_offset.x), round(visual_anchor.y + local_offset.y))
    return Vector2(round(semantic.x * 0.5), round(semantic.y * 0.5))

func _map_live_position(creature: Dictionary) -> Vector2:
    return _map_semantic_position(
        float(creature.get("x", 400)),
        float(creature.get("y", 320)),
        str(creature.get("zone", ""))
    )

func _variant_from_frame(frame: Dictionary) -> String:
    var weather := str(frame.get("weather", "clear"))
    var lighting := str(frame.get("lighting", "day"))
    var season := str(frame.get("season", {}).get("name", "spring"))
    # The current candidate has one strong authored night treatment. Use it for any canonical
    # night rather than falsely presenting a live night frame as daylight; season-specific night
    # variants can replace this fallback without changing simulation authority.
    if lighting == "night":
        return "winter_warm_night"
    if weather == "rain":
        return "rain"
    return "spring_day"

func _motion_from_creature(creature: Dictionary) -> String:
    var activity := str(creature.get("activity", "idle"))
    var pose := str(creature.get("pose", activity))
    # Carrying is authoritative and remains visible during canonical travel/continuation.
    if creature.get("carrying") != null and activity != "place":
        return "carry"
    if activity == "sleep" or pose.begins_with("sleep"):
        return "sleep"
    if activity == "wake" or pose.begins_with("wake"):
        return "wake"
    return str(CANONICAL_ACTIVITY_TO_MOTION.get(activity, "idle"))

func _on_adapter_state(state) -> void:
    if typeof(state) != TYPE_DICTIONARY:
        return
    live_debug_last_adapter_state = state.duplicate(true)
    var phase := str(state.get("phase", ""))
    if phase == "skipped_in_flight":
        live_debug_stats["request_overlap_skips"] = int(live_debug_stats["request_overlap_skips"]) + 1
    elif phase == "ignored_tick":
        if str(state.get("reason", "")) == "older":
            live_debug_stats["older_ticks_ignored"] = int(live_debug_stats["older_ticks_ignored"]) + 1
        else:
            live_debug_stats["duplicate_ticks_ignored"] = int(live_debug_stats["duplicate_ticks_ignored"]) + 1
    _emit_live_debug(true)

func _vector_payload(value: Vector2) -> Dictionary:
    return {"x": snappedf(value.x, 0.001), "y": snappedf(value.y, 0.001)}

func _route_payload() -> Array:
    var result: Array = []
    for point in live_route_points:
        if typeof(point) == TYPE_VECTOR2:
            result.append(_vector_payload(point))
    return result

func _emit_live_debug(force: bool) -> void:
    if not live_debug_enabled or not OS.has_feature("web"):
        return
    var now_ms := Time.get_ticks_msec()
    if not force and now_ms - live_debug_last_emit_ms < LIVE_DEBUG_EMIT_MS:
        return
    live_debug_last_emit_ms = now_ms
    var creature: Dictionary = live_frame.get("creature", {}) if not live_frame.is_empty() else {}
    var event = live_frame.get("last_event", {}) if not live_frame.is_empty() else {}
    var action_visible := action_object != null and action_object.visible
    var payload := {
        "schema": "terrarium.godot-web-debug.v1",
        "tick": int(live_frame.get("tick", -1)) if not live_frame.is_empty() else -1,
        "arrival_interval_ms": live_last_arrival_interval_ms,
        "canonical": {
            "activity": str(creature.get("activity", "")),
            "pose": str(creature.get("pose", "")),
            "zone": str(creature.get("zone", "")),
            "x": creature.get("x"),
            "y": creature.get("y"),
            "facing": str(creature.get("facing", "")),
            "carrying": creature.get("carrying"),
            "target_object_id": creature.get("target_object_id"),
            "last_event_action": str(event.get("action", "")) if typeof(event) == TYPE_DICTIONARY else "",
            "last_event_route": event.get("route", []) if typeof(event) == TYPE_DICTIONARY else [],
        },
        "presentation": {
            "selected_motion": motion,
            "rendered_motion": rendered_motion,
            "motion_started_ms": live_motion_started_ms,
            "motion_elapsed_ms": maxi(0, now_ms - live_motion_started_ms),
            "recovery_motion": live_recovery_motion if now_ms < live_recovery_until_ms else "",
            "transition_started_ms": live_transition_started_ms,
            "transition_elapsed_ms": maxi(0, now_ms - live_transition_started_ms),
            "transition_duration_ms": live_transition_duration_ms,
            "route": _route_payload(),
            "rendered_actor_position": _vector_payload($Actor.position),
            "rendered_actor_anchor": _vector_payload(_current_rendered_anchor()),
            "target_anchor": _vector_payload(live_position),
            "animation_frame": frame_index,
            "facing_left": $Actor.flip_h,
            "action_object_id": live_action_object_id,
            "action_object_state": live_action_object_state,
            "action_object_visible": action_visible,
            "action_object_position": _vector_payload(action_object.position) if action_visible else null,
        },
        "adapter": live_debug_last_adapter_state,
        "stats": live_debug_stats,
    }
    var raw := JSON.stringify(payload)
    var script := "window.__terrariumDebug=%s;let p=document.getElementById('terrarium-debug');if(!p){p=document.createElement('pre');p.id='terrarium-debug';p.style.cssText='position:fixed;left:0;bottom:0;z-index:99999;max-width:100vw;max-height:42vh;overflow:auto;margin:0;padding:6px;background:rgba(0,0,0,.82);color:#d8f3dc;font:11px monospace;white-space:pre-wrap;pointer-events:none';document.body.appendChild(p);}p.textContent=JSON.stringify({godot:window.__terrariumDebug,browser_errors:window.__terrariumBrowserErrors||[]});" % raw
    JavaScriptBridge.eval(script, true)
    if force:
        print("TERRARIUM_WEB_DEBUG " + raw)

func _on_live_error(message) -> void:
    printerr("TERRARIUM_REFERENCE_LIVE_ERROR " + str(message))

func _capture_and_quit() -> void:
    RenderingServer.force_draw(false)
    var image := get_viewport().get_texture().get_image()
    var w := image.get_width()
    var h := image.get_height()
    if not ((w == 400 and h == 240) or (w == 800 and h == 480)):
        printerr("TERRARIUM_REFERENCE unexpected viewport %sx%s" % [w, h])
        get_tree().quit(3)
        return
    var absolute_path := capture_path
    if capture_path.begins_with("res://") or capture_path.begins_with("user://"):
        absolute_path = ProjectSettings.globalize_path(capture_path)
    DirAccess.make_dir_recursive_absolute(absolute_path.get_base_dir())
    var err := image.save_png(absolute_path)
    if err != OK:
        printerr("TERRARIUM_REFERENCE save_png=%s" % err)
        get_tree().quit(4)
        return
    print("TERRARIUM_REFERENCE_CAPTURE variant=%s motion=%s manual_ms=%s output=%sx%s sha256=%s path=%s" % [variant, motion, manual_ms, w, h, FileAccess.get_sha256(absolute_path), absolute_path])
    get_tree().quit(0)
