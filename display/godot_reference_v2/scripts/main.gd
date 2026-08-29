extends Node2D

const FrameAdapter = preload("res://scripts/frame_adapter.gd")

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
const LIVE_TRANSITION_MS := 2600.0
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
var live_motion_started_ms := 0
var adapter
var action_object: Sprite2D
var bed_occluder: Sprite2D

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
    bed_occluder = Sprite2D.new()
    bed_occluder.centered = false
    bed_occluder.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    bed_occluder.texture = load("res://art/bed_front_lip.png")
    bed_occluder.z_index = 19
    bed_occluder.visible = false
    add_child(bed_occluder)
    _apply_variant()
    started_ms = Time.get_ticks_msec()
    _present(0 if manual_ms < 0 else manual_ms)
    if live_mode:
        adapter = FrameAdapter.new()
        add_child(adapter)
        adapter.frame_ready.connect(_on_live_frame)
        adapter.frame_error.connect(_on_live_error)
        adapter.start_live(api_url)
    elif not capture_path.is_empty():
        call_deferred("_capture_and_quit")

func _process(_delta: float) -> void:
    if manual_ms >= 0:
        return
    if live_mode:
        if not live_frame.is_empty():
            _present_live(live_frame, Time.get_ticks_msec() - live_transition_started_ms)
        return
    _present(Time.get_ticks_msec() - started_ms)

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
    if api_url_explicit:
        return
    var window = JavaScriptBridge.get_interface("window")
    if window != null:
        api_url = str(window.location.origin)

func _apply_variant() -> void:
    $Background.texture = load(VARIANT_TEXTURES[variant])
    if variant == "winter_warm_night":
        $Actor.modulate = Color(0.95, 0.91, 0.88, 1.0)
    elif variant == "rain":
        $Actor.modulate = Color(0.90, 0.96, 0.96, 1.0)
    else:
        $Actor.modulate = Color.WHITE

func _present(elapsed_ms: int) -> void:
    var frames: Array = MOTION_FRAMES[motion]
    var idx := _frame_for_motion(elapsed_ms, frames.size())
    if idx != frame_index:
        frame_index = idx
        $Actor.texture = load(frames[idx])
    _place_actor(elapsed_ms)
    _update_support_occlusion()
    _present_action_object()

func _frame_for_motion(elapsed_ms: int, count: int) -> int:
    if count <= 1:
        return 0
    var step := int(MOTION_STEP_MS.get(motion, 240))
    if motion in ["walk", "look"]:
        return int(elapsed_ms / step) % count
    return min(int(elapsed_ms / step), count - 1)

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
        bed_occluder.visible = motion in ["sleep", "wake"]

func _present_action_object() -> void:
    if action_object == null:
        return
    action_object.visible = motion in ["carry", "place"]
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
    if motion == "carry":
        action_object.position = $Actor.position + (Vector2(5, 27) if $Actor.flip_h else Vector2(45, 27))
    else:
        # Presentation-only choreography: canonical state decides that a place action exists;
        # these offsets only make the authored lower -> contact -> release sequence legible.
        var right_offsets := [Vector2(45, 27), Vector2(45, 33), Vector2(43, 38), Vector2(43, 40), Vector2(43, 40)]
        var left_offsets := [Vector2(0, 27), Vector2(0, 33), Vector2(1, 38), Vector2(1, 40), Vector2(1, 40)]
        var place_idx: int = clampi(frame_index, 0, right_offsets.size() - 1)
        action_object.position = $Actor.position + (left_offsets[place_idx] if $Actor.flip_h else right_offsets[place_idx])

func _on_live_frame(previous_frame, frame: Dictionary) -> void:
    var creature: Dictionary = frame.get("creature", {})
    variant = _variant_from_frame(frame)
    var next_motion := _motion_from_creature(creature)
    var now_ms := Time.get_ticks_msec()
    if live_motion_started_ms <= 0 or next_motion != motion:
        live_motion_started_ms = now_ms
        frame_index = -1
    motion = next_motion
    _read_live_action_object(frame, creature)
    live_position = _map_live_position(creature)
    live_facing_left = str(creature.get("facing", "right")) == "left"
    live_route_points = _build_live_route(previous_frame, frame)
    live_frame = frame
    live_transition_started_ms = now_ms
    _apply_variant()
    # Captures represent the authoritative target frame; ordinary live viewing interpolates to it.
    _present_live(frame, int(LIVE_TRANSITION_MS) if not capture_path.is_empty() else 0)
    if not capture_path.is_empty():
        call_deferred("_capture_and_quit")

func _read_live_action_object(frame: Dictionary, creature: Dictionary) -> void:
    live_action_object_id = ""
    live_action_object_state = "loose"
    var carrying = creature.get("carrying")
    if carrying != null:
        live_action_object_id = str(carrying)
    else:
        live_action_object_id = str(creature.get("target_object_id", ""))
        if live_action_object_id.is_empty():
            var event = frame.get("last_event", {})
            if typeof(event) == TYPE_DICTIONARY:
                live_action_object_id = str(event.get("object_id", ""))
    if LIVE_OBJECT_TEXTURES.has(live_action_object_id):
        live_action_object_state = str(LIVE_OBJECT_DEFAULT_STATES[live_action_object_id])
        for obj in frame.get("objects", []):
            if typeof(obj) == TYPE_DICTIONARY and str(obj.get("id", "")) == live_action_object_id:
                live_action_object_state = str(obj.get("interaction_state", live_action_object_state))
                break

func _present_live(_frame: Dictionary, elapsed_ms: int) -> void:
    var frames: Array = MOTION_FRAMES[motion]
    var motion_elapsed_ms: int = maxi(0, Time.get_ticks_msec() - live_motion_started_ms)
    var idx := _frame_for_motion(motion_elapsed_ms, frames.size())
    $Actor.texture = load(frames[idx])
    frame_index = idx
    var creature: Dictionary = _frame.get("creature", {})
    var zone := str(creature.get("zone", ""))
    # Action-specific support/perch staging is presentation-only and already visually validated.
    if motion == "sleep" and zone == "sleeping_nook":
        $Actor.position = SLEEP_STAGE_POSITIONS[clampi(idx, 0, SLEEP_STAGE_POSITIONS.size() - 1)]
        $Actor.flip_h = live_facing_left
    elif motion == "wake" and zone == "sleeping_nook":
        $Actor.position = WAKE_STAGE_POSITIONS[clampi(idx, 0, WAKE_STAGE_POSITIONS.size() - 1)]
        $Actor.flip_h = live_facing_left
    elif motion == "window_watch" and zone == "window":
        $Actor.position = Vector2(118, 65)
        $Actor.flip_h = true
    else:
        var actor_base := live_position
        var facing_left := live_facing_left
        if live_route_points.size() >= 2 and elapsed_ms < LIVE_TRANSITION_MS:
            var t: float = clampf(float(elapsed_ms) / LIVE_TRANSITION_MS, 0.0, 1.0)
            var eased := t * t * (3.0 - 2.0 * t)
            actor_base = _route_position(live_route_points, eased)
            var earlier := _route_position(live_route_points, maxf(0.0, eased - 0.02))
            if absf(actor_base.x - earlier.x) >= 0.5:
                facing_left = actor_base.x < earlier.x
        $Actor.position = Vector2(round(actor_base.x - 22.0), round(actor_base.y - 36.0))
        $Actor.flip_h = facing_left
    _update_support_occlusion()
    _present_action_object()

func _build_live_route(previous_frame, frame: Dictionary) -> Array:
    var result: Array = []
    if typeof(previous_frame) == TYPE_DICTIONARY:
        var previous_creature = previous_frame.get("creature", {})
        if typeof(previous_creature) == TYPE_DICTIONARY:
            result.append(_map_live_position(previous_creature))
    var event = frame.get("last_event", {})
    if typeof(event) == TYPE_DICTIONARY and str(event.get("action", "")) == "walk":
        for route_item in event.get("route", []):
            if typeof(route_item) == TYPE_DICTIONARY:
                result.append(_map_live_route_point(route_item))
    var target := _map_live_position(frame.get("creature", {}))
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

func _map_live_position(creature: Dictionary) -> Vector2:
    var semantic := Vector2(float(creature.get("x", 400)), float(creature.get("y", 320)))
    var zone := str(creature.get("zone", ""))
    if LIVE_ZONE_CANONICAL_ANCHORS.has(zone) and LIVE_ZONE_VISUAL_ANCHORS.has(zone):
        var canonical_anchor: Vector2 = LIVE_ZONE_CANONICAL_ANCHORS[zone]
        var visual_anchor: Vector2 = LIVE_ZONE_VISUAL_ANCHORS[zone]
        var local_offset := (semantic - canonical_anchor) * LIVE_LOCAL_SCALE
        return Vector2(round(visual_anchor.x + local_offset.x), round(visual_anchor.y + local_offset.y))
    # Fail-safe for unknown future zones: preserve the hardware-neutral semantic projection rather
    # than inventing a new destination.
    return Vector2(round(semantic.x * 0.5), round(semantic.y * 0.5))

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
