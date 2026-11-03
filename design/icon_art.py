# Illustrated app icon concepts (vector), rendered to PNG. Usage: python3 icon-art.py OUTDIR
import math, sys, pathlib
from playwright.sync_api import sync_playwright
W = 1024
DEFS = '''<defs>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3fd0ff"/><stop offset="1" stop-color="#1366d6"/></linearGradient>
<linearGradient id="deep" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b2f8f"/><stop offset="1" stop-color="#0e7fc9"/></linearGradient>
<linearGradient id="grass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9be86a"/><stop offset="1" stop-color="#3fae3a"/></linearGradient>
<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffcf4a"/><stop offset="1" stop-color="#ff6a3d"/></linearGradient>
<linearGradient id="teal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16d9c0"/><stop offset="1" stop-color="#0a6fd6"/></linearGradient>
<linearGradient id="hull" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff5a5a"/><stop offset="1" stop-color="#d91c3c"/></linearGradient>
<radialGradient id="puff" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#ffd27a"/><stop offset=".6" stop-color="#ff9a2e"/><stop offset="1" stop-color="#e8641a"/></radialGradient>
<radialGradient id="jel" cx=".4" cy=".3" r=".8"><stop offset="0" stop-color="#ffc2f2"/><stop offset="1" stop-color="#b04ddb"/></radialGradient>
<radialGradient id="oct" cx=".4" cy=".3" r=".8"><stop offset="0" stop-color="#c79bff"/><stop offset="1" stop-color="#6a2fd1"/></radialGradient>
<radialGradient id="star" cx=".45" cy=".4" r=".7"><stop offset="0" stop-color="#fff07a"/><stop offset="1" stop-color="#ffb21e"/></radialGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff38a"/><stop offset="1" stop-color="#f0a500"/></linearGradient>
<filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#002" flood-opacity=".35"/></filter>
</defs>'''
def G(x, y, s=1, r=0, body='', f=True):
    return f'<g transform="translate({x},{y}) rotate({r}) scale({s})"{" filter=\'url(#sh)\'" if f else ""}>{body}</g>'
def eyes(dx, y, r, lx=0, ly=0, mood=''):
    s = ''
    for sx in (-1, 1):
        s += f'<circle cx="{sx*dx}" cy="{y}" r="{r}" fill="#fff" stroke="#3a1a10" stroke-width="{r*.18}"/>'
        s += f'<circle cx="{sx*dx+lx*r*.35}" cy="{y+ly*r*.35}" r="{r*.5}" fill="#1b1030"/><circle cx="{sx*dx+lx*r*.35-r*.18}" cy="{y+ly*r*.35-r*.2}" r="{r*.17}" fill="#fff"/>'
        if mood == 'angry':
            s += f'<path d="M{sx*(dx+r*1.1)},{y-r*1.5} L{sx*(dx-r*.9)},{y-r*.95}" stroke="#3a1a10" stroke-width="{r*.35}" stroke-linecap="round"/>'
    return s
def boat():
    return ('<path d="M0,-58 C24,-32 28,-6 28,22 L28,40 Q28,52 16,52 L-16,52 Q-28,52 -28,40 L-28,22 C-28,-6 -24,-32 0,-58Z" fill="url(#hull)" stroke="#9e1230" stroke-width="3"/>'
            '<path d="M0,-40 C15,-22 18,-4 18,18 L18,36 Q18,42 12,42 L-12,42 Q-18,42 -18,36 L-18,18 C-18,-4 -15,-22 0,-40Z" fill="#fff"/>'
            '<rect x="-14" y="2" width="28" height="26" rx="6" fill="#ffd34a" stroke="#c98f00" stroke-width="2"/>'
            '<rect x="-12" y="-8" width="24" height="10" rx="4" fill="#7fd6ff" stroke="#2a7fb8" stroke-width="2"/>'
            '<circle cx="0" cy="15" r="6" fill="#1b2a44"/>')
def wake():
    return '<path d="M-20,50 Q-30,72 -44,90 M20,50 Q30,72 44,90" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round" opacity=".6"/>'
def puffer(crown=False, look=(0, 0), mood=''):
    sp = ''
    for i in range(16):
        a = i / 16 * 2 * math.pi; b = .13
        p = [(math.cos(a-b)*48, math.sin(a-b)*48), (math.cos(a)*68, math.sin(a)*68), (math.cos(a+b)*48, math.sin(a+b)*48)]
        sp += '<polygon points="%s" fill="#fff4d6" stroke="#c46a1a" stroke-width="2.5" stroke-linejoin="round"/>' % ' '.join(f'{x:.1f},{y:.1f}' for x, y in p)
    s = sp + '<circle r="52" fill="url(#puff)" stroke="#c4561a" stroke-width="3"/><ellipse cx="0" cy="24" rx="30" ry="18" fill="#ffe9b8" opacity=".8"/>'
    s += eyes(19, -8, 14, *look, mood) + '<ellipse cx="0" cy="22" rx="8" ry="6" fill="#7a2410"/>'
    s += '<ellipse cx="-22" cy="-30" rx="12" ry="7" fill="#fff" opacity=".45" transform="rotate(-30 -22 -30)"/>'
    if crown:
        s += '<path d="M-34,-50 L-38,-88 L-18,-66 L0,-96 L18,-66 L38,-88 L34,-50Z" fill="url(#gold)" stroke="#b07400" stroke-width="3" stroke-linejoin="round"/><circle cx="0" cy="-60" r="6" fill="#e83a6a"/>'
    return s
def jelly(look=(0, 0)):
    t = ''.join(f'<path d="M{x},10 q{-10 if i%2 else 10},18 0,34 t0,34" stroke="#d77ef0" stroke-width="7" fill="none" stroke-linecap="round"/>' for i, x in enumerate((-30, -10, 10, 30)))
    return t + ('<path d="M-48,12 C-48,-52 48,-52 48,12 Q36,22 24,12 Q12,22 0,12 Q-12,22 -24,12 Q-36,22 -48,12Z" fill="url(#jel)" stroke="#8a2fb0" stroke-width="3"/>'
                '<ellipse cx="-18" cy="-24" rx="12" ry="7" fill="#fff" opacity=".5" transform="rotate(-25 -18 -24)"/>') + eyes(16, -4, 11, *look) + '<path d="M-6,8 q6,6 12,0" stroke="#5a1070" stroke-width="3" fill="none"/>'
def starfish(look=(0, 0)):
    pts = ' '.join(f'{math.cos(-math.pi/2+i*math.pi/5)*(56 if i%2==0 else 24):.1f},{math.sin(-math.pi/2+i*math.pi/5)*(56 if i%2==0 else 24):.1f}' for i in range(10))
    return f'<polygon points="{pts}" fill="url(#star)" stroke="#ffb21e" stroke-width="18" stroke-linejoin="round"/><polygon points="{pts}" fill="none" stroke="#d27a00" stroke-width="3" stroke-linejoin="round" transform="scale(1.12)"/>' + eyes(11, -2, 9, *look) + '<path d="M-6,12 q6,5 12,0" stroke="#7a3a00" stroke-width="3" fill="none"/>'
def octo(look=(0, 0)):
    t = ''.join(f'<path d="M{x},20 q{d*14},26 {d*30},30 q{d*12},2 {d*10},-10" stroke="#7a3ae0" stroke-width="13" fill="none" stroke-linecap="round"/>' for x, d in ((-30, -1), (-12, -1), (12, 1), (30, 1)))
    return t + '<ellipse cx="0" cy="-8" rx="46" ry="48" fill="url(#oct)" stroke="#4a1aa0" stroke-width="3"/><ellipse cx="-16" cy="-34" rx="12" ry="7" fill="#fff" opacity=".45" transform="rotate(-30 -16 -34)"/>' + eyes(17, 0, 12, *look) + '<ellipse cx="0" cy="22" rx="7" ry="5" fill="#2a0a60"/>'
def trail(d, w=12):
    return f'<path d="{d}" stroke="#fff" stroke-width="{w}" stroke-dasharray="{w*2} {w*1.4}" stroke-linecap="round" fill="none"/>'
def rays(cx, cy, n=18, op=.12):
    s = ''
    for i in range(n):
        a = i / n * 2 * math.pi; b = math.pi / n / 1.6
        s += f'<polygon points="{cx},{cy} {cx+math.cos(a-b)*1500},{cy+math.sin(a-b)*1500} {cx+math.cos(a+b)*1500},{cy+math.sin(a+b)*1500}" fill="#fff" opacity="{op}"/>'
    return s
def waves(col='#fff', op=.18):
    return ''.join(f'<path d="M{x},{y} q20,-12 40,0 t40,0" stroke="{col}" stroke-width="7" fill="none" opacity="{op}" stroke-linecap="round"/>' for x, y in ((90,180),(700,140),(160,820),(760,700),(420,940),(860,420),(60,520)))
def flowers(x0, y0, x1, y1, n=14, seed=3):
    import random; r = random.Random(seed); s = ''
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        s += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(5,9):.0f}" fill="{r.choice(["#fff","#fff27a","#ffb3d9"])}" opacity=".9"/>'
    return s
def land(d):
    return f'<path d="{d}" fill="#7a4a24" transform="translate(0,22)"/><path d="{d}" fill="url(#grass)" stroke="#2f8a2c" stroke-width="4"/>'

I = {}
# 1 Hero chase: sunburst, crowned king, jelly, starfish, boat racing with a curved line
I['01-chase'] = ('<rect width="1024" height="1024" fill="url(#water)"/>' + rays(700, 300) + waves() +
    trail('M260,1060 C240,900 300,820 400,760') +
    G(720, 330, 3.0, 0, puffer(True, (-.8, .6), 'angry')) + G(200, 300, 1.6, -10, jelly((.8, .5))) + G(830, 800, 1.2, 15, starfish((-.8, -.3))) +
    G(430, 720, 2.6, 40, wake() + boat()))
# 2 Split: grass claims the top-left, the boat rides the edge
I['02-split'] = ('<rect width="1024" height="1024" fill="url(#water)"/>' + waves() +
    land('M-20,-20 L1044,-20 L1044,300 L-20,760Z') + flowers(40, 40, 900, 300) + trail('M-20,760 L470,535', 14) +
    G(860, 760, 2.4, 0, puffer(False, (-.7, -.6), 'angry')) + G(350, 870, 1.1, 0, starfish((.6, -.6))) +
    G(560, 495, 2.6, 66, wake() + boat()))
# 3 Close call: huge angry king, boat in the foreground
I['03-face'] = ('<rect width="1024" height="1024" fill="url(#deep)"/>' + rays(512, 380, 20, .08) +
    G(512, 420, 6.2, 0, puffer(True, (0, 1), 'angry')) + trail('M-20,940 C200,900 300,900 420,870') +
    G(560, 860, 2.4, 80, wake() + boat()))
# 4 Trapped: a dashed loop almost closed around a scared puffer
I['04-trap'] = ('<rect width="1024" height="1024" fill="url(#grass)"/>' + flowers(20, 20, 1000, 1000, 30, 5) +
    '<rect x="110" y="110" width="804" height="804" rx="60" fill="url(#water)" stroke="#7a4a24" stroke-width="14"/>' + waves() +
    trail('M170,230 L170,820 L850,820 L850,260 L560,260', 16) +
    G(500, 560, 3.0, 0, puffer(False, (-.6, -.5))) + G(470, 262, 2.4, -90, wake() + boat()))
# 5 Monster party: boat in the middle, four monsters of all sizes
I['05-party'] = ('<rect width="1024" height="1024" fill="url(#deep)"/>' + rays(512, 512, 22, .07) + waves() +
    G(250, 270, 2.5, -8, puffer(True, (.7, .7), 'angry')) + G(800, 260, 1.5, 10, jelly((-.8, .7))) +
    G(220, 790, 1.4, 0, octo((.8, -.6))) + G(820, 800, 1.0, 20, starfish((-.8, -.8))) +
    G(540, 560, 2.6, 25, wake() + boat()))
# 6 Island: round island, a line slicing across the sea
I['06-island'] = ('<rect width="1024" height="1024" fill="url(#water)"/>' + waves() +
    land('M300,260 C460,140 760,180 800,380 C840,560 700,640 520,620 C340,600 200,420 300,260Z') + flowers(360, 260, 720, 520, 10) +
    G(520, 400, 1.6, 0, puffer(False, (0, .8))) + trail('M-20,780 L620,780', 14) +
    G(700, 780, 2.4, 90, wake() + boat()) + G(240, 900, 1.2, 0, jelly((.6, -.6))))
# 7 Octopus: giant octopus from the top, boat escaping
I['07-octo'] = ('<rect width="1024" height="1024" fill="url(#water)"/>' + rays(512, 0, 16, .1) + waves() +
    G(512, 250, 5.0, 0, octo((.3, 1))) + trail('M1044,980 C860,920 720,880 600,800') +
    G(560, 770, 2.6, -55, wake() + boat()) + G(140, 820, 1.1, 0, starfish((.8, -.4))))
# 8 Sunset: warm sky, sea, boat and the king on the horizon
I['08-sunset'] = ('<rect width="1024" height="1024" fill="url(#sun)"/>' + '<circle cx="512" cy="470" r="230" fill="#fff6c2" opacity=".85"/>' +
    G(512, 470, 2.9, 0, puffer(True, (0, .8)), False) +
    '<rect y="560" width="1024" height="464" fill="url(#water)"/>' + waves('#fff', .25) + trail('M80,1000 C220,900 300,860 420,830') +
    G(470, 800, 2.6, 60, wake() + boat()))
# 9 L for Landscraper: land drawn as an L by the line
I['09-letter'] = ('<rect width="1024" height="1024" fill="url(#teal)"/>' + waves() +
    land('M220,140 L440,140 L440,640 L820,640 L820,860 L220,860Z') + flowers(240, 160, 420, 840, 10) + flowers(460, 660, 800, 840, 6, 9) +
    trail('M820,640 L820,330', 14) + G(820, 300, 2.3, 0, wake() + boat()) +
    G(690, 330, 1.4, 0, puffer(False, (.8, 0), 'angry')))
# 10 Clean: one big boat, one swoosh, one monster
I['10-clean'] = ('<rect width="1024" height="1024" fill="url(#teal)"/><circle cx="512" cy="512" r="420" fill="url(#glow)"/>' +
    trail('M-20,880 C260,980 420,700 500,560', 18) + G(560, 470, 4.0, 35, boat()) + G(820, 230, 1.6, 0, puffer(False, (-.8, .7), 'angry')))

I = {}
# 1 final: the boat has just left the land it claimed, the king and friends wait
I['01a-chase-land'] = ('<rect width="1024" height="1024" fill="url(#water)"/>' + rays(720, 380) + waves() +
    land('M-20,640 L250,640 Q300,640 300,690 L300,1044 L-20,1044Z') + flowers(10, 660, 280, 1010, 10) +
    trail('M300,930 C350,900 372,850 373,760', 18) +
    G(752, 385, 3.35, 0, puffer(True, (-.9, .5), 'angry')) + G(170, 250, 2.1, -10, jelly((.8, .5))) + G(860, 850, 1.7, 15, starfish((-.8, -.5))) +
    G(430, 600, 3.2, 20, boat()))
I['01b-chase-land'] = ('<rect width="1024" height="1024" fill="url(#water)"/>' + rays(740, 400) + waves() +
    land('M-20,740 L1044,740 L1044,1044 L-20,1044Z') + flowers(10, 760, 1010, 1010, 14) +
    trail('M300,740 C320,715 335,700 343,676', 18) +
    G(745, 400, 3.4, 0, puffer(True, (-.9, .5), 'angry')) + G(170, 250, 2.1, -10, jelly((.8, .5))) + G(880, 640, 1.5, 15, starfish((-.8, -.5))) +
    G(400, 520, 3.2, 20, boat()))
def render(items, out, w=W, h=W, vb=None):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': w, 'height': h})
        for k, body in items.items():
            pg.set_content(f'<body style="margin:0;background:#000"><svg width="{w}" height="{h}" viewBox="{vb or f'0 0 {w} {h}'}" xmlns="http://www.w3.org/2000/svg">{DEFS}{body}</svg></body>')
            pg.screenshot(path=str(out / f'{k}.png'))
        b.close()

if __name__ == '__main__':
    render(I, sys.argv[1] if len(sys.argv) > 1 else 'design/icon-art')
