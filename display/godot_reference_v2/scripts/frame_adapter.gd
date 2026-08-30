extends Node
class_name TerrariumReferenceFrameAdapter

signal frame_ready(previous_frame, frame)
signal frame_error(message)
signal request_state(state)

const FRAME_SCHEMA := "terrarium.frame.v1"
const LOGICAL_WIDTH := 800
const LOGICAL_HEIGHT := 480
const DEFAULT_POLL_SECONDS := 3.0
const MIN_POLL_SECONDS := 0.1

var _http: HTTPRequest
var _timer: Timer
var _api_url := ""
var _current_frame = null
var _request_in_flight := false
var _request_started_ms := 0

func _ready() -> void:
    _http = HTTPRequest.new()
    add_child(_http)
    _http.request_completed.connect(_on_request_completed)
    _timer = Timer.new()
    _timer.wait_time = DEFAULT_POLL_SECONDS
    _timer.one_shot = false
    add_child(_timer)
    _timer.timeout.connect(_fetch_live)

func start_live(api_url: String, poll_seconds: float = DEFAULT_POLL_SECONDS) -> void:
    _api_url = api_url.rstrip("/")
    _timer.wait_time = maxf(poll_seconds, MIN_POLL_SECONDS)
    _fetch_live()
    _timer.start()

func stop_live() -> void:
    _timer.stop()
    if _request_in_flight:
        _http.cancel_request()
        _request_in_flight = false

func _fetch_live() -> void:
    if _api_url.is_empty():
        return
    if _request_in_flight:
        request_state.emit({
            "phase": "skipped_in_flight",
            "at_ms": Time.get_ticks_msec(),
        })
        return
    _request_started_ms = Time.get_ticks_msec()
    var err := _http.request(_api_url + "/api/frame", [], HTTPClient.METHOD_GET)
    if err != OK:
        request_state.emit({
            "phase": "start_error",
            "at_ms": Time.get_ticks_msec(),
            "error": int(err),
        })
        _fail("unable to start GET /api/frame: %s" % err)
        return
    _request_in_flight = true
    request_state.emit({
        "phase": "started",
        "at_ms": _request_started_ms,
    })

func _on_request_completed(result, response_code, _headers, body) -> void:
    var completed_ms := Time.get_ticks_msec()
    var elapsed_ms := maxi(0, completed_ms - _request_started_ms)
    _request_in_flight = false
    request_state.emit({
        "phase": "completed",
        "at_ms": completed_ms,
        "elapsed_ms": elapsed_ms,
        "result": int(result),
        "status": int(response_code),
    })
    if result != HTTPRequest.RESULT_SUCCESS or response_code != 200:
        _fail("GET /api/frame failed: result=%s status=%s" % [result, response_code])
        return
    var frame = JSON.parse_string(body.get_string_from_utf8())
    if not _validate_frame(frame):
        return
    var tick := int(frame.get("tick", -1))
    if _current_frame != null:
        var current_tick := int(_current_frame.get("tick", -1))
        if tick <= current_tick:
            request_state.emit({
                "phase": "ignored_tick",
                "at_ms": completed_ms,
                "tick": tick,
                "current_tick": current_tick,
                "reason": "duplicate" if tick == current_tick else "older",
            })
            return
    var previous_frame = _current_frame
    _current_frame = frame
    request_state.emit({
        "phase": "accepted",
        "at_ms": completed_ms,
        "tick": tick,
    })
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
    if int(frame.get("tick", -1)) < 0:
        return _fail("frame tick missing")
    return true

func _fail(message: String) -> bool:
    push_error("TerrariumReferenceFrameAdapter: " + message)
    frame_error.emit(message)
    return false
