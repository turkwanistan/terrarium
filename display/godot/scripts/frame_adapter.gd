extends Node
class_name TerrariumFrameAdapter

signal frame_ready(previous_frame, current_frame)
signal frame_error(message)

const FRAME_SCHEMA := "terrarium.frame.v1"
const LOGICAL_WIDTH := 800
const LOGICAL_HEIGHT := 480

var previous_frame = null
var current_frame = null
var _http: HTTPRequest
var _timer: Timer
var _api_url := ""

func _ready():
    _http = HTTPRequest.new()
    add_child(_http)
    _http.request_completed.connect(_on_request_completed)
    _timer = Timer.new()
    _timer.wait_time = 3.0
    _timer.one_shot = false
    add_child(_timer)
    _timer.timeout.connect(_fetch_live)

func load_fixture(path: String, scenario_name: String) -> bool:
    if not FileAccess.file_exists(path):
        return _fail("fixture file missing: %s" % path)
    var payload = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(payload) != TYPE_DICTIONARY:
        return _fail("fixture JSON is not an object")
    if payload.get("schema") != "terrarium.godot-fixtures.v1":
        return _fail("unsupported fixture pack schema")
    var scenarios = payload.get("scenarios", {})
    if not scenarios.has(scenario_name):
        return _fail("unknown fixture scenario: %s" % scenario_name)
    var scenario = scenarios[scenario_name]
    var source = scenario.get("source")
    var target = scenario.get("target")
    if not _validate_frame(source) or not _validate_frame(target):
        return false
    previous_frame = source
    current_frame = target
    frame_ready.emit(previous_frame, current_frame)
    return true

func start_live(api_url: String) -> void:
    _api_url = api_url.rstrip("/")
    _fetch_live()
    _timer.start()

func stop_live() -> void:
    _timer.stop()

func _fetch_live() -> void:
    if _api_url.is_empty():
        return
    var err = _http.request(_api_url + "/api/frame", [], HTTPClient.METHOD_GET)
    if err != OK:
        _fail("unable to start GET /api/frame: %s" % err)

func _on_request_completed(result, response_code, _headers, body) -> void:
    if result != HTTPRequest.RESULT_SUCCESS or response_code != 200:
        _fail("GET /api/frame failed: result=%s status=%s" % [result, response_code])
        return
    var parsed = JSON.parse_string(body.get_string_from_utf8())
    if not _validate_frame(parsed):
        return
    previous_frame = current_frame
    current_frame = parsed
    frame_ready.emit(previous_frame, current_frame)

func _validate_frame(frame) -> bool:
    if typeof(frame) != TYPE_DICTIONARY:
        return _fail("frame is not an object")
    if frame.get("schema") != FRAME_SCHEMA:
        return _fail("frame schema mismatch: %s" % frame.get("schema"))
    if int(frame.get("logical_width", -1)) != LOGICAL_WIDTH or int(frame.get("logical_height", -1)) != LOGICAL_HEIGHT:
        return _fail("frame logical dimensions must remain 800x480")
    if typeof(frame.get("creature")) != TYPE_DICTIONARY:
        return _fail("frame creature payload missing")
    if typeof(frame.get("objects")) != TYPE_ARRAY:
        return _fail("frame objects payload missing")
    return true

func _fail(message: String) -> bool:
    push_error("TerrariumFrameAdapter: " + message)
    frame_error.emit(message)
    return false
