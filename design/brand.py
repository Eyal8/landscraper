# Final app icon, Android launcher icons, splash and Play feature graphic from the chosen concept (icon_art.py, 01a).
# Usage: python3 design/brand.py
import pathlib, shutil, sys
from PIL import Image, ImageDraw
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from icon_art import *
root = pathlib.Path(__file__).resolve().parent.parent
tmp = root / 'design' / 'out'; tmp.mkdir(exist_ok=True)

def scene(ext=0):
    e = ext
    return ('<rect x="-2000" y="-2000" width="5000" height="5000" fill="url(#water)"/>' + rays(720, 380) + waves() +
        land(f'M{-20-e},640 L250,640 Q300,640 300,690 L300,{1044+e} L{-20-e},{1044+e}Z') + flowers(10, 660, 280, 1010, 10) +
        trail('M300,930 C350,900 372,850 373,760', 18) +
        G(752, 385, 3.35, 0, puffer(True, (-.9, .5), 'angry')) + G(170, 250, 2.1, -10, jelly((.8, .5))) + G(860, 850, 1.7, 15, starfish((-.8, -.5))) +
        G(430, 600, 3.2, 20, boat()))
render({'icon': scene()}, tmp)
icon = Image.open(tmp / 'icon.png').convert('RGB')
icon.save(root / 'assets/icon-only.png'); icon.save(root / 'ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png')
icon.save(root / 'design/icon.png')
icon.resize((512, 512), Image.LANCZOS).save(root / 'store/android/play-icon-512.png')
icon.save(root / 'assets/icon-background.png')
Image.new('RGBA', (1024, 1024), (0, 0, 0, 0)).save(root / 'assets/icon-foreground.png')

# Android launcher icons. The adaptive icon insets both layers by 16.7%, so the full art fills the visible area.
res = root / 'android/app/src/main/res'
for d, px in {'ldpi': 36, 'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}.items():
    big = int(px * 1.5)
    icon.resize((big, big), Image.LANCZOS).save(res / f'mipmap-{d}/ic_launcher_background.png')
    Image.new('RGBA', (big, big), (0, 0, 0, 0)).save(res / f'mipmap-{d}/ic_launcher_foreground.png')
    for name, shape in (('ic_launcher', 'sq'), ('ic_launcher_round', 'ci')):
        s4 = px * 4; m = Image.new('L', (s4, s4), 0); dr = ImageDraw.Draw(m)
        dr.rounded_rectangle((0, 0, s4 - 1, s4 - 1), s4 * .18, fill=255) if shape == 'sq' else dr.ellipse((0, 0, s4 - 1, s4 - 1), fill=255)
        im = icon.resize((s4, s4), Image.LANCZOS).convert('RGBA'); im.putalpha(m)
        im.resize((px, px), Image.LANCZOS).save(res / f'mipmap-{d}/{name}.png')

# Splash: sea with the rays, the icon art in the middle, the name under it
TITLE = ('<text x="{x}" y="{y}" text-anchor="{a}" font-family="Poppins" font-weight="700" font-size="{fs}" fill="#fff" stroke="#0b3f8f" stroke-width="{sw}" paint-order="stroke" filter="url(#sh)">Landscraper</text>'
         '<text x="{x}" y="{y2}" text-anchor="{a}" font-family="Poppins" font-weight="700" font-size="{fs2}" letter-spacing="{ls}" fill="#ffd34a" stroke="#0b3f8f" stroke-width="{sw2}" paint-order="stroke">DRAW &amp; CONQUER</text>')
FONT = '<style>@font-face{font-family:Poppins;src:url(file:///usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf)}</style>'
sp = (FONT + '<rect width="2732" height="2732" fill="url(#water)"/>' + rays(1366, 1200, 24, .1) +
      '<clipPath id="rr"><rect x="966" y="760" width="800" height="800" rx="180"/></clipPath>' +
      f'<g filter="url(#sh)"><g clip-path="url(#rr)"><g transform="translate(966,760) scale(.78125)">{scene()}</g></g></g>' +
      TITLE.format(x=1366, y=1800, a='middle', fs=170, sw=18, y2=1900, fs2=62, ls=14, sw2=10))
render({'splash': sp}, tmp, 2732, 2732)
splash = Image.open(tmp / 'splash.png').convert('RGB'); splash.save(root / 'assets/splash.png')
for f in (root / 'ios/App/App/Assets.xcassets/Splash.imageset').glob('*.png'):
    splash.save(f)
for f in res.glob('drawable*/splash.png'):
    w, h = Image.open(f).size; S = max(w, h) * 1.0
    k = max(w, h) / 2732 * (1.6 if min(w, h) < 2732 else 1)
    im = splash.resize((int(2732 * max(w, h) / min(2732, max(w, h)) * 1), ) * 2, Image.LANCZOS) if False else splash
    side = max(w, h); im = splash.resize((side, side), Image.LANCZOS)
    im.crop(((side - w) // 2, (side - h) // 2, (side - w) // 2 + w, (side - h) // 2 + h)).save(f)

# Play feature graphic 1024 x 500
fg = (FONT + '<rect width="1024" height="500" fill="url(#water)"/>' + rays(820, 230, 20, .1) + waves() +
      land('M-20,360 L90,360 Q125,360 125,395 L125,520 L-20,520Z') +
      trail('M125,470 C150,450 168,420 170,380', 12) +
      G(950, 270, 2.25, 0, puffer(True, (-.9, .3), 'angry')) + G(720, 425, .85, 15, starfish((-.6, -.6))) + G(70, 105, 1.0, -10, jelly((.8, .5))) +
      G(205, 285, 1.75, 22, boat()) +
      TITLE.format(x=290, y=250, a='start', fs=82, sw=11, y2=305, fs2=30, ls=7, sw2=6))
render({'feature': fg}, tmp, 1024, 500)
Image.open(tmp / 'feature.png').convert('RGB').save(root / 'store/android/feature-graphic.png')
print('done')
