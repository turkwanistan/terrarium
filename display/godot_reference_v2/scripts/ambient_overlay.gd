extends Node2D

# Lightweight presentation-only ambience. Canonical weather/lighting decides whether an effect is
# active; this node only gives already-authoritative conditions some motion. Keep the draw budget
# deliberately tiny so visual UAT does not turn the OptiPlex into a software-rendering benchmark.

var weather := "clear"
var lighting := "day"
var phase_seconds := 0.0

func present(frame: Dictionary) -> void:
    weather = str(frame.get("weather", "clear"))
    lighting = str(frame.get("lighting", "day"))

func _process(delta: float) -> void:
    phase_seconds += minf(delta, 0.10)
    queue_redraw()

func _draw() -> void:
    if weather == "rain":
        _draw_window_rain()
    elif lighting == "day":
        _draw_day_motes()

func _draw_window_rain() -> void:
    # Match the authored window aperture only; rain should move outside, not through the room.
    var phase := int(phase_seconds * 12.0)
    for i in range(14):
        var x := 84 + ((i * 17 + phase * 3) % 80)
        var y := 40 + ((i * 11 + phase * 5) % 44)
        draw_rect(Rect2(x, y, 1, 3 + (i % 2)), Color(0.58, 0.77, 0.84, 0.48), true)

func _draw_day_motes() -> void:
    # Five slow one-pixel motes are enough to stop the room reading as a dead backdrop without
    # competing with Moss or adding a particle-system/runtime cost.
    var phase := int(phase_seconds * 3.0)
    for i in range(5):
        var x := 110 + ((i * 31 + phase) % 92)
        var y := 91 + ((i * 19 + phase / 2) % 49)
        draw_rect(Rect2(x, y, 1, 1), Color(0.94, 0.86, 0.63, 0.34), true)
