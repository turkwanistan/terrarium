from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art"

PALETTE = {
    "transparent": (0, 0, 0, 0),
    "wall": (124, 126, 101, 255), "wall_light": (151, 148, 112, 255), "wall_shadow": (83, 88, 77, 255),
    "wood_deep": (61, 39, 45, 255), "wood_shadow": (91, 49, 45, 255), "wood": (128, 68, 48, 255), "wood_warm": (166, 91, 52, 255), "wood_gold": (205, 137, 68, 255),
    "floor": (125, 74, 53, 255), "floor_light": (160, 94, 57, 255), "floor_shadow": (87, 51, 49, 255),
    "cream": (233, 218, 164, 255), "cream_shadow": (189, 169, 126, 255),
    "blue": (74, 115, 137, 255), "blue_light": (111, 157, 165, 255), "blue_dark": (48, 72, 96, 255),
    "green_deep": (42, 70, 53, 255), "green": (62, 103, 58, 255), "green_light": (104, 142, 68, 255), "leaf_yellow": (170, 157, 67, 255),
    "rug_deep": (40, 73, 59, 255), "rug": (57, 104, 72, 255), "rug_light": (97, 136, 80, 255),
    "amber": (224, 159, 69, 255), "amber_dark": (163, 100, 48, 255), "terracotta": (183, 83, 56, 255), "red": (164, 63, 61, 255),
    "sky": (109, 162, 181, 255), "sky_light": (169, 199, 193, 255), "night": (44, 60, 91, 255), "snow": (214, 220, 207, 255),
    "dog_deep": (67, 43, 43, 255), "dog_shadow": (100, 59, 48, 255), "dog": (145, 87, 58, 255), "dog_light": (192, 126, 72, 255), "muzzle": (211, 168, 105, 255),
    "ink": (45, 39, 45, 255), "glass": (133, 178, 181, 255), "paper": (224, 210, 162, 255),
}


def rgba(name: str):
    return PALETTE[name]


class Image:
    def __init__(self, w: int, h: int, fill="transparent"):
        self.w, self.h = w, h
        self.p = [list(rgba(fill)) for _ in range(w*h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y*self.w+x] = list(rgba(c) if isinstance(c, str) else c)

    def rect(self, x, y, w, h, c):
        color = rgba(c) if isinstance(c, str) else c
        for yy in range(max(0,y), min(self.h,y+h)):
            for xx in range(max(0,x), min(self.w,x+w)):
                self.p[yy*self.w+xx] = list(color)

    def line(self, x0, y0, x1, y1, c):
        dx, sx = abs(x1-x0), 1 if x0 < x1 else -1
        dy, sy = -abs(y1-y0), 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0,y0,c)
            if x0 == x1 and y0 == y1: break
            e2 = 2*err
            if e2 >= dy: err += dy; x0 += sx
            if e2 <= dx: err += dx; y0 += sy

    def poly(self, pts, c):
        color = rgba(c) if isinstance(c, str) else c
        minx,maxx = max(0,min(x for x,_ in pts)), min(self.w-1,max(x for x,_ in pts))
        miny,maxy = max(0,min(y for _,y in pts)), min(self.h-1,max(y for _,y in pts))
        for y in range(miny,maxy+1):
            for x in range(minx,maxx+1):
                inside=False
                j=len(pts)-1
                for i in range(len(pts)):
                    xi,yi=pts[i]; xj,yj=pts[j]
                    if ((yi>y)!=(yj>y)) and x < (xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi:
                        inside=not inside
                    j=i
                if inside: self.p[y*self.w+x]=list(color)

    def save(self, path: Path):
        raw=bytearray()
        for y in range(self.h):
            raw.append(0)
            for x in range(self.w): raw.extend(self.p[y*self.w+x])
        def chunk(kind,data):
            return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',self.w,self.h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b'')
        path.write_bytes(png)


def room_back():
    im=Image(400,240,"wall")
    im.rect(0,0,400,7,"wood_deep"); im.rect(0,7,400,2,"wood_gold")
    im.rect(0,130,400,5,"wood_deep"); im.rect(0,135,400,25,"wood_shadow")
    for x in range(8,400,42):
        im.rect(x,18,2,105,"wall_shadow"); im.rect(x+2,18,1,105,"wall_light")
    for y in (38,82,119): im.rect(0,y,400,1,"wall_shadow")
    im.rect(0,160,400,80,"floor")
    for y in range(161,240,13):
        im.rect(0,y,400,1,"floor_shadow"); im.rect(0,y+1,400,1,"floor_light")
    for row,y in enumerate(range(161,240,13)):
        offset=0 if row%2==0 else 29
        for x in range(-offset,400,58):
            im.rect(x,y,1,13,"floor_shadow")
            if x+17<400: im.rect(x+17,y+5,13,1,"floor_light")
            if x+37<400: im.rect(x+37,y+9,8,1,"floor_shadow")
    # wall frames and trim details concentrated in the slice
    im.rect(173,14,2,111,"wood_deep"); im.rect(175,14,1,111,"wood_gold")
    im.rect(204,25,38,2,"wood_deep"); im.rect(205,27,36,24,"cream_shadow"); im.rect(208,30,30,18,"green_deep")
    im.rect(211,33,9,12,"green"); im.rect(221,35,14,8,"sky")
    im.rect(252,58,34,3,"wood_deep"); im.rect(255,61,28,2,"wood_gold")
    # Small asymmetric plaster/trim marks keep broad wall planes authored
    # without turning the background into uniform visual noise.
    for x,y,w in [(185,18,22),(242,18,10),(286,31,18),(195,68,12),(235,95,17),(280,105,11),(365,20,13)]:
        im.rect(x,y,w,1,"wall_light")
    for x,y,w in [(182,19,8),(285,32,7),(233,96,8),(364,21,5)]:
        im.rect(x,y,w,1,"wall_shadow")
    return im


def window(season="spring"):
    im=Image(148,148)
    im.rect(8,7,132,8,"wood_deep"); im.rect(12,10,124,4,"wood_gold")
    im.rect(12,15,7,90,"wood_shadow"); im.rect(129,15,7,90,"wood_shadow")
    im.rect(19,15,110,83,"sky" if season!="winter" else "night")
    if season=="winter":
        im.rect(19,68,110,30,"snow"); im.rect(19,64,110,4,"sky_light")
        for x,y in [(31,22),(52,30),(82,18),(107,35)]:
            im.line(x,y,x+8,y+49,"wood_shadow"); im.line(x+3,y+17,x+19,y+7,"wood_shadow"); im.line(x+5,y+28,x-8,y+18,"wood_shadow")
        for x,y in [(28,76),(47,83),(69,72),(94,88),(116,79)]: im.rect(x,y,8,3,"snow")
    else:
        im.rect(19,75,110,23,"green_deep")
        for x,y,c in [(24,55,"green"),(33,39,"green_light"),(45,62,"green"),(57,48,"green_light"),(69,64,"green"),(84,43,"green_light"),(98,56,"green"),(113,35,"green_light"),(121,65,"green")]:
            im.rect(x,y,13,8,c); im.rect(x+4,y-4,8,7,c); im.rect(x+8,y+4,9,6,c)
        for x,y in [(38,37),(53,53),(88,42),(105,62),(119,46)]: im.rect(x,y,3,3,"cream")
    # panes, sill, curtains
    im.rect(72,15,4,83,"wood_deep"); im.rect(19,54,110,4,"wood_deep")
    im.rect(74,17,1,79,"cream_shadow"); im.rect(21,56,106,1,"cream_shadow")
    im.poly([(0,10),(22,13),(19,92),(5,104)],"blue_dark"); im.poly([(4,16),(17,17),(15,85),(7,93)],"blue")
    im.rect(6,26,3,55,"blue_light"); im.poly([(148,10),(126,13),(129,92),(143,104)],"blue_dark"); im.poly([(144,16),(131,17),(133,85),(141,93)],"blue")
    im.rect(139,25,3,56,"blue_light")
    im.rect(5,98,138,6,"cream_shadow"); im.rect(2,104,144,8,"wood_gold"); im.rect(6,112,136,7,"wood_deep")
    im.rect(20,119,108,6,"wood_warm"); im.rect(25,125,98,9,"cream_shadow"); im.rect(31,128,86,5,"rug")
    im.rect(22,134,7,14,"wood_deep"); im.rect(119,134,7,14,"wood_deep")
    return im


def nook_back():
    im=Image(132,72)
    im.rect(2,9,128,47,"wood_deep"); im.rect(7,5,118,48,"wood_warm")
    im.rect(12,11,108,38,"cream_shadow")
    # pillow and quilt
    im.poly([(15,15),(49,12),(57,18),(53,32),(19,34),(12,26)],"cream")
    im.rect(20,17,26,2,"wall_light"); im.rect(18,28,31,2,"cream_shadow")
    im.poly([(54,13),(117,16),(119,47),(50,47),(47,28)],"blue")
    im.rect(58,17,55,5,"blue_light"); im.rect(52,28,64,6,"blue_dark"); im.rect(59,36,57,5,"blue")
    for x,y in [(66,21),(78,31),(96,22),(105,38)]: im.rect(x,y,8,2,"cream_shadow")
    # side textile tassels and mattress edge
    im.rect(10,49,112,5,"wood_gold"); im.rect(10,54,112,4,"wood_deep")
    return im


def nook_front():
    im=Image(132,72)
    im.rect(7,52,118,5,"wood_gold"); im.rect(5,57,122,7,"wood_deep")
    im.rect(12,64,10,8,"wood_deep"); im.rect(110,64,10,8,"wood_deep")
    im.rect(14,57,99,2,"wood_warm")
    im.poly([(52,40),(121,40),(119,55),(58,55)],"blue_dark"); im.rect(60,42,56,3,"blue")
    return im


def rug():
    im=Image(144,54)
    im.poly([(9,3),(135,3),(143,12),(139,44),(130,52),(12,52),(3,44),(0,13)],"rug_deep")
    im.poly([(10,7),(134,7),(138,14),(135,42),(127,48),(15,48),(7,42),(5,15)],"rug")
    im.rect(13,11,118,2,"rug_light"); im.rect(14,40,116,2,"green_deep")
    # woven motifs, intentionally clustered with open negative space
    for x,y in [(20,18),(43,30),(70,18),(95,31),(118,19)]:
        im.rect(x,y,9,2,"rug_light"); im.rect(x+3,y-3,3,8,"amber"); im.rect(x+2,y+4,5,1,"green_deep")
    for x in range(14,132,16): im.rect(x,49,1,5,"rug_light")
    return im


def bookcase():
    """Large authored right-wall anchor for the vertical-slice composition."""
    im=Image(78,105)
    # contact shadow and warm outer carcass
    im.rect(5,7,72,96,(43,38,42,115))
    im.rect(0,2,72,7,"wood_deep"); im.rect(4,0,64,4,"wood_warm"); im.rect(4,8,64,92,"wood_deep")
    im.rect(8,12,56,82,"wood_shadow")
    # shelves with deliberately uneven object groupings
    for y in (33,55,77):
        im.rect(6,y,60,4,"wood_warm"); im.rect(8,y+4,56,2,"wood_deep")
    # top shelf: books + framed blue-green object + pottery
    im.rect(11,16,5,15,"blue_dark"); im.rect(17,14,5,17,"cream_shadow"); im.rect(23,17,6,14,"green")
    im.rect(35,16,14,11,"green_deep"); im.rect(38,18,8,6,"sky")
    im.rect(54,20,8,9,"terracotta"); im.rect(56,17,4,3,"amber")
    # middle shelf: staggered books and a pale ceramic bottle
    im.rect(12,41,5,11,"terracotta"); im.rect(18,39,4,13,"blue"); im.rect(23,43,8,9,"green_deep")
    im.rect(39,39,6,13,"cream"); im.rect(46,37,5,15,"blue_dark"); im.rect(55,45,6,7,"amber_dark")
    # lower shelf: basket, folded textile and plant cutting
    im.rect(11,63,18,10,"amber_dark"); im.rect(13,65,14,6,"wood_gold"); im.rect(36,67,16,5,"cream_shadow")
    im.rect(54,62,4,11,"wood_shadow"); im.rect(50,61,7,5,"green"); im.rect(57,59,6,6,"green_light")
    # bottom cabinet doors create weight instead of another open shelf
    im.rect(10,82,24,12,"wood"); im.rect(38,82,24,12,"wood")
    im.rect(12,84,20,8,"wood_shadow"); im.rect(40,84,20,8,"wood_shadow")
    im.rect(30,87,2,2,"wood_gold"); im.rect(40,87,2,2,"wood_gold")
    im.rect(8,96,58,4,"wood_warm"); im.rect(11,100,8,5,"wood_deep"); im.rect(53,100,8,5,"wood_deep")
    return im


def simple_prop(kind):
    sizes={"plant_small":(18,27),"plant_large":(24,38),"books":(21,13),"basket":(22,17),"pot":(14,15),"mug":(11,10),"frame":(18,21),"paper":(14,9),"cushion":(20,13),"blocks":(13,9),"stool":(25,26),"table":(30,31),"lamp":(18,30),"jar":(13,18),"candle":(8,18),"slippers":(20,8),"herb":(15,19),"bowl":(16,9)}
    w,h=sizes[kind]; im=Image(w,h)
    if kind.startswith("plant"):
        im.rect(w//2-1,h-15,3,10,"wood_shadow")
        leaf="green_light" if kind=="plant_large" else "green"
        for x,y in [(w//2-7,h-24),(w//2-2,h-29),(w//2+3,h-23),(w//2-5,h-18),(w//2+1,h-17)]: im.rect(x,y,8,5,leaf); im.rect(x+2,y-3,4,4,"green_deep")
        im.rect(w//2-6,h-7,12,6,"terracotta"); im.rect(w//2-4,h-9,8,3,"cream_shadow")
    elif kind=="books":
        im.rect(0,8,20,4,"blue_dark"); im.rect(2,5,17,3,"terracotta"); im.rect(5,2,15,3,"green_deep"); im.rect(7,1,10,1,"cream")
    elif kind=="basket":
        im.rect(1,7,20,9,"wood_gold"); im.rect(3,9,16,5,"amber_dark"); im.rect(5,3,12,2,"wood_deep"); im.rect(3,4,2,6,"wood_deep"); im.rect(17,4,2,6,"wood_deep"); im.rect(6,10,2,4,"wood_gold"); im.rect(12,10,2,4,"wood_gold")
    elif kind=="pot": im.rect(2,5,10,9,"terracotta"); im.rect(0,4,14,3,"cream_shadow"); im.rect(4,8,6,2,"amber")
    elif kind=="mug": im.rect(1,2,7,7,"cream"); im.rect(8,3,3,4,"cream_shadow"); im.rect(3,1,4,1,"blue_dark")
    elif kind=="frame": im.rect(1,1,16,19,"wood_deep"); im.rect(3,3,12,15,"cream_shadow"); im.rect(5,5,8,10,"sky"); im.rect(6,11,6,4,"green_deep")
    elif kind=="paper": im.poly([(1,1),(13,0),(12,8),(0,8)],"paper"); im.rect(3,3,7,1,"blue_dark"); im.rect(2,6,5,1,"wood_shadow")
    elif kind=="cushion": im.poly([(2,2),(17,1),(20,6),(17,12),(2,12),(0,7)],"terracotta"); im.rect(5,4,9,2,"amber")
    elif kind=="blocks": im.rect(0,4,6,5,"amber"); im.rect(5,1,6,7,"blue"); im.rect(9,5,4,4,"terracotta")
    elif kind=="stool": im.rect(1,3,23,7,"wood_warm"); im.rect(4,10,5,15,"wood_deep"); im.rect(17,10,5,15,"wood_deep"); im.rect(5,4,15,2,"wood_gold")
    elif kind=="table": im.rect(1,6,28,6,"wood_warm"); im.rect(3,12,5,19,"wood_deep"); im.rect(22,12,5,19,"wood_deep"); im.rect(4,7,22,2,"wood_gold")
    elif kind=="lamp": im.rect(8,13,2,16,"wood_deep"); im.poly([(4,4),(14,4),(17,12),(1,12)],"amber"); im.rect(6,1,6,4,"cream"); im.rect(5,28,8,2,"wood_deep")
    elif kind=="jar": im.rect(2,5,9,12,"blue"); im.rect(3,3,7,3,"cream_shadow"); im.rect(4,8,5,3,"blue_light"); im.rect(3,15,7,2,"blue_dark")
    elif kind=="candle": im.rect(2,5,4,12,"cream"); im.rect(1,16,6,2,"wood_deep"); im.rect(3,1,2,4,"amber"); im.set(4,0,"cream")
    elif kind=="slippers": im.rect(0,3,9,5,"blue_dark"); im.rect(11,2,9,5,"blue"); im.rect(2,2,5,2,"blue_light"); im.rect(13,1,5,2,"blue_light")
    elif kind=="herb": im.rect(7,0,2,19,"wood_shadow"); im.rect(1,4,7,4,"green"); im.rect(8,7,7,4,"green_light"); im.rect(2,12,6,4,"green_deep")
    elif kind=="bowl": im.rect(1,3,14,5,"terracotta"); im.rect(3,1,10,3,"cream_shadow"); im.rect(4,7,8,2,"wood_deep")
    return im


def moss_pose(kind, step=0):
    im=Image(46,36)
    # contact shadow kept in sprite for planted feel
    im.rect(8,31,30,2,(43,38,42,120))
    body_shift = [0,1,0,-1][step%4] if kind=="walk" else 0
    head_x = 25 + (1 if kind=="inspect" else 0)
    head_y = 9 + body_shift + (2 if kind=="loaf" else 0)
    if kind=="loaf":
        im.poly([(7,19),(14,13),(31,12),(39,18),(38,28),(29,31),(12,29),(6,25)],"dog_shadow")
        im.poly([(12,17),(29,15),(36,20),(33,26),(13,26),(9,22)],"dog")
        head_x,head_y=27,12
    else:
        im.poly([(7,17+body_shift),(13,12+body_shift),(30,12+body_shift),(38,18+body_shift),(36,27+body_shift),(27,30+body_shift),(10,28+body_shift),(5,23+body_shift)],"dog_shadow")
        im.poly([(11,16+body_shift),(16,13+body_shift),(29,14+body_shift),(35,19+body_shift),(33,25+body_shift),(24,27+body_shift),(12,25+body_shift),(8,21+body_shift)],"dog")
        im.rect(14,16+body_shift,13,3,"dog_light")
    # head and floppy ears
    if kind=="inspect": head_x += 3
    im.poly([(head_x-2,head_y),(head_x+8,head_y-1),(head_x+14,head_y+5),(head_x+12,head_y+14),(head_x+4,head_y+18),(head_x-3,head_y+13),(head_x-5,head_y+5)],"dog")
    im.poly([(head_x-5,head_y+2),(head_x-9,head_y+4),(head_x-9,head_y+13),(head_x-4,head_y+16),(head_x,head_y+8)],"dog_deep")
    im.poly([(head_x+9,head_y+2),(head_x+15,head_y+4),(head_x+15,head_y+12),(head_x+11,head_y+14),(head_x+7,head_y+8)],"dog_shadow")
    im.rect(head_x+5,head_y+8,10,7,"muzzle"); im.rect(head_x+12,head_y+10,3,3,"ink"); im.rect(head_x+6,head_y+5,2,2,"ink")
    # Face blaze, eyebrow highlight and collar make Moss read as a character rather than a brown block.
    im.rect(head_x+3,head_y+1,3,6,"cream_shadow"); im.rect(head_x+4,head_y+2,2,4,"cream")
    im.rect(head_x+2,head_y+3,7,2,"dog_light"); im.rect(head_x-1,head_y+14,10,2,"blue_dark")
    if kind not in ("loaf",):
        im.rect(18,19+body_shift,5,7,"muzzle"); im.rect(19,20+body_shift,4,4,"cream_shadow")
    # tail
    im.poly([(8,18+body_shift),(3,15+body_shift),(1,17+body_shift),(5,20+body_shift),(9,22+body_shift)],"dog_deep")
    # legs / gait
    if kind=="walk":
        legs=[(12,25,5,7),(27,25,5,7)]
        if step==0: legs=[(10,25,5,7),(29,24,5,8)]
        elif step==1: legs=[(14,24,5,8),(27,26,5,6)]
        elif step==2: legs=[(12,26,5,6),(31,25,5,7)]
        elif step==3: legs=[(15,25,5,7),(26,24,5,8)]
        for x,y,w,h in legs: im.rect(x,y,w,h,"dog_deep"); im.rect(x,y+h-2,w+1,2,"ink")
    elif kind not in ("loaf",):
        im.rect(11,25,5,7,"dog_deep"); im.rect(29,25,5,7,"dog_deep"); im.rect(10,30,7,2,"ink"); im.rect(28,30,7,2,"ink")
    if kind=="inspect":
        reach=step
        if reach>=1: im.rect(34,24,5+reach*2,4,"dog_light")
        if reach>=2: im.rect(39,25,5,2,"dog_deep")
    if kind=="carry":
        im.rect(34,23,7,4,"dog_light")
    return im


def object_thread(state):
    im=Image(16,16)
    if state=="loose":
        im.line(1,10,5,6,"red"); im.line(5,6,9,11,"red"); im.line(9,11,14,7,"red"); im.rect(4,5,2,2,"amber_dark")
    elif state=="rumpled":
        im.line(2,11,5,5,"red"); im.line(5,5,10,12,"red"); im.line(10,12,13,5,"red"); im.line(3,8,12,8,"amber_dark"); im.rect(6,6,3,3,"red")
    else:
        im.rect(3,5,10,7,"red"); im.rect(5,3,6,10,"amber_dark"); im.rect(6,5,4,5,"transparent"); im.rect(2,10,12,2,"red")
    return im


def warm_light():
    im=Image(164,82)
    im.rect(5,31,154,42,(225,142,56,22)); im.rect(18,22,126,49,(235,155,62,28)); im.rect(38,15,88,48,(245,177,73,36)); im.rect(55,8,56,44,(255,194,86,42))
    # break the masks into pixel-authentic stepped edges
    im.rect(5,31,12,5,"transparent"); im.rect(147,31,12,5,"transparent"); im.rect(18,22,12,5,"transparent"); im.rect(132,22,12,5,"transparent")
    return im


def main():
    ART.mkdir(parents=True, exist_ok=True)
    assets={
        "room_back.png":room_back(), "window_spring.png":window("spring"), "window_winter.png":window("winter"),
        "sleeping_nook_back.png":nook_back(), "sleeping_nook_front.png":nook_front(), "rug.png":rug(), "warm_light.png":warm_light(),
        "bookcase.png":bookcase(),
        "moss_idle.png":moss_pose("idle"), "moss_loaf.png":moss_pose("loaf"), "moss_carry.png":moss_pose("carry"),
    }
    for i in range(4): assets[f"moss_walk_{i}.png"]=moss_pose("walk",i); assets[f"moss_inspect_{i}.png"]=moss_pose("inspect",i)
    for state in ("loose","rumpled","nested"): assets[f"object_red_thread_{state}.png"]=object_thread(state)
    for kind in ("plant_small","plant_large","books","basket","pot","mug","frame","paper","cushion","blocks","stool","table","lamp","jar","candle","slippers","herb","bowl"):
        assets[f"prop_{kind}.png"]=simple_prop(kind)
    for name,im in assets.items(): im.save(ART/name)

    static=[
        {"id":"room-back","texture":"res://art/room_back.png","position":[0,0],"layer":"Background","z":0},
        {"id":"major-window","texture":"res://art/window_spring.png","position":[8,12],"layer":"Structure","z":0},
        {"id":"sleeping-nook-back","texture":"res://art/sleeping_nook_back.png","position":[9,164],"layer":"Structure","z":1},
        {"id":"living-rug","texture":"res://art/rug.png","position":[132,168],"layer":"Surface","z":0},
        {"id":"warm-light","texture":"res://art/warm_light.png","position":[0,158],"layer":"Atmosphere","z":1},
        {"id":"sleeping-nook-front","texture":"res://art/sleeping_nook_front.png","position":[9,164],"layer":"Foreground","z":2},
        # wall/surface details: individually addressable authored props
        {"id":"wall-frame-1","texture":"res://art/prop_frame.png","position":[164,34],"layer":"Structure","z":2},
        {"id":"wall-frame-2","texture":"res://art/prop_frame.png","position":[188,48],"layer":"Structure","z":2},
        {"id":"wall-herb-1","texture":"res://art/prop_herb.png","position":[148,72],"layer":"Structure","z":2},
        {"id":"wall-herb-2","texture":"res://art/prop_herb.png","position":[268,78],"layer":"Structure","z":2},
        {"id":"right-bookcase","texture":"res://art/bookcase.png","position":[316,24],"layer":"Structure","z":2},
        {"id":"nook-books","texture":"res://art/prop_books.png","position":[16,150],"layer":"Structure","z":3},
        {"id":"nook-candle","texture":"res://art/prop_candle.png","position":[42,145],"layer":"Structure","z":3},
        {"id":"nook-mug","texture":"res://art/prop_mug.png","position":[55,154],"layer":"Structure","z":3},
        {"id":"window-pot","texture":"res://art/prop_pot.png","position":[114,105],"layer":"Structure","z":3},
        {"id":"window-plant","texture":"res://art/prop_plant_small.png","position":[109,89],"layer":"Structure","z":4},
        {"id":"side-table","texture":"res://art/prop_table.png","position":[145,129],"layer":"Structure","z":2},
        {"id":"side-lamp","texture":"res://art/prop_lamp.png","position":[151,103],"layer":"Structure","z":3},
        {"id":"side-books","texture":"res://art/prop_books.png","position":[173,137],"layer":"Structure","z":3},
        {"id":"side-jar","texture":"res://art/prop_jar.png","position":[183,121],"layer":"Structure","z":3},
        {"id":"paper-wall","texture":"res://art/prop_paper.png","position":[225,111],"layer":"Structure","z":2},
    ]
    ys=[
        ("floor-plant-a","plant_large",176,216,12,38),("floor-plant-b","plant_small",254,205,9,27),
        ("basket-a","basket",119,228,11,17),("basket-b","basket",274,224,11,17),
        ("stool-a","stool",228,220,12,26),("cushion-a","cushion",198,216,10,13),
        ("blocks-a","blocks",247,226,6,9),("blocks-b","blocks",262,232,6,9),
        ("slippers-a","slippers",91,231,10,8),("bowl-a","bowl",153,226,8,9),
        ("jar-floor","jar",289,220,6,18),("mug-floor","mug",212,229,5,10),
        ("paper-floor-a","paper",182,224,7,9),("paper-floor-b","paper",193,230,7,9),
        ("pot-floor","pot",306,225,7,15),("books-floor","books",322,224,10,13),
        ("basket-c","basket",357,231,11,17),
    ]
    y_sorted=[{"id":id_,"texture":f"res://art/prop_{kind}.png","base":[x,y],"anchor":[ax,ay],"z":0} for id_,kind,x,y,ax,ay in ys]
    manifest={
        "schema":"terrarium.godot-slice-manifest.v1","art_surface":[400,240],"semantic_frame":[800,480],"authored_detail_instances":len(static)-6+len(y_sorted),
        "static":static,"y_sorted":y_sorted,
        "notes":"POC raster art is conventional engine-neutral PNG. Godot scene resources only compose it; canonical state stays in terrarium.frame.v1."
    }
    (ART/"slice_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"assets":len(assets),"detail_instances":manifest["authored_detail_instances"],"art":str(ART)}))


if __name__ == "__main__": main()
