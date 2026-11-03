# Store screenshots with the brand look: caption on top, the real game screenshot in a frame, a monster in the corner.
# Run design/screens-store.py android and iphone-large first. Usage: python3 design/store-frames.py
import base64, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from icon_art import *
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
FONT = '<style>@font-face{font-family:Poppins;src:url(file:///usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf)}</style>'
SHOTS = [('1-draw', 'Draw lines.', 'Claim the land.', lambda W, H: G(W*.86, H*.955, W/650, 0, puffer(True, (-.8, .6), 'angry'))),
         ('2-boss', 'Beat 5', 'giant bosses', lambda W, H: G(W*.15, H*.95, W/650, -10, jelly((.8, .5)))),
         ('3-claim', 'Trap every', 'monster', lambda W, H: G(W*.86, H*.95, W/650, 0, octo((-.8, .6)))),
         ('4-home', '100 levels.', 'Daily + Rush.', lambda W, H: G(W*.14, H*.955, W/700, -20, starfish((.8, .5)))),
         ('5-skins', 'Collect', 'fun skins', lambda W, H: G(W*.86, H*.95, W/700, 30, boat())),
         ('6-trophies', 'Win monthly', 'trophies', lambda W, H: G(W*.14, H*.955, W/650, 0, puffer(False, (.8, .6))))]
SETS = [('android', 'store/android/screenshots', 1080, 1920), ('iphone-large', 'store/ios/screenshots', 1290, 2796)]
for name, folder, W, H in SETS:
    d = root / folder; items = {}
    for key, l1, l2, deco in SHOTS:
        src = d / f'{name}-{key}.png'
        uri = 'data:image/png;base64,' + base64.b64encode(src.read_bytes()).decode()
        fs = W * .1; sw = W * .78; sh = sw * H / W; x = (W - sw) / 2; y = H * .02 + fs * 2.75; r = W * .07; bw = W * .014
        items[f'{name}-store-{key}'] = (FONT + f'<rect width="{W}" height="{H}" fill="url(#water)"/>' + rays(W/2, H*.12, 22, .1) +
            f'<rect x="{x-bw}" y="{y-bw}" width="{sw+2*bw}" height="{sh+2*bw}" rx="{r+bw}" fill="#fff" filter="url(#sh)"/>'
            f'<clipPath id="c"><rect x="{x}" y="{y}" width="{sw}" height="{sh}" rx="{r}"/></clipPath>'
            f'<image href="{uri}" x="{x}" y="{y}" width="{sw}" height="{sh}" clip-path="url(#c)" preserveAspectRatio="xMidYMid slice"/>' +
            deco(W, H) +
            f'<text x="{W/2}" y="{H*.02+fs}" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="{fs}" fill="#fff" stroke="#0b3f8f" stroke-width="{fs*.12}" paint-order="stroke">{l1}</text>'
            f'<text x="{W/2}" y="{H*.02+fs*2.15}" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="{fs}" fill="#ffd34a" stroke="#0b3f8f" stroke-width="{fs*.12}" paint-order="stroke">{l2}</text>')
    out = root / folder / 'final'
    render(items, out, W, H)
    for f in out.glob('*.png'): Image.open(f).convert('RGB').save(f)
    print('wrote', out)
