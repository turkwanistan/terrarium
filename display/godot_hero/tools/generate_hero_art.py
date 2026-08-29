from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art"

P = {
    "clear": (0, 0, 0, 0),
    "ink": (39, 34, 42, 255),
    "plum": (67, 48, 58, 255),
    "wall_deep": (91, 82, 73, 255),
    "wall": (153, 143, 112, 255),
    "wall_light": (188, 173, 132, 255),
    "wall_cool": (112, 126, 126, 255),
    "wood_deep": (65, 39, 40, 255),
    "wood_shadow": (92, 49, 42, 255),
    "wood": (126, 67, 48, 255),
    "wood_warm": (166, 92, 57, 255),
    "wood_gold": (207, 137, 71, 255),
    "floor_deep": (93, 50, 43, 255),
    "floor": (137, 76, 52, 255),
    "floor_light": (177, 103, 62, 255),
    "cream_shadow": (188, 166, 122, 255),
    "cream": (232, 214, 164, 255),
    "cream_light": (247, 230, 182, 255),
    "blue_deep": (42, 61, 78, 255),
    "blue": (65, 105, 124, 255),
    "blue_light": (104, 151, 159, 255),
    "teal": (53, 111, 104, 255),
    "green_deep": (38, 70, 56, 255),
    "green": (61, 105, 62, 255),
    "green_light": (106, 145, 79, 255),
    "leaf_gold": (174, 159, 71, 255),
    "rug_deep": (34, 70, 59, 255),
    "rug": (50, 105, 75, 255),
    "rug_light": (91, 139, 84, 255),
    "terracotta": (179, 80, 56, 255),
    "rust": (152, 62, 52, 255),
    "amber_dark": (158, 93, 46, 255),
    "amber": (226, 160, 67, 255),
    "gold": (241, 191, 95, 255),
    "sky": (103, 164, 183, 255),
    "sky_light": (159, 199, 196, 255),
    "hill": (67, 112, 85, 255),
    "hill_light": (93, 137, 91, 255),
    "rain_sky": (83, 123, 139, 255),
    "rain_light": (129, 159, 163, 255),
    "night": (36, 50, 75, 255),
    "night_mid": (53, 70, 94, 255),
    "night_light": (83, 100, 119, 255),
    "snow": (214, 220, 207, 255),
    "snow_shadow": (164, 181, 181, 255),
    "dog_deep": (72, 44, 45, 255),
    "dog_shadow": (104, 59, 47, 255),
    "dog": (155, 91, 57, 255),
    "dog_light": (202, 132, 78, 255),
    "muzzle": (225, 183, 112, 255),
    "collar": (65, 112, 128, 255),
}


def c(name):
    return P[name] if isinstance(name, str) else name


class Image:
    def __init__(self, w: int, h: int, fill="clear"):
        self.w = w
        self.h = h
        self.p = [list(c(fill)) for _ in range(w * h)]

    def get(self, x, y):
        return self.p[y * self.w + x]

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y * self.w + x] = list(c(color))

    def blend(self, x, y, color):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return
        src = c(color)
        a = src[3] / 255.0
        if a <= 0:
            return
        dst = self.get(x, y)
        inv = 1.0 - a
        self.p[y * self.w + x] = [int(src[0] * a + dst[0] * inv), int(src[1] * a + dst[1] * inv), int(src[2] * a + dst[2] * inv), 255]

    def rect(self, x, y, w, h, color):
        col = c(color)
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.p[yy * self.w + xx] = list(col)

    def blend_rect(self, x, y, w, h, color):
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.blend(xx, yy, color)

    def line(self, x0, y0, x1, y1, color):
        dx, sx = abs(x1 - x0), 1 if x0 < x1 else -1
        dy, sy = -abs(y1 - y0), 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def poly(self, pts, color, blend=False):
        minx = max(0, min(x for x, _ in pts)); maxx = min(self.w - 1, max(x for x, _ in pts))
        miny = max(0, min(y for _, y in pts)); maxy = min(self.h - 1, max(y for _, y in pts))
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                inside = False; j = len(pts) - 1
                for i in range(len(pts)):
                    xi, yi = pts[i]; xj, yj = pts[j]
                    if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
                        inside = not inside
                    j = i
                if inside:
                    self.blend(x, y, color) if blend else self.set(x, y, color)

    def save(self, path: Path):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            for x in range(self.w): raw.extend(self.p[y * self.w + x])
        def chunk(kind, data):
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        payload = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
        path.write_bytes(payload)


def wall_and_floor(im: Image, mode: str):
    if mode == "night":
        wall, wall_hi, wall_deep = "night_mid", "night_light", "night"; floor, floor_hi, floor_deep = (92,58,57,255),(119,72,63,255),(58,43,52,255)
    elif mode == "rain":
        wall, wall_hi, wall_deep = "wall_cool", (145,154,142,255), (83,94,93,255); floor, floor_hi, floor_deep = (118,70,57,255),(151,87,65,255),(79,53,52,255)
    else:
        wall, wall_hi, wall_deep = "wall", "wall_light", "wall_deep"; floor, floor_hi, floor_deep = "floor", "floor_light", "floor_deep"
    im.rect(0,0,400,132,wall); im.rect(0,0,400,8,"wood_deep"); im.rect(0,8,400,3,"wood_gold"); im.rect(0,126,400,6,"wood_deep"); im.rect(0,132,400,108,floor)
    for x in (14,202,292,393): im.rect(x,15,2,104,wall_deep); im.rect(x+2,15,1,104,wall_hi)
    for y in (61,101): im.rect(0,y,400,1,wall_deep)
    for x,y,w in ((219,27,19),(259,17,14),(268,94,18),(311,22,12),(371,110,14),(8,113,16)): im.rect(x,y,w,1,wall_hi)
    for x,y,w in ((220,29,7),(263,96,9),(369,112,6),(7,115,5)): im.rect(x,y,w,1,wall_deep)
    for y in range(133,240,14): im.rect(0,y,400,1,floor_deep); im.rect(0,y+1,400,1,floor_hi)
    for row,y in enumerate(range(133,240,14)):
        offset=0 if row%2==0 else 42
        for x in range(-offset,400,84): im.rect(x,y,1,14,floor_deep)
    for x,y,w in ((9,142,24),(72,150,17),(198,139,14),(338,145,31),(22,179,12),(82,192,19),(302,182,14),(355,211,20),(150,224,18),(268,232,25)):
        im.rect(x,y,w,1,floor_hi); im.rect(x+4,y+2,max(3,w//3),1,floor_deep)


def draw_window(im: Image, mode: str):
    x,y,w,h=24,17,174,103
    im.rect(x+5,y-3,w-10,5,"wood_warm"); im.rect(x,y,w,h,"wood_deep"); im.rect(x+5,y+5,w-10,h-14,"wood_shadow")
    glass="night" if mode=="night" else "rain_sky" if mode=="rain" else "sky"; im.rect(x+10,y+10,w-20,h-29,glass)
    if mode=="night":
        im.rect(x+10,y+55,w-20,25,"snow_shadow"); im.rect(x+10,y+61,w-20,19,"snow")
        for bx,by in ((42,34),(75,29),(126,31),(160,38)):
            im.line(bx,by,bx+4,81,"wood_shadow"); im.line(bx+2,by+19,bx+15,by+11,"wood_shadow"); im.line(bx+3,by+31,bx-8,by+23,"wood_shadow")
        for sx,sy in ((39,28),(69,46),(97,24),(145,29),(177,50)): im.rect(sx,sy,2,2,"snow")
    else:
        im.poly([(34,78),(57,58),(82,65),(107,51),(141,67),(188,54),(188,91),(34,91)],"hill")
        im.poly([(34,81),(64,69),(95,76),(124,64),(158,77),(188,69),(188,91),(34,91)],"hill_light")
        for lx,ly,col in ((31,46,"green_deep"),(43,37,"green"),(56,52,"green_light"),(165,41,"green"),(176,51,"green_light"),(153,60,"green_deep")):
            im.rect(lx,ly,16,8,col); im.rect(lx+4,ly-6,10,8,col); im.rect(lx+9,ly+5,11,6,col)
        for fx,fy in ((46,39),(61,55),(168,45),(178,58)): im.rect(fx,fy,2,2,"cream_light")
    im.rect(x+82,y+7,4,h-21,"wood_deep"); im.rect(x+8,y+48,w-16,4,"wood_deep"); im.rect(x+84,y+9,1,h-25,"cream_shadow"); im.rect(x+10,y+50,w-20,1,"cream_shadow")
    im.rect(x+15,y+14,2,30,"sky_light" if mode!="night" else "night_light"); im.rect(x+89,y+14,1,25,"sky_light" if mode!="night" else "night_light")
    if mode=="rain":
        for rx,ry,ln in ((38,28,20),(52,35,28),(71,24,16),(91,33,34),(116,21,25),(137,37,26),(158,26,37),(180,42,19)):
            for i in range(ln):
                if i%3!=1: im.set(rx,ry+i,"rain_light")
            im.set(rx-1,ry+ln,"sky_light")
        im.rect(33,93,155,2,"rain_light")
        for px in (44,73,106,151,181): im.rect(px,95,2,5+(px%5),"rain_light")
    im.poly([(12,14),(35,18),(31,101),(20,112),(13,104)],"blue_deep"); im.poly([(17,19),(31,21),(28,95),(21,103),(17,99)],"blue"); im.rect(20,25,4,61,"blue_light")
    im.poly([(209,14),(188,18),(191,99),(203,111),(211,101)],"blue_deep"); im.poly([(204,19),(191,21),(194,94),(202,102),(206,97)],"blue"); im.rect(200,25,3,58,"blue_light")
    im.rect(10,11,201,4,"wood_deep"); im.rect(14,12,193,2,"wood_gold")
    im.rect(18,111,187,8,"wood_warm"); im.rect(14,119,195,7,"wood_deep"); im.rect(20,126,184,8,"wood_shadow"); im.rect(26,131,172,9,"wood_warm")


def draw_daybed(im: Image):
    im.rect(22,134,176,44,"wood_deep"); im.rect(27,136,166,31,"cream_shadow"); im.rect(31,139,158,24,"cream")
    im.poly([(32,140),(67,137),(76,144),(72,158),(35,159),(28,151)],"cream_light"); im.rect(36,143,28,2,"wall_light")
    im.poly([(69,143),(98,140),(109,147),(105,160),(75,160),(67,152)],"terracotta"); im.rect(76,145,21,2,"amber")
    im.poly([(100,139),(189,141),(192,165),(176,171),(105,168),(97,155)],"blue"); im.rect(108,143,72,5,"blue_light"); im.rect(102,151,86,5,"blue_deep")
    for qx,qy in ((112,158),(132,146),(151,159),(171,149)): im.rect(qx,qy,9,2,"cream_shadow"); im.rect(qx+3,qy-2,3,6,"teal")
    im.rect(18,166,181,8,"wood_gold"); im.rect(16,174,186,7,"wood_deep"); im.rect(25,181,12,15,"wood_deep"); im.rect(178,181,12,15,"wood_deep"); im.rect(43,177,116,2,"wood_warm")


def draw_rug(im: Image):
    im.poly([(133,154),(337,154),(360,166),(365,216),(349,231),(147,231),(126,218),(122,170)],"rug_deep")
    im.poly([(142,160),(331,160),(352,169),(355,211),(342,224),(151,224),(134,214),(131,173)],"rug")
    im.rect(148,164,181,3,"rug_light"); im.rect(150,218,187,2,"green_deep")
    for rx in (150,179,292,321): im.rect(rx,173,11,2,"rug_light"); im.rect(rx+4,170,3,8,"amber")
    for rx in (157,188,301,329): im.rect(rx,208,9,2,"rug_light"); im.rect(rx+3,205,3,8,"terracotta")
    im.rect(205,184,10,2,"rug_light"); im.rect(252,199,13,2,"rug_light")
    for tx in range(149,345,18): im.rect(tx,224,1,5,"rug_light")


def draw_bookcase(im: Image):
    x,y=307,28
    im.rect(x+6,y+6,73,125,(36,31,38,90)); im.rect(x,y,74,7,"wood_deep"); im.rect(x+4,y-3,66,4,"wood_warm"); im.rect(x+4,y+7,66,118,"wood_deep"); im.rect(x+9,y+13,56,100,"wood_shadow")
    for sy in (54,79,104): im.rect(x+6,sy,62,5,"wood_warm"); im.rect(x+9,sy+5,56,2,"wood_deep")
    im.rect(x+13,43,5,11,"blue"); im.rect(x+19,39,5,15,"cream_shadow"); im.rect(x+25,42,6,12,"green"); im.rect(x+38,42,15,8,"green_deep"); im.rect(x+41,44,9,4,"sky"); im.rect(x+56,45,7,8,"terracotta"); im.rect(x+58,42,3,3,"amber")
    im.rect(x+12,64,5,14,"rust"); im.rect(x+18,67,4,11,"blue_light"); im.rect(x+23,62,6,16,"blue_deep"); im.rect(x+38,66,7,12,"cream"); im.rect(x+46,62,5,16,"teal"); im.rect(x+55,69,7,9,"amber_dark")
    im.rect(x+12,88,20,11,"amber_dark"); im.rect(x+14,90,16,7,"wood_gold"); im.rect(x+38,92,17,5,"cream_shadow"); im.rect(x+40,89,13,3,"blue"); im.rect(x+58,85,3,13,"wood_shadow"); im.rect(x+53,85,7,5,"green"); im.rect(x+59,82,7,6,"green_light")
    im.rect(x+10,112,25,14,"wood"); im.rect(x+39,112,25,14,"wood"); im.rect(x+12,114,21,10,"wood_shadow"); im.rect(x+41,114,21,10,"wood_shadow"); im.rect(x+31,118,2,2,"wood_gold"); im.rect(x+41,118,2,2,"wood_gold"); im.rect(x+8,127,58,5,"wood_warm"); im.rect(x+12,132,8,9,"wood_deep"); im.rect(x+54,132,8,9,"wood_deep")


def draw_wall_details(im: Image):
    im.rect(222,35,19,23,"wood_deep"); im.rect(225,38,13,17,"cream_shadow"); im.rect(229,44,5,7,"green_deep"); im.rect(231,40,1,13,"wood_shadow")
    im.rect(249,22,26,20,"wood_deep"); im.rect(252,25,20,14,"cream_shadow"); im.rect(256,28,12,8,"sky"); im.rect(258,33,8,3,"hill")
    im.rect(274,72,26,3,"wood_warm"); im.rect(278,75,18,2,"wood_deep"); im.rect(283,65,7,7,"terracotta"); im.rect(285,62,3,3,"amber")
    im.rect(288,88,2,23,"wood_shadow"); im.rect(279,93,9,5,"green"); im.rect(290,96,9,5,"green_light"); im.rect(281,104,7,5,"green_deep")
    im.rect(213,10,2,18,"wood_shadow"); im.rect(205,26,18,6,"terracotta"); im.rect(208,31,12,5,"amber_dark")
    for lx,ly in ((203,35),(214,34),(207,41),(217,44),(210,49)): im.rect(lx,ly,9,5,"green"); im.rect(lx+2,ly-3,5,4,"green_light")


def draw_side_table_and_props(im: Image):
    im.rect(211,118,71,7,"wood_warm"); im.rect(216,125,62,6,"wood_deep"); im.rect(220,131,7,33,"wood_deep"); im.rect(264,131,7,33,"wood_deep"); im.rect(225,139,39,5,"wood_shadow"); im.rect(228,144,33,13,"wood"); im.rect(232,148,25,5,"wood_shadow"); im.rect(250,151,3,2,"wood_gold")
    im.rect(241,94,3,24,"wood_deep"); im.poly([(231,86),(254,86),(261,101),(225,101)],"amber"); im.rect(231,88,24,3,"gold"); im.rect(234,101,18,3,"amber_dark"); im.rect(238,114,11,3,"wood_deep")
    im.rect(214,112,23,4,"blue_deep"); im.rect(218,108,20,4,"terracotta"); im.rect(222,105,16,3,"green_deep"); im.rect(261,108,9,8,"cream"); im.rect(269,110,4,5,"cream_shadow"); im.rect(263,107,5,1,"blue_deep")
    im.rect(274,101,8,15,"blue"); im.rect(276,98,4,4,"cream_shadow"); im.rect(276,105,4,4,"blue_light"); im.poly([(197,125),(209,124),(208,132),(196,133)],"cream"); im.rect(199,128,7,1,"blue_deep")


def draw_small_lived_in_details(im: Image):
    im.rect(154,103,15,12,"terracotta"); im.rect(152,101,19,4,"cream_shadow"); im.rect(160,88,2,14,"wood_shadow")
    for lx,ly,col in ((150,91,"green"),(158,84,"green_light"),(164,91,"green"),(154,96,"green_deep")): im.rect(lx,ly,11,6,col); im.rect(lx+3,ly-4,6,5,col)
    im.rect(28,124,21,4,"blue_deep"); im.rect(31,120,19,4,"terracotta"); im.rect(35,117,15,3,"green_deep"); im.rect(55,118,10,9,"cream"); im.rect(64,120,4,5,"cream_shadow"); im.rect(57,117,6,1,"blue_deep")
    im.rect(74,112,5,15,"cream"); im.rect(72,126,9,2,"wood_deep"); im.rect(76,107,2,5,"amber")
    im.rect(83,205,30,17,"wood_gold"); im.rect(87,208,22,11,"amber_dark"); im.rect(89,202,18,3,"wood_deep"); im.rect(85,203,4,8,"wood_deep"); im.rect(107,203,4,8,"wood_deep")
    for bx in (91,99): im.rect(bx,209,2,8,"wood_gold")
    im.rect(44,215,20,7,"blue_deep"); im.rect(67,214,19,7,"blue"); im.rect(47,213,12,2,"blue_light"); im.rect(70,212,12,2,"blue_light")
    im.rect(112,226,18,9,"terracotta"); im.rect(115,223,12,4,"cream_shadow"); im.poly([(167,217),(183,215),(181,226),(165,228)],"cream"); im.rect(170,220,8,1,"blue_deep")
    im.poly([(184,225),(197,222),(199,231),(185,232)],"cream_shadow"); im.rect(187,226,7,1,"rust"); im.rect(278,218,12,12,"terracotta"); im.rect(281,214,7,6,"amber"); im.rect(283,218,4,4,"cream_shadow")
    im.rect(304,209,14,10,"blue_deep"); im.rect(307,206,9,4,"blue_light"); im.rect(321,215,19,8,"cream_shadow"); im.rect(324,212,14,4,"green"); im.rect(340,224,17,9,"amber_dark"); im.rect(343,220,11,5,"wood_gold")
    im.line(258,213,263,209,"rust"); im.line(263,209,268,215,"rust"); im.line(268,215,274,211,"rust")


def apply_mood(im: Image, mode: str):
    if mode=="rain":
        im.blend_rect(0,0,400,240,(52,80,91,38)); im.blend_rect(18,120,187,67,(232,184,116,12))
    elif mode=="night":
        im.blend_rect(0,0,400,240,(26,40,68,74)); im.poly([(188,86),(291,86),(318,132),(318,180),(173,180),(173,126)],(239,163,69,52),blend=True); im.poly([(205,96),(276,96),(296,130),(296,165),(188,165),(188,126)],(246,178,78,55),blend=True); im.poly([(224,104),(260,104),(275,131),(275,151),(210,151),(210,124)],(255,198,91,64),blend=True)
        im.rect(231,88,24,3,"gold"); im.poly([(231,91),(254,91),(259,101),(227,101)],"amber")


def hero_back(mode: str):
    im=Image(400,240,"wall"); wall_and_floor(im,mode); draw_window(im,mode); draw_wall_details(im); draw_bookcase(im); draw_daybed(im); draw_rug(im); draw_side_table_and_props(im); draw_small_lived_in_details(im); apply_mood(im,mode); return im


def foreground():
    im=Image(400,240); im.rect(366,195,18,40,"wood_deep"); im.rect(361,188,28,15,"terracotta"); im.rect(364,184,22,7,"cream_shadow"); im.rect(374,145,3,42,"wood_shadow")
    for ox,oy,pts,col in ((347,156,[(0,8),(12,0),(26,5),(18,16),(5,18)],"green_deep"),(366,145,[(0,11),(10,0),(23,8),(17,20),(4,20)],"green"),(378,160,[(0,8),(13,1),(22,9),(14,18),(2,17)],"green_light"),(350,174,[(0,7),(11,0),(25,6),(20,16),(7,19)],"green"),(371,180,[(0,8),(12,0),(25,7),(19,18),(5,18)],"green_deep")):
        im.poly([(ox+x,oy+y) for x,y in pts],col); im.rect(ox+8,oy+8,10,1,"green_light" if col!="green_light" else "leaf_gold")
    for tx in range(153,346,18): im.rect(tx,229,2,7,"rug_light")
    im.rect(334,224,28,7,"wood_deep"); im.rect(338,220,20,7,"wood_gold"); im.rect(341,222,14,5,"amber_dark"); return im


MOSS_ROLE_MAP = {
    "shadow": (43, 36, 29, 92),
    "dogDark": P["dog_deep"],
    "dog": P["dog"],
    "dogLight": P["dog_light"],
    "dogCream": P["muzzle"],
    "eye": P["ink"],
}


def _canonical_moss(asset_name: str):
    """Render the accepted Canvas Moss silhouette into the Godot art palette."""
    repo_root = ROOT.parents[1]
    data = json.loads((repo_root / "display" / "art" / "moss" / f"{asset_name}.json").read_text())
    im = Image(data["width"], data["height"])
    for x, y, w, h, role in data["runs"]:
        im.rect(x, y, w, h, MOSS_ROLE_MAP[role])
    eye_runs = [r for r in data["runs"] if r[-1] == "eye"]
    # The smaller eye-role run is the visible eye; the larger/farther run is nose.
    visible_eye = min(eye_runs, key=lambda r: r[2] * r[3])
    nose = max(eye_runs, key=lambda r: r[2] * r[3])
    _embellish_moss(im, visible_eye[:2], nose[:2], asset_name)
    return im


def _embellish_moss(im: Image, eye_xy, nose_xy, asset_name: str):
    """Small authored detail pass that preserves the old silhouette exactly."""
    ex, ey = eye_xy
    nx, ny = nose_xy
    motion_y = 1 if asset_name in {"walk-1", "walk-3"} else 0

    # Eye catchlight and brow: cuter/readable without turning the face into noise.
    im.set(ex, ey, "cream_light")
    im.rect(ex-1, ey-2, 4, 1, "dog_deep")

    # Refine the accepted cream blaze and muzzle with two additional value clusters.
    im.rect(ex-2, ey-5, 4, 2, "cream_light")
    im.rect(nx-5, ny-1, 5, 2, "cream_light")
    im.rect(nx-3, ny+2, 3, 1, "cream_shadow")
    im.rect(nx-1, ny+3, 3, 1, "dog_deep")

    # Inner-ear warm cluster breaks the old rectangular ear mass while retaining it.
    im.rect(ex-10, ey+1, 2, 7, "dog_shadow")
    im.rect(ex-9, ey+2, 1, 4, "dog")

    # Dorsal/body fur clusters and brighter chest/paws add craft at hero scale.
    im.rect(22, 23+motion_y, 11, 2, "dog_light")
    im.rect(25, 26+motion_y, 6, 1, "dog_light")
    im.rect(35, 28+motion_y, 3, 5, "cream_light")
    im.rect(20, 41+motion_y, 3, 1, "muzzle")
    im.rect(35, 41+motion_y, 3, 1, "muzzle")

    # Tiny warm tail-tip accent; do not enlarge or curl the accepted tail silhouette.
    im.rect(7, 23+motion_y, 3, 2, "dog_light")


def moss_pose(frame: int, walking=False):
    if walking:
        return _canonical_moss(f"walk-{frame % 4}")
    # Idle remains genuinely still: all four pilot frames use the same planted pose.
    return _canonical_moss("idle")


def inspect_pose(frame: int):
    names=("inspect-anticipate", "inspect-contact", "inspect-hold", "inspect-recover")
    return _canonical_moss(names[frame % 4])


def main():
    ART.mkdir(parents=True,exist_ok=True)
    hero_back("day").save(ART/"hero_spring_day.png"); hero_back("rain").save(ART/"hero_rain.png"); hero_back("night").save(ART/"hero_winter_night.png"); foreground().save(ART/"hero_foreground.png")
    for i in range(4): moss_pose(i,False).save(ART/f"moss_idle_{i}.png"); moss_pose(i,True).save(ART/f"moss_walk_{i}.png"); inspect_pose(i).save(ART/f"moss_inspect_{i}.png")
    details=[
        "deep three-pane window",
        "layered curtains",
        "authored exterior landscape / weather glass",
        "built-in window-seat architecture",
        "layered daybed",
        "pillow + quilt textile composition",
        "sill ceramic planter",
        "sill plant",
        "nook books",
        "nook mug + candle cluster",
        "hanging plant",
        "pressed-herb frame",
        "landscape frame",
        "tiny wall shelf + herb bundle",
        "bookcase",
        "curated shelf books",
        "shelf basket + folded textile",
        "ceramic shelf vessel",
        "side table",
        "warm lamp",
        "tabletop reading cluster",
        "woven rug",
        "floor basket + slippers",
        "floor story cluster",
        "foreground plant + basket occlusion",
    ]
    manifest={"schema":"terrarium.godot-hero-gate.v1","art_surface":[400,240],"presentation":[800,480],"slice":"window + sleeping/reading nook + rug edge","variants":["spring_day","rain","winter_warm_night"],"motion":["idle_4","walk_4","inspect_4"],"authored_details":details,"authored_detail_count":len(details),"moss_character_pass":"accepted Canvas Moss silhouette + restrained Godot-specific detail overlays; planted idle; canonical walk/inspect poses","notes":"Decision-gate art proof. Hardcoded presentation only; no canonical simulation/state integration."}
    (ART/"hero_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"assets":16,"detail_count":len(details),"art":str(ART)}))

if __name__=="__main__": main()
