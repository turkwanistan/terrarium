extends Node

const MANIFEST_PATH := "res://art/slice_manifest.json"
const ANIMATION_PATH := "res://art/moss_animations.json"
const SEMANTIC_SCALE := 0.5
const TRANSITION_MS := 2600.0

var root
var manifest := {}
var animations := {}
var texture_cache := {}
var static_nodes := {}
var object_nodes := {}
var moss_base: Node2D
var moss_sprite: Sprite2D
var carried_sprite: Sprite2D
var warm_light: Sprite2D

func configure(root_node: Node2D) -> void:
    root = root_node
    manifest = _load_json(MANIFEST_PATH)
    animations = _load_json(ANIMATION_PATH)
    _build_static_scene()
    _build_dynamic_scene()

func _load_json(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        push_error("missing presentation resource: " + path)
        return {}
    var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(parsed) != TYPE_DICTIONARY:
        push_error("invalid presentation JSON: " + path)
        return {}
    return parsed

func _texture(path: String):
    if not texture_cache.has(path):
        texture_cache[path] = load(path)
    return texture_cache[path]

func _sprite(path: String, pos: Vector2, parent: Node, name: String) -> Sprite2D:
    var s = Sprite2D.new()
    s.name = name
    s.centered = false
    s.position = pos
    s.texture = _texture(path)
    s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    parent.add_child(s)
    return s

func _build_static_scene() -> void:
    for entry in manifest.get("static", []):
        var layer = str(entry.get("layer", "Structure"))
        var parent = root.get_node(layer)
        var p = entry.get("position", [0, 0])
        var s = _sprite(str(entry["texture"]), Vector2(float(p[0]), float(p[1])), parent, str(entry.get("id", "static")))
        s.z_index = int(entry.get("z", 0))
        static_nodes[str(entry.get("id", ""))] = s
    for entry in manifest.get("y_sorted", []):
        var base = Node2D.new()
        base.name = str(entry.get("id", "prop"))
        var b = entry.get("base", [0, 0])
        var a = entry.get("anchor", [0, 0])
        base.position = Vector2(float(b[0]), float(b[1]))
        var s = _sprite(str(entry["texture"]), Vector2(-float(a[0]), -float(a[1])), base, "Sprite")
        s.z_index = int(entry.get("z", 0))
        root.get_node("World").add_child(base)
    warm_light = static_nodes.get("warm-light")
    if warm_light:
        warm_light.visible = false

func _build_dynamic_scene() -> void:
    moss_base = Node2D.new()
    moss_base.name = "Moss"
    moss_sprite = Sprite2D.new()
    moss_sprite.centered = false
    moss_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    moss_base.add_child(moss_sprite)
    carried_sprite = Sprite2D.new()
    carried_sprite.centered = false
    carried_sprite.position = Vector2(23, -16)
    carried_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    carried_sprite.visible = false
    moss_base.add_child(carried_sprite)
    root.get_node("World").add_child(moss_base)

func present(previous, current: Dictionary, manual_ms: int) -> void:
    _present_environment(current)
    _present_moss(previous, current, manual_ms)
    _present_objects(previous, current, manual_ms)

func _present_environment(frame: Dictionary) -> void:
    var season = str(frame.get("season", {}).get("name", "spring"))
    var window = static_nodes.get("major-window")
    if window:
        window.texture = _texture("res://art/window_winter.png" if season == "winter" else "res://art/window_spring.png")
    if warm_light:
        warm_light.visible = str(frame.get("lighting", "day")) == "night"

func _present_moss(previous, current: Dictionary, manual_ms: int) -> void:
    var c = current["creature"]
    var pos = _semantic_position(c)
    var moving = false
    if previous != null and previous.has("creature"):
        var p = previous["creature"]
        moving = float(p.get("x", 0)) != float(c.get("x", 0)) or float(p.get("y", 0)) != float(c.get("y", 0))
        if moving and str(c.get("activity", "")) == "walk":
            var t = clamp(float(manual_ms) / TRANSITION_MS, 0.0, 1.0)
            pos = _route_position(previous, current, _smoother(t))
    moss_base.position = Vector2(round(pos.x), round(pos.y))
    var activity = str(c.get("activity", "idle"))
    var frame_path = _moss_frame(activity, manual_ms, moving)
    moss_sprite.texture = _texture(frame_path)
    var anchor = animations.get("anchor", [22, 30])
    moss_sprite.position = Vector2(-float(anchor[0]), -float(anchor[1]))
    moss_sprite.flip_h = str(c.get("facing", "right")) == "left"
    carried_sprite.position.x = -31 if moss_sprite.flip_h else 23
    var carrying = c.get("carrying")
    carried_sprite.visible = carrying != null
    if carrying != null:
        carried_sprite.texture = _texture("res://art/object_red_thread_loose.png")

func _moss_frame(activity: String, manual_ms: int, moving: bool) -> String:
    if moving or activity == "walk":
        var walk = animations.get("animations", {}).get("walk", {})
        var frames = walk.get("frames", ["res://art/moss_walk_0.png"])
        var durations = walk.get("durations_ms", [180, 180, 180, 180])
        var total = 0
        for d in durations:
            total += int(d)
        var phase = manual_ms % max(total, 1)
        var cursor = 0
        for i in range(frames.size()):
            cursor += int(durations[min(i, durations.size() - 1)])
            if phase < cursor:
                return _art_path(str(frames[i]))
        return _art_path(str(frames[0]))
    if activity in ["inspect", "nudge", "place"]:
        var contact = animations.get("animations", {}).get("inspect", {})
        var frames = contact.get("frames", ["res://art/moss_inspect_0.png"])
        var idx = 0 if manual_ms < 250 else 1 if manual_ms < 700 else 2 if manual_ms < 1200 else 3
        return _art_path(str(frames[min(idx, frames.size() - 1)]))
    if activity in ["rest", "loaf", "sleep"]:
        return "res://art/moss_loaf.png"
    if activity == "carry":
        return "res://art/moss_carry.png"
    return "res://art/moss_idle.png"

func _art_path(filename: String) -> String:
    return filename if filename.begins_with("res://") else "res://art/" + filename

func _present_objects(previous, current: Dictionary, manual_ms: int) -> void:
    var prior_by_id = {}
    if previous != null:
        for o in previous.get("objects", []):
            prior_by_id[str(o.get("id"))] = o
    for o in current.get("objects", []):
        var oid = str(o.get("id"))
        if oid != "red_thread":
            continue
        if not object_nodes.has(oid):
            var base = Node2D.new()
            base.name = "Object_red_thread"
            var sprite = Sprite2D.new()
            sprite.name = "Sprite"
            sprite.centered = false
            sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
            base.add_child(sprite)
            root.get_node("World").add_child(base)
            object_nodes[oid] = base
        var node: Node2D = object_nodes[oid]
        var sprite: Sprite2D = node.get_node("Sprite")
        node.visible = str(o.get("state", "placed")) != "carried"
        var p = _semantic_position(o)
        var prior = prior_by_id.get(oid)
        var event = current.get("last_event", {})
        if event == null:
            event = {}
        if prior != null and str(event.get("object_id", "")) == oid:
            var t = _smoother(clamp(float(manual_ms) / TRANSITION_MS, 0.0, 1.0))
            p = _semantic_position(prior).lerp(_semantic_position(o), t)
        node.position = Vector2(round(p.x), round(p.y))
        var state = str(o.get("interaction_state", "loose"))
        if prior != null and str(event.get("object_id", "")) == oid and manual_ms < 850:
            state = str(prior.get("interaction_state", state))
        sprite.texture = _texture("res://art/object_red_thread_%s.png" % state)
        sprite.position = Vector2(-8, -8)

func _semantic_position(item: Dictionary) -> Vector2:
    return Vector2(float(item.get("x", 0)) * SEMANTIC_SCALE, float(item.get("y", 0)) * SEMANTIC_SCALE)

func _route_position(previous: Dictionary, current: Dictionary, t: float) -> Vector2:
    var start = _semantic_position(previous["creature"])
    var points = [start]
    var event = current.get("last_event", {})
    if event == null:
        event = {}
    for p in event.get("route", []):
        points.append(Vector2(float(p.get("x", 0)) * SEMANTIC_SCALE, float(p.get("y", 0)) * SEMANTIC_SCALE))
    var target = _semantic_position(current["creature"])
    if points[-1].distance_to(target) > 0.01:
        points.append(target)
    if points.size() < 2:
        return target
    var lengths = []
    var total = 0.0
    for i in range(points.size() - 1):
        var length = points[i].distance_to(points[i + 1])
        lengths.append(length)
        total += length
    if total <= 0.001:
        return target
    var wanted = total * t
    var traversed = 0.0
    for i in range(lengths.size()):
        if wanted <= traversed + lengths[i]:
            var local = (wanted - traversed) / max(lengths[i], 0.001)
            return points[i].lerp(points[i + 1], local)
        traversed += lengths[i]
    return points[-1]

func _smoother(t: float) -> float:
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)
