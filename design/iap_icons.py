# Play Store product icons (512 x 512, no text) for the six in-app purchases.
import pathlib, sys, math
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from icon_art import *
from PIL import Image
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'store/iap-icons')
EXTRA = '''<defs>
<linearGradient id="sea2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4fd8ff"/><stop offset="1" stop-color="#1253c9"/></linearGradient>
<linearGradient id="space2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a1680"/><stop offset="1" stop-color="#8f4dff"/></linearGradient>
<linearGradient id="pool2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff7ad9"/><stop offset="1" stop-color="#3fd8c8"/></linearGradient>
<linearGradient id="gold2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe066"/><stop offset="1" stop-color="#ff9a1f"/></linearGradient>
<linearGradient id="teal2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2ee0c0"/><stop offset="1" stop-color="#0a6fd6"/></linearGradient>
<linearGradient id="sat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd27a"/><stop offset=".5" stop-color="#ff9a3d"/><stop offset="1" stop-color="#e86a2a"/></linearGradient>
<radialGradient id="ysub" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#fff27a"/><stop offset="1" stop-color="#f0b400"/></radialGradient>
</defs>'''
def sub():
    return ('<rect x="-12" y="-150" width="24" height="70" rx="8" fill="#2a3550"/><rect x="-12" y="-158" width="50" height="22" rx="8" fill="#2a3550"/>'
            '<rect x="-60" y="-110" width="120" height="80" rx="30" fill="url(#ysub)" stroke="#b07a00" stroke-width="6"/>'
            '<ellipse rx="190" ry="105" fill="url(#ysub)" stroke="#b07a00" stroke-width="7"/>'
            + ''.join(f'<circle cx="{x}" cy="5" r="30" fill="#9fe6ff" stroke="#2a3550" stroke-width="10"/>' for x in (-90, 0, 90)) +
            '<path d="M180,-20 L250,-70 L250,70 L180,20Z" fill="#2a3550"/><ellipse cx="-70" cy="-60" rx="50" ry="18" fill="#fff" opacity=".5"/>')
def saturn():
    return ('<ellipse rx="230" ry="62" fill="none" stroke="#b98cff" stroke-width="30" transform="rotate(-18)"/>'
            '<circle r="135" fill="url(#sat)"/><ellipse cx="-45" cy="-60" rx="45" ry="20" fill="#fff" opacity=".45"/>'
            '<path d="M-230,0 A230,62 0 0 0 230,0" fill="none" stroke="#b98cff" stroke-width="30" transform="rotate(-18)"/>'
            '<circle cx="-40" cy="-5" r="20" fill="#fff"/><circle cx="40" cy="-5" r="20" fill="#fff"/><circle cx="-35" cy="0" r="10" fill="#1b1030"/><circle cx="45" cy="0" r="10" fill="#1b1030"/>')
def donut():
    s = '<circle r="200" fill="#e0a060"/><circle r="185" fill="#ff4fae"/><circle r="72" fill="url(#pool2)"/><circle r="72" fill="none" stroke="#c97a3a" stroke-width="10"/>'
    import random; r = random.Random(4)
    for k in range(26):
        a = r.uniform(0, 6.28); d = r.uniform(95, 165)
        s += f'<rect x="-18" y="-6" width="36" height="12" rx="6" fill="{r.choice(["#fff","#7ff0ff","#ffd166","#7be36b","#9b5cff"])}" transform="translate({math.cos(a)*d:.0f},{math.sin(a)*d:.0f}) rotate({r.uniform(0,180):.0f})"/>'
    return s + '<ellipse cx="-80" cy="-110" rx="50" ry="20" fill="#fff" opacity=".4" transform="rotate(-35 -80 -110)"/>'
def stars(n=22, seed=2):
    import random; r = random.Random(seed)
    return ''.join(f'<circle cx="{r.uniform(20,1004):.0f}" cy="{r.uniform(20,1004):.0f}" r="{r.uniform(3,8):.0f}" fill="#fff" opacity="{r.uniform(.4,.9):.2f}"/>' for _ in range(n))
def noads():
    return ('<rect x="-230" y="-160" width="460" height="320" rx="50" fill="#fff" stroke="#0b3f8f" stroke-width="14"/>'
            '<path d="M-50,-80 L90,0 L-50,80Z" fill="#0a6fd6"/>'
            '<circle r="270" fill="none" stroke="#ff3048" stroke-width="56"/><path d="M-190,-190 L190,190" stroke="#ff3048" stroke-width="56" stroke-linecap="round"/>')
def crown():
    return ('<path d="M-260,140 L-300,-160 L-120,-20 L0,-230 L120,-20 L300,-160 L260,140Z" fill="url(#gold)" stroke="#b07400" stroke-width="16" stroke-linejoin="round"/>'
            '<rect x="-270" y="140" width="540" height="80" rx="20" fill="url(#gold)" stroke="#b07400" stroke-width="16"/>'
            '<circle cx="0" cy="40" r="44" fill="#ff3f8e"/><circle cx="-160" cy="80" r="30" fill="#3fd0ff"/><circle cx="160" cy="80" r="30" fill="#7be36b"/>')
bg = lambda g: f'<rect width="1024" height="1024" fill="url(#{g})"/>'
I = {
  'pack-sea': bg('sea2') + rays(512, 512, 18, .09) + waves() + G(512, 540, 1.45, -8, sub()),
  'pack-space': bg('space2') + stars() + G(512, 512, 1.55, 0, saturn()),
  'pack-pool': bg('pool2') + rays(512, 512, 18, .1) + G(512, 512, 1.6, 0, donut()),
  'all-skins': bg('gold2') + rays(512, 512, 22, .14) + G(300, 330, .75, -10, sub()) + G(730, 360, .72, 0, saturn()) + G(512, 720, .78, 0, donut()),
  'remove-ads': bg('teal2') + rays(512, 512, 18, .08) + G(512, 512, 1.15, 0, noads()),
  'everything': bg('space2') + rays(512, 560, 22, .12) + stars(30, 7) + G(512, 540, 1.05, 0, crown()),
}
tmp = pathlib.Path(__file__).parent / 'out'
import icon_art
icon_art.DEFS = icon_art.DEFS + EXTRA
render(I, tmp)
out.mkdir(parents=True, exist_ok=True)
for k in I: Image.open(tmp / f'{k}.png').convert('RGBA').resize((512, 512), Image.LANCZOS).save(out / f'{k}.png')
print('done', out)
