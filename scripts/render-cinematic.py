#!/usr/bin/env python3
"""Cinematic video wallpapers for all four car views. Requires numpy, Pillow and FFmpeg.

Uses the clear photograph as a locked plate (no mismatched-image morphing),
advected fractal density, layered extinction/scattering, and isolated lamps.
"""
from pathlib import Path
import argparse
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
W, H = 1672, 942
FPS = 30

SCENES = {
    1: dict(car=[(207,745),(213,539),(290,421),(583,350),
        (710,282),(870,229),(1130,221),(1267,253),(1360,331),
        (1455,359),(1517,464),(1515,657),(1380,717),(1150,811),
        (781,839),(420,810)], lamps=[(823,477,91,29),(277,470,27,44)],
        centre=225, fog_height=150, beam="left"),
    2: dict(car=[(523,767),(523,545),(543,491),(529,467),(550,448),
        (585,452),(613,425),(657,390),(730,378),(929,380),(992,398),
        (1056,461),(1083,453),(1112,459),(1127,478),(1111,506),
        (1137,577),(1131,772),(1011,792),(620,793)],
        lamps=[(609,573,66,37),(1034,574,65,36)],
        centre=207, fog_height=166, beam="forward"),
    3: dict(car=[(278,677),(272,535),(298,451),(348,423),(432,388),
        (551,346),(751,332),(897,350),(1002,405),(1060,447),
        (1070,427),(1105,425),(1122,452),(1118,473),(1165,505),
        (1190,569),(1174,695),(1034,741),(821,756),(430,743)],
        lamps=[(318,487,35,22),(724,490,83,30)],
        centre=182, fog_height=155, beam="rear",
        strips=[[(301,472),(321,468),(346,468)],
                [(287,506),(329,506)],
                [(652,469),(703,473),(750,482),(776,489),(769,499),
                 (741,507),(680,509),(644,507)]]),
    4: dict(car=[(121,773),(125,509),(160,436),(254,353),(439,304),
        (650,267),(786,207),(962,144),(1162,118),(1378,119),
        (1534,162),(1605,259),(1672,290),(1672,674),(1463,772),
        (1241,860),(885,857),(431,828)],
        lamps=[(880,422,141,41),(230,409,49,62)],
        centre=240, fog_height=158, beam="left"),
}

def smooth(a, b, t):
    u = np.clip((t-a)/(b-a), 0, 1)
    return u*u*(3-2*u)


def field(rng, size):
    # Continuous periodic fractal noise; large eddies carry smaller detail.
    out = np.zeros((236, 418), np.float32)
    for cells, weight in [(5, .30), (10, .28), (20, .22), (40, .14), (80, .06)]:
        tile = rng.random((cells, cells), dtype=np.float32)
        tile = np.tile(tile, (3, 3))
        im = Image.fromarray(tile).resize((1254, 708), Image.Resampling.BICUBIC)
        out += np.asarray(im)[236:472, 418:836]*weight
    return out


def sample(a, x, y):
    x, y = x % a.shape[1], y % a.shape[0]
    ix, iy = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x-ix, y-iy
    ix, iy = ix % a.shape[1], iy % a.shape[0]
    return ((a[iy, ix]*(1-fx)+a[iy,(ix+1)%a.shape[1]]*fx)*(1-fy)
            +(a[(iy+1)%a.shape[0],ix]*(1-fx)+a[(iy+1)%a.shape[0],(ix+1)%a.shape[1]]*fx)*fy)


def up(a):
    return np.asarray(Image.fromarray(a.astype(np.float32)).resize((W,H), Image.Resampling.BILINEAR))


class Scene:
    def __init__(self, number=1):
        config = SCENES[number]
        self.number = number
        self.config = config
        self.rear = config['beam'] == 'rear'
        self.tint = np.array([1., .018, .006] if self.rear else [.76,.86,1.0])
        im = Image.open(ROOT/f'backgrounds/carbon-black-wallpapers-{number}.png').convert('RGB')
        self.plate = np.pad(np.asarray(im, dtype=np.float32)/255, ((0,1),(0,0),(0,0)))
        # Work in linear light so light scattering and extinction are additive.
        self.plate = self.plate**2.2
        mask = Image.new('L',(W,H))
        ImageDraw.Draw(mask).polygon(config['car'],fill=255)
        self.car = np.asarray(mask.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.GaussianBlur(12)),dtype=np.float32)/255
        yy,xx=np.mgrid[:H,:W].astype(np.float32)
        self.lamps=np.zeros((H,W),np.float32)
        self.halo=np.zeros((H,W),np.float32)
        self.beams=np.zeros((H,W),np.float32)
        for cx,cy,sx,sy in config['lamps']:
            self.lamps=np.maximum(self.lamps,np.exp(-2*((xx-cx)/sx)**2-2*((yy-cy)/sy)**2))
            self.halo+=np.exp(-((xx-cx)/115)**2-((yy-cy)/68)**2)
            if config['beam'] == 'left':
                dx=cx-xx
                axis=cy+dx*.19
                width=12+np.maximum(dx,0)*.15
                self.beams+=np.exp(-((yy-axis)/width)**2)*np.exp(-np.maximum(dx,0)/430)*(dx>0)
            elif config['beam'] == 'forward':
                distance=np.maximum(yy-cy,0)
                width=25+distance*.38
                self.beams+=np.exp(-((xx-cx)/width)**2)*np.exp(-distance/230)*(yy>cy)
        if self.rear:
            # Tail lamps are diffuse red emitters, without forward-projecting beams.
            strips=Image.new('L',(W,H))
            draw=ImageDraw.Draw(strips)
            for points in config['strips']:
                draw.line(points,fill=255,width=5,joint='curve')
            self.lamps=np.asarray(strips.filter(ImageFilter.GaussianBlur(1.2)),dtype=np.float32)/255
        self.low_y,self.low_x=np.mgrid[:236,:418].astype(np.float32)
        self.layers=[field(np.random.default_rng(n),236) for n in [41,92,123]]
        self.height=np.exp(-((self.low_y-config['fog_height'])/75)**2)

    def frame(self,t):
        # Loop returns through a separate slow fog-in, not reverse playback.
        clear=float(smooth(7,18,t)*(1-smooth(24,30,t)))
        # LED lamps switch within one video frame. Extinguish only once the
        # returning fog has hidden the body; 30..32 plus 0..3 gives a five
        # second dark pause across the seamless loop boundary.
        lights=float(3 <= t < 30)
        # Motion is periodic over 32s; smoke never snaps at the loop seam.
        phase=2*np.pi*t/32
        density=np.zeros_like(self.low_x)
        for i,a in enumerate(self.layers):
            radius=[24,39,61][i]
            warp=sample(self.layers[(i+1)%3],self.low_x+11*np.sin(phase),self.low_y+7*np.cos(phase))
            nx=self.low_x+radius*np.sin(phase+i)+21*(warp-.5)
            ny=self.low_y+radius*.45*np.cos(phase+i)+15*(warp-.5)
            n=sample(a,nx,ny)
            density+=np.maximum(n-.35,0)**2*[30.0,20.0,14.0][i]
        # Clear from the centre outwards while wisps escape to the edges.
        escape=np.abs(self.low_x-self.config['centre'])/225
        clearing=smooth(0,1,np.clip(clear*1.5-escape*.38,0,1))
        density*=self.height*(1-clearing)*1.8
        fog=up(density)
        trans=np.exp(-fog)
        # Car body stays almost invisible until the fog starts clearing.
        body=.00005+.99995*clear
        exposure=1-self.car*(1-body)
        exposure=np.maximum(exposure,self.lamps*lights)
        base=self.plate*exposure[:,:,None]
        # Existing luminous beams in the photograph stay dark until ignition.
        base*= (1-(1-lights)*np.clip(self.beams*.75,0,.8))[:,:,None]
        light=(.003+lights*(self.beams*.032+self.halo*.05))
        scatter=(1-trans)*light
        if self.rear:
            # Ambient fog stays neutral when the tail lamps are off. Only
            # the light scattered from the lamps carries their red colour.
            scattered=(1-trans)[:,:,None]*(.003*np.array([.76,.86,1.0])+
                lights*(self.halo*.05)[:,:,None]*self.tint)
        else:
            scattered=scatter[:,:,None]*self.tint
        rgb=base*trans[:,:,None]+scattered
        rgb+=self.plate*self.lamps[:,:,None]*lights*(1-trans[:,:,None])*.85
        if self.rear:
            rgb+=lights*self.lamps[:,:,None]*self.tint*.22
            rgb+=lights*self.halo[:,:,None]*self.tint*.004*(1-clear)
        else:
            rgb+=lights*self.halo[:,:,None]*np.array([.001,.0014,.002])*(1-clear)
        return (np.clip(rgb,0,1)**(1/2.2)*255).astype(np.uint8)


def encode(destination, duration):
    return subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-t',str(duration),'-an','-c:v','libx264','-preset','slow','-crf','16',
        '-threads','4','-pix_fmt','yuv420p','-movflags','+faststart',str(destination)],stdin=subprocess.PIPE)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stills',action='store_true')
    parser.add_argument('--number',type=int,choices=range(1,5),action='append',
                        help='Scene to render; repeat for multiple scenes (default: all).')
    args=parser.parse_args()
    for number in args.number or range(1,5):
        scene=Scene(number)
        if args.stills:
            for t in [1,5,10,15,21]:
                Image.fromarray(scene.frame(t)).save(f'/tmp/cinematic-{number}-{t}.jpg')
            continue
        dest=ROOT/f'backgrounds/carbon-black-cinematic-{number}.mp4'
        temp=dest.with_suffix('.partial.mp4')
        proc=encode(temp,32)
        try:
            for frame in range(32*FPS):
                proc.stdin.write(scene.frame(frame/FPS).tobytes())
                if frame%(FPS*4)==0:
                    print(f'Scene {number}: rendered {frame/FPS:.0f}/32 seconds',flush=True)
        finally:
            proc.stdin.close()
        if proc.wait(): raise SystemExit('FFmpeg failed')
        temp.replace(dest)
        print(dest,flush=True)
