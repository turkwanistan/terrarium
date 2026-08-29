from __future__ import annotations
import json, math, struct, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'art'
REPO = ROOT.parents[1]

P = {
 'clear':(0,0,0,0),'void':(12,10,10,255),'ink':(38,25,22,255),'ink2':(58,34,25,255),
 'wall0':(154,119,75,255),'wall1':(184,146,91,255),'wall2':(214,176,112,255),'wall3':(232,198,135,255),
 'wood0':(62,32,19,255),'wood1':(94,48,22,255),'wood2':(137,72,27,255),'wood3':(178,98,34,255),'wood4':(218,137,51,255),
 'floor0':(75,39,19,255),'floor1':(111,57,24,255),'floor2':(146,77,27,255),'floor3':(178,97,34,255),'floor4':(205,120,45,255),
 'blue0':(26,47,91,255),'blue1':(32,70,142,255),'blue2':(48,99,189,255),'blue3':(82,137,220,255),'blue4':(130,176,232,255),
 'green0':(31,55,26,255),'green1':(45,85,34,255),'green2':(65,118,42,255),'green3':(94,151,55,255),'green4':(144,184,67,255),
 'rug0':(31,73,41,255),'rug1':(43,107,52,255),'rug2':(58,139,61,255),'rug3':(88,163,68,255),
 'gold0':(142,80,25,255),'gold1':(193,119,30,255),'gold2':(239,164,49,255),'gold3':(255,204,87,255),
 'cream0':(167,140,102,255),'cream1':(210,185,143,255),'cream2':(239,218,177,255),'cream3':(255,240,201,255),
 'red0':(99,41,29,255),'red1':(153,54,32,255),'red2':(201,73,39,255),'red3':(232,104,51,255),
 'pot0':(90,43,24,255),'pot1':(144,67,28,255),'pot2':(195,91,34,255),'pot3':(227,127,48,255),
 'sky0':(65,66,120,255),'sky1':(105,80,151,255),'sky2':(233,93,81,255),'sky3':(255,154,71,255),'sky4':(255,208,99,255),
 'water0':(35,79,115,255),'water1':(50,111,145,255),'water2':(87,157,171,255),
 'dog0':(66,38,28,255),'dog1':(105,56,34,255),'dog2':(151,83,45,255),'dog3':(190,113,61,255),'dog4':(225,153,92,255),
 'muzzle0':(172,147,111,255),'muzzle1':(224,206,169,255),'muzzle2':(255,239,207,255),
 'stone0':(93,91,84,255),'stone1':(149,143,126,255),'stone2':(205,196,169,255),
 'shadow':(30,24,20,150),'rain':(137,181,199,255),'night':(37,43,69,255),'night2':(56,64,92,255),
}

def C(v): return P[v] if isinstance(v,str) else v

class Image:
 def __init__(self,w=400,h=240,fill='clear'):
  self.w=w; self.h=h; self.p=[list(C(fill)) for _ in range(w*h)]
 def set(self,x,y,col):
  if 0<=x<self.w and 0<=y<self.h:self.p[y*self.w+x]=list(C(col))
 def get(self,x,y): return self.p[y*self.w+x]
 def rect(self,x,y,w,h,col):
  q=C(col)
  for yy in range(max(0,y),min(self.h,y+h)):
   off=yy*self.w
   for xx in range(max(0,x),min(self.w,x+w)): self.p[off+xx]=list(q)
 def blend(self,x,y,col):
  if not(0<=x<self.w and 0<=y<self.h):return
  s=C(col); a=s[3]/255; d=self.get(x,y)
  self.p[y*self.w+x]=[int(s[i]*a+d[i]*(1-a)) for i in range(3)]+[255]
 def blend_rect(self,x,y,w,h,col):
  for yy in range(y,y+h):
   for xx in range(x,x+w): self.blend(xx,yy,col)
 def line(self,x0,y0,x1,y1,col):
  dx=abs(x1-x0); sx=1 if x0<x1 else -1; dy=-abs(y1-y0); sy=1 if y0<y1 else -1; err=dx+dy
  while True:
   self.set(x0,y0,col)
   if x0==x1 and y0==y1: break
   e=2*err
   if e>=dy: err+=dy; x0+=sx
   if e<=dx: err+=dx; y0+=sy
 def poly(self,pts,col):
  minx,maxx=max(0,min(x for x,_ in pts)),min(self.w-1,max(x for x,_ in pts)); miny,maxy=max(0,min(y for _,y in pts)),min(self.h-1,max(y for _,y in pts))
  for y in range(miny,maxy+1):
   for x in range(minx,maxx+1):
    inside=False; j=len(pts)-1
    for i,(xi,yi) in enumerate(pts):
     xj,yj=pts[j]
     if ((yi>y)!=(yj>y)) and x < (xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi: inside=not inside
     j=i
    if inside:self.set(x,y,col)
 def ellipse(self,cx,cy,rx,ry,col):
  for y in range(cy-ry,cy+ry+1):
   for x in range(cx-rx,cx+rx+1):
    if ((x-cx)**2)/(rx*rx or 1)+((y-cy)**2)/(ry*ry or 1)<=1:self.set(x,y,col)
 def save(self,path):
  raw=bytearray()
  for y in range(self.h):
   raw.append(0)
   for x in range(self.w): raw.extend(self.p[y*self.w+x])
  def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
  path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',self.w,self.h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b''))

def orect(im,x,y,w,h,fill,outline='ink',hi=None):
 im.rect(x,y,w,h,outline); im.rect(x+2,y+2,w-4,h-4,fill)
 if hi: im.rect(x+3,y+2,w-6,1,hi)

def speckle(im,x,y,w,h,cols,step=9):
 for yy in range(y+2,y+h-2,step):
  for xx in range(x+3,y*0+ x+w-2,step+3):
   k=(xx*13+yy*7)%len(cols); dx=((xx+yy)%5)-2; dy=((xx*3+yy)%3)-1
   im.set(xx+dx,yy+dy,cols[k])

def room_shell(im,mode):
 im.rect(0,0,400,240,'void')
 # outer timber frame
 im.rect(8,7,384,226,'ink'); im.rect(11,10,378,220,'wood0'); im.rect(14,13,372,214,'wood2'); im.rect(17,16,366,208,'ink2')
 # inner room
 wall='night2' if mode=='night' else 'wall1'; im.rect(20,19,360,72,wall)
 if mode!='night':
  im.rect(20,19,360,3,'wall3')
 # horizontal timber rail/wainscot
 im.rect(20,81,360,7,'wood0'); im.rect(20,83,360,3,'wood3'); im.rect(20,88,360,9,'wood1'); im.rect(20,91,360,3,'wood2')
 # floor
 im.rect(20,97,360,127,'floor1')
 for y in range(98,224,13):
  im.rect(20,y,360,1,'floor0'); im.rect(20,y+1,360,1,'floor3')
  offset=0 if ((y-98)//13)%2==0 else 27
  for x in range(20-offset,381,54): im.rect(x,y,1,13,'floor0')
 # plank grain
 for y in range(104,220,13):
  for x in range(28,374,31):
   if (x+y)%4: im.rect(x,y,10+(x%8),1,'floor2')
   if (x*3+y)%5==0: im.rect(x+4,y+3,7,1,'floor0')
 # inside frame highlights + corner caps
 im.rect(14,13,372,3,'wood4'); im.rect(14,224,372,3,'wood0'); im.rect(14,16,3,208,'wood4'); im.rect(383,16,3,208,'wood0')
 for x,y in ((9,8),(371,8),(9,211),(371,211)):
  orect(im,x,y,20,18,'wood2','ink2','wood4'); im.line(x+3,y+3,x+16,y+14,'wood1'); im.line(x+16,y+3,x+3,y+14,'wood3')

def window(im,mode):
 x,y,w,h=72,31,105,53
 # outer carved frame
 im.rect(x-4,y-4,w+8,h+8,'ink'); im.rect(x-2,y-2,w+4,h+4,'wood1'); im.rect(x,y,w,h,'wood3'); im.rect(x+4,y+4,w-8,h-8,'ink')
 glass='night' if mode=='night' else 'sky1' if mode=='rain' else 'sky2'; im.rect(x+7,y+7,w-14,h-14,glass)
 if mode=='night':
  im.rect(x+7,y+30,w-14,16,'water0'); im.poly([(x+7,y+28),(x+26,y+19),(x+43,y+27),(x+62,y+14),(x+82,y+29),(x+w-7,y+22),(x+w-7,y+34),(x+7,y+34)],'green0')
  for sx,sy in ((84,43),(102,36),(143,48),(159,39)): im.rect(sx,sy,1,1,'cream3')
 else:
  im.rect(x+7,y+7,w-14,7,'sky3'); im.rect(x+7,y+14,w-14,5,'sky4')
  im.poly([(x+7,y+34),(x+25,y+23),(x+42,y+31),(x+61,y+20),(x+80,y+32),(x+w-7,y+25),(x+w-7,y+39),(x+7,y+39)],'green0')
  im.poly([(x+7,y+37),(x+25,y+29),(x+43,y+35),(x+62,y+27),(x+81,y+36),(x+w-7,y+31),(x+w-7,y+41),(x+7,y+41)],'green2')
  im.rect(x+7,y+40,w-14,6,'water1'); im.rect(x+17,y+42,70,1,'water2'); im.rect(x+50,y+43,18,1,'sky4')
  im.ellipse(x+51,y+16,6,4,'gold3'); im.rect(x+47,y+16,8,1,'sky4')
 # mullions
 im.rect(x+51,y+4,4,h-8,'ink'); im.rect(x+4,y+25,w-8,4,'ink'); im.rect(x+52,y+5,1,h-10,'wood4'); im.rect(x+5,y+26,w-10,1,'wood4')
 # curtains thick blue with folds
 for side in (0,1):
  bx=x-12 if side==0 else x+w-2
  pts=[(bx,y-6),(bx+16,y-6),(bx+14,y+16),(bx+17,y+28),(bx+11,y+48),(bx+4,y+51),(bx+1,y+38),(bx+4,y+22)] if side==0 else [(bx+12,y-6),(bx-4,y-6),(bx-2,y+16),(bx-5,y+28),(bx+1,y+48),(bx+8,y+51),(bx+11,y+38),(bx+8,y+22)]
  im.poly(pts,'blue0');
  if side==0:
   im.poly([(bx+4,y-4),(bx+9,y-4),(bx+9,y+42),(bx+5,y+46)],'blue2'); im.rect(bx+10,y+1,3,36,'blue1'); im.rect(bx+2,y+23,15,4,'gold1')
  else:
   im.poly([(bx+1,y-4),(bx+6,y-4),(bx+5,y+42),(bx+1,y+46)],'blue2'); im.rect(bx-2,y+1,3,36,'blue1'); im.rect(bx-5,y+23,15,4,'gold1')
 # curtain rod and finials
 im.rect(x-15,y-10,w+30,4,'ink'); im.rect(x-13,y-9,w+26,2,'wood4'); im.ellipse(x-16,y-8,4,4,'ink'); im.ellipse(x-16,y-8,2,3,'gold2'); im.ellipse(x+w+15,y-8,4,4,'ink'); im.ellipse(x+w+15,y-8,2,3,'gold2')
 if mode=='rain':
  for rx in range(x+10,x+w-8,9):
   st=(rx*7)%8
   for yy in range(y+9+st,y+h-8,8): im.rect(rx,yy,1,4,'rain')

def wall_decor(im):
 # left framed art
 orect(im,35,35,24,21,'wood2','ink','wood4'); orect(im,40,39,14,12,'sky1','wood0'); im.poly([(42,49),(47,43),(51,47),(54,45),(54,50),(42,50)],'green2'); im.set(49,42,'gold3')
 # hanging plant center
 im.line(207,24,202,33,'gold1'); im.line(207,24,212,33,'gold1'); im.line(202,33,212,33,'gold1')
 for ox,oy,c in ((198,34,'green2'),(204,31,'green3'),(210,35,'green1'),(200,40,'green3'),(208,42,'green2'),(214,38,'green4')):
  im.ellipse(ox,oy,5,4,c); im.set(ox,oy-2,'green4')
 im.ellipse(207,44,8,5,'blue1'); im.rect(202,44,10,3,'blue2')
 # small right frame
 orect(im,258,32,18,19,'wood2','ink','wood4'); im.rect(263,37,8,9,'cream2'); im.poly([(264,44),(267,39),(270,44)],'green2')

def bed(im):
 x,y=62,107
 # shadow
 im.rect(x+2,y+43,70,5,'shadow')
 # posts
 for px in (x-4,x+69):
  im.rect(px,y-7,9,52,'ink'); im.rect(px+2,y-5,5,48,'wood2'); im.ellipse(px+4,y-8,5,5,'ink'); im.ellipse(px+4,y-8,3,3,'wood4')
 # rails/mattress
 orect(im,x,y,72,39,'wood2','ink','wood4'); im.rect(x+6,y+5,60,24,'cream1'); im.rect(x+7,y+6,59,6,'cream3'); im.rect(x+7,y+12,18,16,'cream2')
 # pillow texture
 im.rect(x+9,y+8,16,12,'cream3'); im.rect(x+10,y+19,14,2,'cream0'); im.set(x+13,y+10,'cream1'); im.set(x+21,y+16,'cream1')
 # red + blue blanket with stitched shade
 im.rect(x+27,y+7,18,22,'red2'); im.rect(x+45,y+7,21,22,'blue2'); im.rect(x+28,y+7,17,2,'red3'); im.rect(x+46,y+7,20,2,'blue3'); im.rect(x+42,y+7,3,22,'red0'); im.rect(x+62,y+9,2,17,'blue1')
 im.rect(x-2,y+32,76,6,'wood0'); im.rect(x,y+33,72,3,'wood3')

def desk(im):
 x,y=200,88
 # shadow and top
 im.rect(x+3,y+39,89,5,'shadow'); orect(im,x,y,90,13,'wood2','ink','wood4'); im.rect(x+3,y+5,84,3,'wood3')
 # legs
 for px in (x+6,x+79): orect(im,px,y+11,9,36,'wood1','ink','wood3')
 # cross apron
 im.rect(x+12,y+13,70,7,'ink2'); im.rect(x+14,y+14,66,4,'wood2')
 # stool
 orect(im,x+31,y+39,31,9,'wood2','ink','wood4'); orect(im,x+37,y+47,8,19,'wood1','ink'); orect(im,x+50,y+47,8,19,'wood1','ink'); im.rect(x+38,y+58,19,4,'ink2'); im.rect(x+39,y+59,17,2,'wood2')
 # book stack left
 for yy,col,w in ((y-8,'blue1',21),(y-12,'red1',18),(y-16,'green1',15)):
  orect(im,x+5,yy,w,5,col,'ink',None); im.rect(x+7,yy+1,w-5,1,'cream1')
 # open book
 im.rect(x+38,y-9,30,13,'ink'); im.poly([(x+40,y-7),(x+52,y-9),(x+53,y+2),(x+40,y+1)],'cream2'); im.poly([(x+54,y-9),(x+66,y-7),(x+66,y+1),(x+53,y+2)],'cream3'); im.line(x+53,y-8,x+53,y+1,'cream0'); im.rect(x+43,y-4,8,1,'cream0'); im.rect(x+56,y-4,8,1,'cream0')
 # lamp
 im.rect(x+69,y-21,5,20,'ink'); im.rect(x+71,y-19,1,17,'gold1'); im.ellipse(x+71,y-23,11,7,'ink'); im.ellipse(x+71,y-23,9,5,'gold2'); im.rect(x+65,y-25,12,2,'gold3'); im.rect(x+66,y-1,12,3,'ink')
 # pen cups
 for cx,c in ((x+78,'blue1'),(x+84,'blue2')):
  orect(im,cx,y-11,6,11,c,'ink');
 for px in (x+79,x+82,x+86,x+89): im.line(px,y-13,px-1,y-22,'ink2')

def bookcase(im):
 x,y=318,51
 im.rect(x+3,y+2,51,87,'shadow'); orect(im,x,y,52,84,'wood1','ink','wood4'); im.rect(x+4,y+4,44,76,'wood0')
 # crown
 im.rect(x-3,y-4,58,8,'ink'); im.rect(x-1,y-2,54,5,'wood3'); im.rect(x+2,y-1,48,2,'wood4')
 # shelves
 for sy in (y+22,y+44,y+64): im.rect(x+4,sy,44,5,'ink'); im.rect(x+6,sy+1,40,2,'wood3')
 # books with bands
 colors=['blue1','cream2','green1','blue2','red1','gold1']
 for row,sy in enumerate((y+7,y+29)):
  xx=x+7
  for i,w in enumerate((5,4,5,4,5,5)):
   h=12-((i+row)%3); col=colors[(i+row)%len(colors)]; im.rect(xx,sy+12-h,w,h,'ink'); im.rect(xx+1,sy+13-h,w-2,h-2,col); im.rect(xx+1,sy+15-h,w-2,1,'gold1' if i%2 else 'cream0'); xx+=w+2
 # plant shelf
 im.rect(x+32,y+51,9,8,'cream2'); im.rect(x+34,y+48,5,4,'green1'); im.ellipse(x+34,y+46,4,3,'green3'); im.ellipse(x+40,y+45,4,3,'green2')
 # drawer
 orect(im,x+8,y+68,36,11,'wood2','ink','wood4'); im.ellipse(x+26,y+73,2,2,'gold2')
 # trailing plant on top/right
 for ox,oy in ((x+40,y-11),(x+46,y-9),(x+50,y-3),(x+51,y+4),(x+49,y+11),(x+47,y+18)):
  im.ellipse(ox,oy,5,4,'green1'); im.ellipse(ox+1,oy-1,3,2,'green4')

def rug(im):
 x,y,w,h=148,143,171,73
 # contact shadow + ornate edges
 im.rect(x+2,y+3,w,h,'shadow'); im.rect(x,y,w,h,'ink'); im.rect(x+3,y+3,w-6,h-6,'rug0'); im.rect(x+6,y+6,w-12,h-12,'rug2'); im.rect(x+9,y+9,w-18,h-18,'rug1')
 # gold stitched inner border
 for xx in range(x+12,x+w-12,7): im.rect(xx,y+11,4,1,'gold2'); im.rect(xx,y+h-12,4,1,'gold1')
 for yy in range(y+14,y+h-14,7): im.rect(x+11,yy,1,4,'gold2'); im.rect(x+w-12,yy,1,4,'gold1')
 # motifs
 for mx,my in ((170,161),(206,160),(243,161),(280,160),(187,193),(225,196),(266,192),(299,190)):
  im.set(mx,my,'gold2'); im.set(mx-2,my,'gold1'); im.set(mx+2,my,'gold1'); im.set(mx,my-2,'gold1'); im.set(mx,my+2,'gold1')
 # fringes
 for yy in range(y+7,y+h-7,6): im.rect(x-2,yy,2,3,'stone2'); im.rect(x+w,yy,2,3,'stone1')

def left_floor_cluster(im):
 # blue pouf
 cx,cy=46,175; im.ellipse(cx,cy+4,18,12,'ink'); im.ellipse(cx,cy,16,11,'blue1'); im.ellipse(cx,cy-1,12,8,'blue2'); im.ellipse(cx,cy-1,5,4,'blue1');
 for ang in range(0,360,45):
  dx=int(math.cos(math.radians(ang))*11); dy=int(math.sin(math.radians(ang))*6); im.line(cx,cy,cx+dx,cy+dy,'blue0')
 # book basket
 orect(im,77,169,31,24,'wood1','ink','wood4'); im.rect(81,166,5,21,'blue2'); im.rect(87,163,5,24,'red2'); im.rect(93,165,5,22,'green2'); im.rect(99,168,5,19,'gold1')
 # bone and ball
 draw_bone(im,79,204); draw_ball(im,99,202,6)

def draw_bone(im,x,y):
 im.rect(x+3,y+1,12,4,'cream3'); im.ellipse(x+2,y+2,3,3,'cream3'); im.ellipse(x+16,y+2,3,3,'cream3'); im.set(x+4,y+2,'cream0'); im.set(x+14,y+4,'cream0')
def draw_ball(im,x,y,r):
 im.ellipse(x,y,r,r,'ink'); im.ellipse(x,y,r-2,r-2,'red2'); im.line(x-r+2,y+2,x+r-2,y-2,'gold1'); im.line(x,y-r+2,x+2,y+r-2,'red0')
def bowl(im,x,y):
 im.ellipse(x,y,11,7,'ink'); im.ellipse(x,y-1,9,5,'blue2'); im.rect(x-8,y-1,16,4,'blue1'); im.ellipse(x,y-2,6,3,'dog0');
 for dx,dy in ((-2,-2),(2,-1),(0,0)): im.set(x+dx,y+dy,'dog3')
def floor_plant(im):
 # right floor plant
 x,y=351,174; orect(im,x-8,y+17,18,17,'pot1','ink','pot3'); im.rect(x-6,y+20,14,2,'pot3'); im.rect(x,y-1,2,20,'green0')
 for ox,oy,rx,ry,c in ((-8,6,8,5,'green2'),(8,7,8,5,'green3'),(-5,-2,7,6,'green3'),(6,-4,7,6,'green2'),(0,-11,6,8,'green4')):
  im.ellipse(x+ox,y+oy,rx,ry,c); im.line(x+ox,y+oy,x,y+14,'green0')

def rug_props(im):
 bowl(im,281,186); draw_ball(im,253,205,6); draw_bone(im,302,204)

def foreground(im):
 # Transparent persistent foreground: only genuine always-front foliage.
 f=Image(400,240)
 for ox,oy,c in ((365,189,'green1'),(372,183,'green2'),(378,195,'green3')): f.ellipse(ox,oy,8,5,c)
 return f

def bed_front_lip():
 # Full-surface transparent support occluder, enabled only during sleep/wake staging.
 f=Image(400,240)
 x,y=62,107
 f.rect(x-2,y+32,76,6,'wood0'); f.rect(x,y+33,72,3,'wood3')
 for xx in range(x+5,x+68,11): f.set(xx,y+33,'wood4')
 return f



def polish_surface_texture(im, mode):
    # Curated material clusters only. Broad procedural peppering made the plaster/floor read dirty.
    if mode != 'night':
        # Small connected plaster flecks, kept off the window, Moss field, and major silhouettes.
        for x,y,w,col in (
            (35,34,3,'wall2'),(54,67,2,'wall0'),(196,31,3,'wall2'),(229,63,2,'wall0'),
            (282,38,3,'wall2'),(306,70,2,'wall3'),(353,31,3,'wall2'),(365,66,2,'wall0')):
            im.rect(x,y,w,1,col)
            if (x+y)%2 == 0: im.set(x+1,y+1,'wall1')
    # Floor grain follows plank direction and is intentionally sparse/irregular rather than a dot field.
    for x,y,w,col in (
        (31,107,9,'floor3'),(66,121,6,'floor0'),(143,109,11,'floor3'),(177,135,7,'floor0'),
        (300,107,10,'floor3'),(337,121,7,'floor0'),(31,160,8,'floor3'),(111,173,12,'floor0'),
        (322,174,9,'floor3'),(45,201,11,'floor0'),(116,214,7,'floor3'),(331,212,10,'floor0')):
        im.rect(x,y,w,1,col)
        if w >= 9: im.rect(x+3,y+1,3,1,'floor2' if col=='floor3' else 'floor1')
    # A few connected knots/scuffs, each attached to nearby grain rather than floating alone.
    for x,y in ((151,151),(211,151),(282,169),(332,157)):
        im.rect(x-2,y,5,1,'floor0'); im.rect(x,y+1,2,1,'wood1')
    # Inner timber wear uses tiny dashes rather than evenly spaced isolated points.
    for x in (41,93,166,247,329): im.rect(x,84,3,1,'wood4')
    for y in (112,151,193): im.rect(22,y,1,3,'floor4')

def polish_window_details(im, mode):
    # extra curtain fold clusters, tie-back sparkle, sill wear, window reflections
    for x in (63,68,176,181):
        for y in range(31,76,9):
            im.rect(x,y,2,5,'blue3' if x in (68,176) else 'blue0')
    im.rect(62,52,10,2,'gold2'); im.set(64,51,'gold3')
    im.rect(173,52,10,2,'gold2'); im.set(180,51,'gold3')
    # carved sill edge
    im.rect(70,82,111,3,'ink2'); im.rect(73,82,105,1,'wood4')
    for x in (79,104,145,166): im.set(x,84,'wood0')
    if mode == 'day':
        # sunset reflection sparkles and water glints
        for x,y in ((93,44),(119,41),(150,47),(112,72),(128,73),(154,71)):
            im.rect(x,y,2,1,'sky4')
    elif mode == 'rain':
        for x,y in ((91,41),(117,48),(143,44),(162,59)):
            im.rect(x,y,1,3,'rain')

def polish_bed_and_desk(im):
    # Bedding seams / connected creases; avoid isolated dirt-like pixels.
    for x in (72,88,104,116): im.rect(x,120,3,1,'cream0')
    im.rect(90,116,1,16,'red3'); im.rect(108,116,1,16,'blue4')
    for x,y,w in ((75,118,3),(82,125,4),(96,127,3),(114,121,4)):
        im.rect(x,y,w,1,'cream1')
    # Warmer hand-authored post highlights.
    for x in (60,133):
        im.rect(x+2,101,2,1,'wood4'); im.set(x+3,102,'gold1')
    # Desktop edge wear and paper/book detail as short marks, not a dotted ruler.
    for x in (208,231,259,279): im.rect(x,91,3,1,'wood4')
    for x in (241,258): im.rect(x,81,7,1,'cream0')
    im.rect(270,69,3,1,'gold3'); im.set(272,70,'cream3')
    # Stool edge wear.
    im.rect(236,135,18,1,'wood4'); im.rect(241,143,3,1,'wood3')

def polish_bookcase(im):
    # Crown bevel, shelf pegs, varied spine labels: keep microdetail attached to actual shelf contents.
    im.rect(319,47,50,1,'wood4'); im.rect(321,48,3,1,'gold1'); im.rect(363,48,3,1,'wood0')
    for x,y in ((327,63),(337,61),(347,64),(358,62),(326,85),(342,83),(354,86)):
        im.rect(x,y,2,1,'cream3')
        if (x+y)%2: im.rect(x,y+2,2,1,'gold2')
    for y in (74,96,116):
        im.rect(324,y,2,1,'wood4'); im.rect(365,y,2,1,'wood0')
    # Plant leaf highlights / irregular trailing silhouette remain paired clusters.
    for x,y in ((355,43),(361,46),(366,52),(368,58),(364,66),(361,72)):
        im.rect(x,y,2,1,'green4'); im.set(x-1,y+1,'green2')

def polish_rug_and_props(im):
    # Rug border stitches are short woven dashes; broad single-pixel fiber scatter was removed.
    for x in (162,186,213,241,271,299):
        im.rect(x,151,3,1,'gold3'); im.rect(x+1,207,3,1,'gold1')
    for y in (158,178,198):
        im.rect(156,y,1,3,'gold2'); im.rect(310,y+2,1,3,'gold1')
    # Four restrained interior fiber/crease clusters, deliberately away from Moss's face/body field.
    for x,y in ((176,175),(215,169),(287,178),(300,202)):
        im.rect(x,y,3,1,'rug3'); im.rect(x+1,y+1,2,1,'green4')
    # Bowl rim + toy/bone connected highlights.
    im.rect(277,182,2,1,'blue4'); im.rect(283,183,2,1,'blue3')
    im.rect(249,202,2,1,'gold2'); im.rect(303,202,2,1,'cream3')
    # Pouf tuft glints / book basket lip.
    for x,y in ((40,170),(46,167),(52,171)): im.rect(x,y,2,1,'blue4')
    im.rect(78,168,29,1,'wood4')

def polish_plants(im):
    # Connected leaf clusters make foliage feel authored without sparkle noise.
    for x,y in ((348,163),(354,158),(359,171),(344,176),(360,184),(202,36),(207,31),(211,40),(362,79)):
        im.rect(x,y,2,1,'green4')
        im.rect(x+1,y+1,2,1,'green1')
    im.rect(349,195,2,1,'pot3'); im.rect(350,193,2,1,'gold1')

def polish_scene(im, mode):
    polish_surface_texture(im, mode)
    polish_window_details(im, mode)
    polish_bed_and_desk(im)
    polish_bookcase(im)
    polish_rug_and_props(im)
    polish_plants(im)

def polish_moss(im, asset):
    # Character charm pass: preserve accepted identity/silhouette, add reference-like clustered fur and facial readability.
    # softer forehead blaze and cheek volume
    for x,y,col in ((36,8,'muzzle2'),(37,8,'muzzle2'),(35,9,'muzzle1'),(38,9,'muzzle2'),
                    (40,15,'muzzle2'),(41,15,'muzzle2'),(42,16,'muzzle1')):
        im.set(x,y,col)
    # eye catchlight, brow, nose shine and mouth corner
    im.set(38,12,'muzzle2'); im.set(39,12,'ink')
    im.set(46,16,'muzzle2'); im.set(47,16,'ink')
    im.set(45,19,'ink2'); im.set(44,20,'dog0')
    # ear depth / warm inner rim
    for x,y in ((28,13),(29,14),(29,16),(30,18),(31,19)):
        im.set(x,y,'dog1')
    for x,y in ((29,12),(30,13),(30,15)): im.set(x,y,'dog3')
    # clustered fur texture on shoulder/back, not random noise
    for x,y,col in ((22,22,'dog4'),(25,22,'dog3'),(28,23,'dog4'),(18,27,'dog3'),(21,30,'dog4'),
                    (25,31,'dog3'),(30,28,'dog4'),(17,33,'dog1'),(29,34,'dog1')):
        im.set(x,y,col)
    # chest/leg separation + tiny cream toes
    im.set(36,31,'muzzle2'); im.set(37,32,'muzzle1')
    for x,y in ((20,41),(22,41),(35,41),(37,41)): im.set(x,y,'muzzle2')
    # tiny warm tail sparkle
    im.set(7,22,'dog4'); im.set(8,23,'dog3')
    # Slightly rounder crown/cheek/ear silhouette for a cuter hero read at gameplay scale.
    for x,y,col in ((33,7,'dog2'),(34,7,'dog3'),(40,8,'dog3'),(43,9,'dog2'),
                    (27,11,'dog0'),(26,13,'dog0'),(26,15,'dog1'),(27,18,'dog1'),
                    (46,14,'dog1'),(47,16,'muzzle1'),(47,18,'muzzle2')):
        im.set(x,y,col)
    # Brighter blaze/chest geometry, inspired by the supplied reference without changing Moss's palette family.
    im.rect(36,8,3,3,'muzzle2'); im.set(39,9,'muzzle1')
    im.rect(36,27,3,7,'muzzle2'); im.set(35,30,'muzzle1')
    # Warm body speckles / shoulder highlights are deliberately clustered rather than random.
    for x,y,col in ((20,25,'dog4'),(23,26,'dog3'),(26,27,'dog4'),(18,29,'dog1'),
                    (22,32,'dog4'),(27,33,'dog3'),(31,30,'dog1')):
        im.set(x,y,col)
    # Friendly mouth/tongue cue: only two pixels, enough to soften the profile.
    im.set(44,20,'ink'); im.set(45,21,'red3')



def audit_selective_edges(im):
    # Break the uniform sticker-outline read on major furniture: warm light-facing edges,
    # dark weighted undersides, and small intentional gaps/edge highlights.
    # Bed frame/post highlights
    for x0,x1,y in ((64,130,106),(64,130,138)):
        for x in range(x0,x1):
            if x % 9 not in (0,1): im.set(x,y,'wood4')
    for x,y in ((59,111),(59,121),(134,113),(134,125)):
        im.set(x,y,'wood3')
    # Desk top selectively warm, underside remains dark
    for x in range(204,287):
        if x % 13 not in (0,1,2): im.set(x,89,'wood4')
    im.rect(204,100,80,2,'wood0')
    # Bookcase crown/top edge and shelf lips
    for x in range(320,368):
        if x % 11 not in (0,1): im.set(x,48,'wood4')
    for y in (74,96,116):
        for x in range(324,366):
            if x % 8 not in (0,1): im.set(x,y,'wood3')
    # Rug: colored/chromatic edge on lit top/left, dark bottom/right
    for x in range(153,314):
        if x % 10 not in (0,1): im.set(x,145,'rug3')
    for y in range(149,212):
        if y % 9 not in (0,1): im.set(150,y,'rug3')
    im.rect(151,214,166,2,'rug0')
    im.rect(317,149,2,65,'rug0')

def audit_bevel_furniture(im):
    # Add shallow top planes / bevels to match the reference's pragmatic 3/4 asset grammar.
    # Bed top rail and mattress lip
    im.poly([(62,106),(134,106),(130,102),(66,102)],'wood3')
    im.line(66,102,130,102,'wood4')
    im.rect(68,110,58,2,'cream3')
    im.set(67,111,'cream1'); im.set(127,111,'cream0')
    # Desk slab top plane
    im.poly([(198,88),(290,88),(286,84),(203,84)],'wood3')
    im.line(203,84,286,84,'wood4')
    im.rect(202,96,86,2,'wood0')
    # Stool top plane
    im.poly([(231,127),(262,127),(258,124),(235,124)],'wood3')
    im.line(235,124,258,124,'wood4')
    # Bookcase crown/top plane + feet
    im.poly([(315,47),(373,47),(369,43),(319,43)],'wood3')
    im.line(319,43,369,43,'wood4')
    im.rect(322,135,8,6,'wood0'); im.rect(360,135,8,6,'wood0')
    im.set(323,136,'wood3'); im.set(361,136,'wood3')
    # Slight perspective corners on rug instead of perfectly rectangular slab
    for x,y in ((148,143),(318,143),(148,215),(318,215)):
        im.set(x,y,'floor1')

def audit_contact_shadows(im):
    # Strong, compact contact shadows like the reference—not blurry lighting.
    # Bed, desk, stool, bookcase, plant, pouf/basket.
    im.blend_rect(61,145,76,4,(28,20,16,125))
    im.blend_rect(201,133,90,4,(28,20,16,115))
    im.blend_rect(230,147,34,3,(28,20,16,110))
    im.blend_rect(316,140,56,4,(28,20,16,140))
    im.blend_rect(337,210,31,3,(28,20,16,120))
    im.blend_rect(28,187,38,3,(28,20,16,95))
    im.blend_rect(75,193,36,3,(28,20,16,95))
    # Reassert lit feet over shadows where needed.
    im.rect(322,135,8,6,'wood0'); im.rect(360,135,8,6,'wood0')

def audit_bedside_cluster(im):
    # The reference's left-side plant/books/candle cluster is a major cozy storytelling anchor.
    # Small bedside chest/table, compact enough not to crowd the bed.
    x,y=27,104
    im.blend_rect(x+2,y+31,29,3,(28,20,16,110))
    orect(im,x,y+8,28,28,'wood1','ink2','wood4')
    im.rect(x+3,y+12,22,5,'wood2')
    for dy in (19,28):
        im.rect(x+5,y+dy,18,6,'wood0'); im.rect(x+7,y+dy+1,14,3,'wood2'); im.set(x+13,y+dy+2,'gold2')
    # Plant in ceramic pot
    im.ellipse(x+13,y+4,6,4,'green2'); im.ellipse(x+8,y+6,5,4,'green3'); im.ellipse(x+18,y+6,5,4,'green1')
    im.set(x+10,y+2,'green4'); im.set(x+18,y+4,'green4')
    im.rect(x+8,y+8,11,5,'cream2'); im.rect(x+9,y+9,9,2,'cream3'); im.rect(x+10,y+12,7,2,'cream0')
    # Book stack + candle on bed-side ledge just above bed rail
    for bx,by,w,col in ((45,101,15,'blue1'),(43,98,17,'red2'),(46,95,13,'green1')):
        im.rect(bx,by,w,4,'ink2'); im.rect(bx+1,by+1,w-2,2,col); im.set(bx+2,by+1,'cream1')
    im.rect(61,93,5,10,'cream2'); im.rect(60,102,7,2,'wood0'); im.set(63,91,'gold3'); im.set(63,92,'gold2')

def audit_material_depth(im, mode):
    # Material depth stays clustered and directional; no floating knot dots.
    for x,y in ((31,111),(48,129),(84,153),(117,165),(173,126),(247,118),(361,119)):
        im.rect(x-2,y,5,1,'floor0')
        im.rect(x,y+1,2,1,'wood1')
        if (x+y)%2: im.rect(x+2,y,2,1,'floor4')
    # Warm top-left accents stay attached to their props.
    for x,y,col in ((35,170,'blue4'),(82,169,'wood4'),(348,187,'green4'),(276,181,'blue4'),(207,31,'green4')):
        im.rect(x,y,2,1,col)
    # A few short warm timber wear marks; the old repeated one-pixel cadence looked procedural.
    if mode == 'day':
        for x,y,w in ((30,86,5),(156,86,6),(318,86,5),(54,219,7),(315,219,6)):
            im.rect(x,y,w,1,'wood3')

def audit_reference_finish(im, mode):
    # Reference rug has chunky pale side tassels/rope knots rather than thin dashed fringe.
    for yy in range(153,208,7):
        im.ellipse(147,yy,3,2,'stone1'); im.ellipse(146,yy-1,2,2,'cream2'); im.set(145,yy-1,'cream3')
        im.ellipse(320,yy,3,2,'stone1'); im.ellipse(321,yy-1,2,2,'cream2'); im.set(322,yy-1,'cream3')
    # More floral stitched motifs with dark centers, keeping the field calm.
    for mx,my in ((176,166),(209,166),(244,166),(280,166),(193,190),(229,194),(269,190),(298,187)):
        im.set(mx,my,'gold0')
        for dx,dy in ((-2,0),(2,0),(0,-2),(0,2)):
            im.set(mx+dx,my+dy,'gold2')
            if (mx+my+dx+dy)%2: im.set(mx+dx+(1 if dx<0 else -1 if dx>0 else 0),my+dy,'gold3')
    # Bed: rounder post caps and cloth fold/shadow pixels.
    for cx in (62,135):
        im.ellipse(cx,99,5,5,'ink2'); im.ellipse(cx,98,3,3,'wood3'); im.set(cx-1,97,'wood4')
    im.rect(70,112,55,2,'cream3'); im.rect(70,130,55,2,'cream0')
    for x,y,col in ((78,119,'cream1'),(84,126,'cream0'),(94,121,'red3'),(102,128,'red0'),(115,118,'blue4'),(120,127,'blue0')):
        im.set(x,y,col)
    # Desk bevel was reading like a bright stripe; make it a warm wooden edge with sparse glints.
    im.line(203,84,286,84,'wood3')
    for x in range(207,284,13): im.rect(x,84,4,1,'wood4')
    im.rect(204,89,82,1,'wood3')
    for x in range(207,284,17): im.set(x,89,'wood4')
    # Break perfect ellipse foliage silhouettes with hand-placed leaf tips/highlights.
    for x,y,col in ((340,169,'green3'),(345,160,'green4'),(354,154,'green3'),(362,169,'green4'),
                    (341,180,'green2'),(359,184,'green3'),(197,34,'green3'),(203,28,'green4'),(215,36,'green3'),
                    (356,42,'green3'),(369,55,'green4'),(366,69,'green2')):
        im.rect(x,y,2,1,col); im.set(x+(1 if x%2 else -1),y-1,col)
    # Tiny warm highlight hierarchy on upper/light-facing object edges.
    for x,y in ((29,113),(31,112),(48,100),(52,97),(321,44),(338,44),(357,44),(78,169),(349,191)):
        im.set(x,y,'wood4' if y>90 else 'gold2')

def audit_pass(im, mode):
    audit_contact_shadows(im)
    audit_bedside_cluster(im)
    audit_bevel_furniture(im)
    audit_material_depth(im, mode)
    audit_selective_edges(im)
    audit_reference_finish(im, mode)

def apply_mode(im,mode):
 if mode=='rain':
  im.blend_rect(20,19,360,205,(39,63,82,38));
  for x in range(83,167,11):
   for y in range(42,76,9): im.rect(x,y,1,4,'rain')
 elif mode=='night':
  im.blend_rect(20,19,360,205,(24,33,62,88))
  # Restrained pixel-native local light: stepped pools tied to the desk lamp, no giant cone.
  im.blend_rect(247,76,48,27,(239,170,72,42))
  im.blend_rect(235,101,64,20,(239,164,63,34))
  im.blend_rect(222,121,88,13,(229,142,53,24))
  im.rect(263,65,16,2,'gold3')

def base_scene(mode):
 im=Image(); room_shell(im,mode); window(im,mode); wall_decor(im); bed(im); desk(im); bookcase(im); rug(im); left_floor_cluster(im); floor_plant(im); rug_props(im); apply_mode(im,mode); polish_scene(im,mode); audit_pass(im,mode); return im


def pose_safe_moss_finish(im):
 # Material-only finish for action poses whose geometry differs from the baseline idle/walk set.
 # It never paints outside an already-authored opaque silhouette.
 original=[px[:] for px in im.p]
 def old(x,y):
  if 0<=x<im.w and 0<=y<im.h: return original[y*im.w+x]
  return [0,0,0,0]
 dog0=list(P['dog0']); dog2=list(P['dog2']); dog4=list(P['dog4']); cream=list(P['muzzle1'])
 for y in range(im.h):
  for x in range(im.w):
   px=old(x,y)
   if px[3] != 255: continue
   above=old(x,y-1); below=old(x,y+1)
   if above[3] == 0:
    if px == dog2: im.set(x,y,'dog3')
    elif px == dog0 and (x+y)%3: im.set(x,y,'dog1')
    elif px == cream: im.set(x,y,'muzzle2')
   elif below[3] == 0 and px == dog2:
    im.set(x,y,'dog1')
   elif px == dog2 and ((x*7+y*11)%29==0):
    im.set(x,y,'dog3')
 return im

# Adapt the existing authored persistent-object silhouettes into the approved Godot material family.
# Object identity/state remains canonical; this table only translates established palette roles.
OBJECT_MAP={
 'shadow':(31,23,18,110),
 'amber':P['gold2'],'brass':P['gold1'],
 'cream':P['cream2'],'creamShade':P['cream0'],
 'dustyBlue':P['blue2'],'rain':P['water2'],'skyDark':P['blue0'],'glassLight':P['blue4'],
 'flower':P['red3'],'terracotta':P['red1'],
 'walnut':P['wood2'],'walnutDark':P['wood0'],'walnutLight':P['wood3'],'woodGold':P['wood4'],
}
def object_asset(source_stem):
 data=json.loads((REPO/'display'/'art'/'objects'/f'{source_stem}.json').read_text()); im=Image(data['width'],data['height'])
 for x,y,w,h,role in data['runs']: im.rect(x,y,w,h,OBJECT_MAP[role])
 return im

LIVE_OBJECT_SOURCES={
 'blue_stone': {'settled':'blue-stone-settled','rolled':'blue-stone-rolled'},
 'amber_leaf': {'fresh':'amber-leaf-fresh','handled':'amber-leaf-handled'},
 'acorn': {'settled':'acorn-settled','rolled':'acorn-rolled'},
 'shell': {'handled':'shell-handled','displayed':'shell-displayed'},
 'red_thread': {'loose':'red-thread-loose','rumpled':'red-thread-rumpled','nested':'red-thread-nested'},
 'glass_star': {'handled':'glass-star-handled','displayed':'glass-star-displayed'},
}

MOSS_MAP={'shadow':(31,23,18,110),'dogDark':P['dog0'],'dog':P['dog2'],'dogLight':P['dog4'],'dogCream':P['muzzle1'],'eye':P['ink']}


def moss_source_palette(asset):
 data=json.loads((REPO/'display'/'art'/'moss'/f'{asset}.json').read_text()); im=Image(data['width'],data['height'])
 for x,y,w,h,role in data['runs']: im.rect(x,y,w,h,MOSS_MAP[role])
 return im

def moss_idle_review_candidate(kind):
 # Idle-only convergence candidates. All retain the authored Canvas silhouette/anchor vocabulary.
 im=moss_source_palette('idle')
 if kind == 'a':
  # A: source-faithful geometry with only the pose-safe Godot material edge treatment.
  return pose_safe_moss_finish(im)
 if kind in ('b','c'):
  im=pose_safe_moss_finish(im)
  # B/C: clarify the existing face without adding a second frontal eye or enlarging the chest.
  im.rect(36,8,3,2,'muzzle2')
  im.set(37,10,'muzzle1')
  im.set(38,12,'muzzle2'); im.set(39,12,'ink')
  im.rect(40,15,5,2,'muzzle2'); im.rect(42,17,4,2,'muzzle1')
  im.set(46,16,'ink'); im.set(46,17,'ink')
  # Keep the authored cream chest footprint (35..39,26..32); only model its top/side plane.
  im.rect(36,27,3,3,'muzzle2'); im.rect(36,30,2,2,'muzzle1')
  # Tiny planted toe highlights stay inside existing paw silhouettes.
  im.rect(20,41,2,1,'muzzle2'); im.rect(35,41,2,1,'muzzle2')
  # Two connected shoulder/back fur accents, not a speckle layer.
  im.rect(23,23,4,1,'dog3'); im.rect(20,29,3,1,'dog4')
  if kind == 'c':
   # C: one-pixel puppy-balance polish: round crown/cheek and soften the near ear, still side/3-quarter.
   im.rect(34,7,3,1,'dog2'); im.set(33,8,'dog3')
   im.set(47,18,'muzzle1')
   im.rect(27,12,2,2,'dog1'); im.set(28,11,'dog0')
   # Lower torso overhang visually shortens the legs without moving anchors or feet.
   im.rect(22,34,3,2,'dog1'); im.rect(34,34,3,2,'dog1')
  return im
 raise ValueError(kind)
def moss(asset):
 # Production Moss rule: preserve authored geometry exactly and translate palette roles only.
 # No fixed-coordinate facial/chest/fur additions and no pose-safe recoloring are allowed here.
 # This keeps every action anatomically identical to its accepted display/art/moss/*.json source.
 return moss_source_palette(asset)

def main():
 ART.mkdir(parents=True,exist_ok=True)
 # Remove the one legacy single-thread proof filename; production now emits state-qualified objects.
 legacy_object=ART/'object_red_thread.png'
 if legacy_object.exists(): legacy_object.unlink()
 base_scene('day').save(ART/'hero_spring_day.png')
 base_scene('rain').save(ART/'hero_rain.png')
 base_scene('night').save(ART/'hero_winter_night.png')
 foreground(None).save(ART/'hero_foreground.png')
 bed_front_lip().save(ART/'bed_front_lip.png')
 for object_id, states in LIVE_OBJECT_SOURCES.items():
  for state, source_stem in states.items():
   object_asset(source_stem).save(ART/f'object_{object_id}_{state}.png')

 # Production Moss set. The rejected frontal/quasi-humanoid idle experiment is intentionally gone.
 # Every pose is the accepted authored Canvas geometry translated through the Godot palette only.
 # No production finishing pass may add geometry or recolor individual pixels beyond MOSS_MAP.
 production = {
  'idle': ('idle',),
  'walk': tuple(f'walk-{i}' for i in range(4)),
  'inspect': ('inspect-anticipate','inspect-contact','inspect-hold','inspect-recover'),
  'nudge': ('nudge-anticipate','nudge-contact','nudge-press','nudge-hold','nudge-recover'),
  'rest': ('rest',),
  'loaf': ('loaf',),
  'groom': ('groom-start','groom-contact','groom-hold','groom-recover'),
  'stretch': ('stretch-ready','stretch-extend','stretch-hold','stretch-recover'),
  'sleep': ('sleep-settle0','sleep-settle1','sleep-settle2','sleep-settle3','sleep-curled'),
  'wake': tuple(f'wake-{i}' for i in range(4)),
  # Canonical carry owns pickup. Presentation stages authored pickup poses once, then settles into carry.
  'carry': ('pickup-anticipate','pickup-contact','pickup-lift','pickup-hold','carry'),
  'place': ('place-lower','place-contact','place-hold','place-release','place-recover'),
  'look': ('react','idle'),
  'window_watch': ('window-ready','window-watch'),
 }
 for motion, assets in production.items():
  for i, asset in enumerate(assets):
   moss(asset).save(ART/f'moss_{motion}_{i}.png')
 # Keep four idle aliases so old deterministic review/capture commands continue to work.
 for i in range(1,4):
  moss('idle').save(ART/f'moss_idle_{i}.png')
 manifest={
  'schema':'terrarium.reference-godot-poc-v3',
  'art_surface':[400,240],
  'presentation':[800,480],
  'visual_baseline':'approved cleaned Reference-v3 room + exact authored Moss geometry with Godot palette mapping only',
  'moss_rendering':'authored_geometry_godot_palette_only',
  'rejected_regression':'frontal low-quadruped / chest-forward Moss experiment',
  'reference_direction':'rich hand-authored cozy late-16-bit interior; dense material pixels; selective chromatic outlines; saturated wood/blue/green accents',
  'scope':'full-room presentation candidate; no simulation authority',
  'variants':['spring_day','rain','winter_warm_night'],
  'motions':{k:list(v) for k,v in production.items()},
  'live_object_support':{object_id:list(states) for object_id,states in LIVE_OBJECT_SOURCES.items()},
  'composition':['timber room shell','textured plaster + wainscot','sunset/weather window + blue curtains','sleeping nook','desk + stool + reading props','bookcase + trailing plant','large patterned green rug','pouf + book basket','floor plant','bowls/toys','Moss hero sprite'],
 }
 review_dir=ART/'review'; review_dir.mkdir(parents=True,exist_ok=True)
 for kind in ('a','b','c'): moss_idle_review_candidate(kind).save(review_dir/f'moss_idle_candidate_{kind}.png')
 moss_source_palette('idle').save(review_dir/'moss_idle_source_palette.png')
 (ART/'hero_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 count=5+sum(len(states) for states in LIVE_OBJECT_SOURCES.values())+sum(len(v) for v in production.values())+3
 print(json.dumps({'status':'ok','assets':count,'surface':'400x240','poc':'reference-v3-production-candidate'}))
if __name__=='__main__': main()
