extends Node2D

var weather := "clear"
var lighting := "day"
var season := "spring"
var manual_ms := 0

func present(frame: Dictionary, timestamp_ms: int) -> void:
    weather = str(frame.get("weather", "clear"))
    lighting = str(frame.get("lighting", "day"))
    var s = frame.get("season", {})
    season = str(s.get("name", "spring"))
    manual_ms = timestamp_ms
    queue_redraw()

func _draw() -> void:
    if lighting == "night":
        draw_rect(Rect2(0, 0, 400, 240), Color(0.055, 0.09, 0.18, 0.52), true)
        draw_rect(Rect2(0, 0, 400, 82), Color(0.05, 0.08, 0.16, 0.22), true)
    elif lighting == "dusk":
        draw_rect(Rect2(0, 0, 400, 240), Color(0.23, 0.10, 0.18, 0.16), true)
    if weather == "rain":
        draw_rect(Rect2(0, 0, 400, 240), Color(0.08, 0.18, 0.27, 0.12), true)
        var phase = int(manual_ms / 120) % 12
        for i in range(26):
            var x = 18 + ((i * 37 + phase * 7) % 360)
            var y = 18 + ((i * 29 + phase * 11) % 185)
            var length = 2 + (i % 3)
            draw_rect(Rect2(x, y, 1, length), Color(0.48, 0.68, 0.78, 0.65), true)
        for i in range(12):
            var xw = 28 + ((i * 19 + phase * 5) % 112)
            var yw = 28 + ((i * 31 + phase * 9) % 102)
            draw_rect(Rect2(xw, yw, 1, 4 + (i % 2)), Color(0.62, 0.80, 0.87, 0.72), true)
