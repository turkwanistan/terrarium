extends Node2D

const VARIANT_TEXTURES := {
    "spring_day": "res://art/hero_spring_day.png",
    "rain": "res://art/hero_rain.png",
    "winter_warm_night": "res://art/hero_winter_night.png",
}
const MOTIONS := ["idle", "walk", "inspect"]

var variant := "spring_day"
var motion := "idle"
var manual_ms := -1
var capture_path := ""
var started_ms := 0
var frame_index := -1

func _ready() -> void:
    _parse_args()
    $Foreground.texture = load("res://art/hero_foreground.png")
    _apply_variant()
    started_ms = Time.get_ticks_msec()
    _present(0 if manual_ms < 0 else manual_ms)
    if not capture_path.is_empty():
        call_deferred("_capture_and_quit")

func _process(_delta: float) -> void:
    if manual_ms >= 0:
        return
    var elapsed := Time.get_ticks_msec() - started_ms
    _present(elapsed)

func _input(event: InputEvent) -> void:
    if event.is_action_pressed("ui_accept"):
        var idx := (MOTIONS.find(motion) + 1) % MOTIONS.size()
        motion = MOTIONS[idx]
        started_ms = Time.get_ticks_msec()
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
        i += 1
    if not VARIANT_TEXTURES.has(variant):
        printerr("TERRARIUM_HERO_GATE bad variant: " + variant)
        get_tree().quit(2)
    if not MOTIONS.has(motion):
        printerr("TERRARIUM_HERO_GATE bad motion: " + motion)
        get_tree().quit(2)

func _apply_variant() -> void:
    $Background.texture = load(VARIANT_TEXTURES[variant])
    if variant == "winter_warm_night":
        $Actor.modulate = Color(0.95, 0.91, 0.88, 1.0)
    elif variant == "rain":
        $Actor.modulate = Color(0.90, 0.96, 0.96, 1.0)
    else:
        $Actor.modulate = Color.WHITE

func _present(elapsed_ms: int) -> void:
    var next_frame := int(elapsed_ms / 180) % 4
    if next_frame == frame_index and motion != "walk":
        return
    frame_index = next_frame
    var actor_path := ""
    match motion:
        "walk":
            actor_path = "res://art/moss_walk_%d.png" % next_frame
            var cycle := elapsed_ms % 2600
            var forward := cycle <= 1300
            var t := float(cycle if forward else 2600 - cycle) / 1300.0
            $Actor.position = Vector2(round(147.0 + 139.0 * t), 157)
            $Actor.flip_h = not forward
        "inspect":
            actor_path = "res://art/moss_inspect_%d.png" % next_frame
            $Actor.position = Vector2(249, 157)
            $Actor.flip_h = false
        _:
            actor_path = "res://art/moss_idle_%d.png" % next_frame
            $Actor.position = Vector2(217, 157)
            $Actor.flip_h = false
    $Actor.texture = load(actor_path)

func _capture_and_quit() -> void:
    RenderingServer.force_draw(false)
    var image := get_viewport().get_texture().get_image()
    var w := image.get_width()
    var h := image.get_height()
    if not ((w == 400 and h == 240) or (w == 800 and h == 480)):
        printerr("TERRARIUM_HERO_GATE unexpected viewport %sx%s" % [w, h])
        get_tree().quit(3)
        return
    var absolute_path := capture_path
    if capture_path.begins_with("res://") or capture_path.begins_with("user://"):
        absolute_path = ProjectSettings.globalize_path(capture_path)
    DirAccess.make_dir_recursive_absolute(absolute_path.get_base_dir())
    var err := image.save_png(absolute_path)
    if err != OK:
        printerr("TERRARIUM_HERO_GATE save_png=%s" % err)
        get_tree().quit(4)
        return
    print("TERRARIUM_HERO_GATE_CAPTURE variant=%s motion=%s manual_ms=%s output=%sx%s sha256=%s path=%s" % [variant, motion, manual_ms, w, h, FileAccess.get_sha256(absolute_path), absolute_path])
    get_tree().quit(0)
