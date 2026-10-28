# Renders Google Play / App Store screenshots from the real game (www/index.html). Run `npm run build` first.
# Usage: python3 design/screens-store.py android|iphone|iphone-large
import pathlib, sys
from PIL import Image
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent
DEVICES = {'android': (360, 640, 'android'), 'iphone': (402, 874, 'ios'), 'iphone-large': (430, 932, 'ios')}
name = sys.argv[1] if len(sys.argv) > 1 else 'android'
w, h, store = DEVICES[name]
out = root / 'store' / store / 'screenshots'; out.mkdir(parents=True, exist_ok=True)
url = f'file://{root}/www/index.html'

def rect_up(x0, y0, x1, bottom=35):
    """Trail from the bottom border up column x0, across row y0, down column x1."""
    return [[x0, y] for y in range(bottom, y0 - 1, -1)] + [[x, y0] for x in range(x0 + 1, x1 + 1)] + [[x1, y] for y in range(y0 + 1, bottom + 1)]

with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    def page(level, monsters):
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=3)
        pg.on('pageerror', lambda e: print('JS error:', e))
        pg.goto(url); pg.wait_for_function('window.__game'); pg.wait_for_timeout(300)
        pg.add_style_tag(content='#hint{display:none!important}')
        pg.click('.btn'); pg.wait_for_timeout(200)
        pg.evaluate(f"__game.setLevel({level}); __game.freeze(true); __game.clearMonsters()")
        for x, y in monsters: pg.evaluate(f"__game.addSea({x}, {y})")
        return pg
    def save(pg, shot):
        d = out / f'{name}-{shot}.png'; pg.screenshot(path=str(d)); Image.open(d).convert('RGB').save(d)
        print('wrote', d.name); pg.close()
    T = lambda pg, cells, close: pg.evaluate('([c, k]) => __game.trail(c, k)', [cells, close])

    # 1: a level in progress, two areas claimed and a trail being drawn
    pg = page(3, [(15.5, 10.5), (8.5, 15.5), (18.5, 19.5)])
    T(pg, rect_up(2, 23, 7), True); pg.wait_for_timeout(1300)
    T(pg, [[12, y] for y in range(2, 9)] + [[x, 8] for x in range(11, 1, -1)], True); pg.wait_for_timeout(1300)
    T(pg, [[15, y] for y in range(35, 26, -1)] + [[x, 27] for x in range(16, 20)], False); pg.evaluate("__game.setLives(2)")
    pg.wait_for_timeout(900); save(pg, '1-draw')
    # 2: a huge claim rising in a wave
    pg = page(1, [(15.5, 8.5), (6.5, 6.5)])
    T(pg, [[x, 22] for x in range(2, 22)], True); pg.wait_for_timeout(380); save(pg, '2-claim')
    # 3: trapping a monster
    pg = page(4, [(18.5, 31.5), (8.5, 10.5), (14.5, 15.5)])
    T(pg, rect_up(2, 26, 6), True); pg.wait_for_timeout(1300)
    T(pg, rect_up(15, 29, 21), True); pg.wait_for_timeout(330); save(pg, '3-trap')
    # 4: level clear, the world you built
    pg = page(2, [(12.5, 5.5)])
    T(pg, rect_up(4, 20, 10), True); pg.wait_for_timeout(1200)
    T(pg, [[x, 9] for x in range(2, 22)], True); pg.wait_for_timeout(2300); save(pg, '4-world')
    b.close()
