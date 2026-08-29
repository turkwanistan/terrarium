extends Node2D

const FIXTURE_FILE := "res://tests/fixtures/vertical_slice.json"
const DEFAULT_FIXTURE := "spring_clear_idle"
const DEFAULT_MANUAL_MS := 1300

var adapter: TerrariumFrameAdapter
var presenter
var manual_ms := DEFAULT_MANUAL_MS
var capture_path := ""
var fixture_name := DEFAULT_FIXTURE
var live_mode := false
var api_url := "http://127.0.0.1:8080"

func _ready() -> void:
    _parse_args()
    adapter = TerrariumFrameAdapter.new()
    add_child(adapter)
    presenter = $Presenter
    presenter.configure(self)
    adapter.frame_ready.connect(_on_frame_ready)
    adapter.frame_error.connect(_on_frame_error)
    if live_mode:
        adapter.start_live(api_url)
    else:
        if not adapter.load_fixture(FIXTURE_FILE, fixture_name):
            get_tree().quit(2)

func _parse_args() -> void:
    var args = OS.get_cmdline_user_args()
    var i = 0
    while i < args.size():
        match args[i]:
            "--fixture":
                if i + 1 < args.size():
                    fixture_name = args[i + 1]
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
                    i += 1
        i += 1

func _on_frame_ready(previous_frame, current_frame) -> void:
    presenter.present(previous_frame, current_frame, manual_ms)
    $Atmosphere.present(current_frame, manual_ms)
    if not capture_path.is_empty():
        call_deferred("_capture_and_quit")

func _on_frame_error(message) -> void:
    printerr("TERRARIUM_GODOT_FRAME_ERROR " + str(message))

func _capture_and_quit() -> void:
    RenderingServer.force_draw(false)
    var image = get_viewport().get_texture().get_image()
    var output_width = image.get_width()
    var output_height = image.get_height()
    if not ((output_width == 400 and output_height == 240) or (output_width == 800 and output_height == 480)):
        printerr("TERRARIUM_GODOT_CAPTURE_ERROR unexpected viewport %sx%s" % [output_width, output_height])
        get_tree().quit(3)
        return
    var absolute_path = capture_path
    if capture_path.begins_with("res://") or capture_path.begins_with("user://"):
        absolute_path = ProjectSettings.globalize_path(capture_path)
    DirAccess.make_dir_recursive_absolute(absolute_path.get_base_dir())
    var err = image.save_png(absolute_path)
    if err != OK:
        printerr("TERRARIUM_GODOT_CAPTURE_ERROR save_png=%s" % err)
        get_tree().quit(4)
        return
    var sha = FileAccess.get_sha256(absolute_path)
    print("TERRARIUM_GODOT_CAPTURE fixture=%s manual_ms=%s surface=400x240 output=%sx%s sha256=%s path=%s" % [fixture_name, manual_ms, output_width, output_height, sha, absolute_path])
    get_tree().quit(0)
