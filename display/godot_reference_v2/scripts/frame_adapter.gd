extends Node
class_name TerrariumReferenceFrameAdapter

signal frame_ready(previous_frame, frame)
signal frame_error(message)

const FRAME_SCHEMA := "terrarium.frame.v1"
const LOGICAL_WIDTH := 800
const LOGICAL_HEIGHT := 480

var _http: HTTPRequest
var _timer: Timer
var _api_url := ""
var _current_frame = null

func _ready() -> void:
    _http = HTTPRequest.new()
    add_child(_http)
    _http.request_completed.connect(_on_request_completed)
    _timer = Timer.new()
    _timer.wait_time = 3.0
    _timer.one_shot = false
    add_child(_timer)
    _timer.timeout.connect(_fetch_live)

func start_live(api_url: String) -> void:
    _api_url = api_url.rstrip("/")
    _fetch_live()
    _timer.start()

func stop_live() -> void:
    _timer.stop()

func _fetch_live() -> void:
    if _api_url.is_empty():
        return
    var err := _http.request(_api_url + "/api/frame", [], HTTPClient.METHOD_GET)
    if err != OK:
        _fail("unable to start GET /api/frame: %s" % err)

func _on_request_completed(result, response_code, _headers, body) -> void:
    if result != HTTPRequest.RESULT_SUCCESS or response_code != 200:
        _fail("GET /api/frame failed: result=%s status=%s" % [result, response_code])
        return
    var frame = JSON.parse_string(body.get_string_from_utf8())
    if not _validate_frame(frame):
        return
    if _current_frame != null and int(frame.get("tick", -1)) == int(_current_frame.get("tick", -2)):
        return
    var previous_frame = _current_frame
    _current_frame = frame
    frame_ready.emit(previous_frame, frame)

func _validate_frame(frame) -> bool:
    if typeof(frame) != TYPE_DICTIONARY:
        return _fail("frame is not an object")
    if frame.get("schema") != FRAME_SCHEMA:
        return _fail("frame schema mismatch")
    if int(frame.get("logical_width", -1)) != LOGICAL_WIDTH or int(frame.get("logical_height", -1)) != LOGICAL_HEIGHT:
        return _fail("frame logical dimensions must remain 800x480")
    if typeof(frame.get("creature")) != TYPE_DICTIONARY:
        return _fail("frame creature payload missing")
    return true

func _fail(message: String) -> bool:
    push_error("TerrariumReferenceFrameAdapter: " + message)
    frame_error.emit(message)
    return false
