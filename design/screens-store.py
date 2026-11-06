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
for old in out.glob(f'{name}-*.png'): old.unlink()
url = f'file://{root}/www/index.html'
SEEN = "['rush','bouncer','eater','saw','zipper','splitter','hunter','inker','magnet','jelly','crab','eel','urchin','boss','bstar','boct','bjelly','beel','p-life','p-slow','p-freeze','p-shield','p-bomb','p-lure','p-time','p-boost','trap']"

def rect_up(x0, y0, x1, bottom=35):
    """Trail from the bottom border up column x0, across row y0, down column x1."""
    return [[x0, y] for y in range(bottom, y0 - 1, -1)] + [[x, y0] for x in range(x0 + 1, x1 + 1)] + [[x1, y] for y in range(y0 + 1, bottom + 1)]

with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    def fresh(stars=3, extra=''):
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=3)
        pg.on('pageerror', lambda e: print('JS error:', e))
        pg.goto(url); pg.wait_for_function('window.__game'); pg.wait_for_timeout(300)
        pg.evaluate(f"""const p={{v:2,done:{{}},stars:{{}},best:{{}},seen:{SEEN},skin:'boat',daily:{{}},rush:12400}};
          __game.levels.slice(0,47).forEach(id=>{{p.done[id]=true;p.stars[id]={stars}}});
          const now=new Date(); for (let d=1; d<=now.getUTCDate(); d++) p.daily[now.getUTCFullYear()+'-'+String(now.getUTCMonth()+1).padStart(2,'0')+'-'+String(d).padStart(2,'0')]={{stars:1+d%3}};
          const pm=new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth()-1, 1)); for (let d=1; d<=new Date(Date.UTC(pm.getUTCFullYear(), pm.getUTCMonth()+1, 0)).getUTCDate(); d++) p.daily[pm.toISOString().slice(0,8)+String(d).padStart(2,'0')]={{stars:3}};
          {extra} localStorage.setItem('ls_prog', JSON.stringify(p))""")
        pg.reload(); pg.wait_for_function('window.__game'); pg.wait_for_timeout(900)
        pg.add_style_tag(content='#hint{display:none!important}')
        return pg
    def level(lv, monsters, skin=None):
        pg = fresh(extra=f"p.skin='{skin}';" if skin else '')
        pg.evaluate(f"__game.startLevel({lv - 1})"); pg.wait_for_timeout(200)
        pg.evaluate("__game.skipIntro()"); pg.wait_for_function('!__game.snap().entering', timeout=60000); pg.wait_for_timeout(1500)
        pg.evaluate("__game.freeze(true); __game.clearMonsters()")
        for k, x, y in monsters: pg.evaluate(f"__game.addMonster('{k}', {x}, {y})")
        return pg
    def save(pg, shot):
        d = out / f'{name}-{shot}.png'; pg.screenshot(path=str(d)); Image.open(d).convert('RGB').save(d)
        print('wrote', d.name); pg.close()
    T = lambda pg, cells, close: pg.evaluate('([c, k]) => __game.trail(c, k)', [cells, close])

    # 1: a level in progress, two areas claimed and a trail being drawn
    pg = level(3, [('bouncer', 15.5, 10.5), ('bouncer', 8.5, 15.5), ('bouncer', 18.5, 19.5)])
    T(pg, rect_up(2, 23, 7), True); pg.wait_for_timeout(1300)
    T(pg, [[12, y] for y in range(2, 9)] + [[x, 8] for x in range(11, 1, -1)], True); pg.wait_for_timeout(1300)
    T(pg, [[15, y] for y in range(35, 26, -1)] + [[x, 27] for x in range(16, 20)], False); pg.evaluate("__game.setLives(2)")
    pg.wait_for_timeout(900); save(pg, '1-draw')
    # 2: a boss: the King Puffer in the meadow, the camera a little closer
    pg = level(20, [('boss', 12.5, 13.5), ('bouncer', 6.5, 7.5), ('bouncer', 17.5, 21.5)])
    T(pg, rect_up(2, 26, 7), True); pg.wait_for_timeout(1300)
    T(pg, [[x, 2] for x in range(14, 22)] + [[21, y] for y in range(3, 9)] + [[x, 8] for x in range(20, 13, -1)] + [[14, y] for y in range(7, 1, -1)], True); pg.wait_for_timeout(1300)
    T(pg, [[15, y] for y in range(35, 24, -1)] + [[x, 24] for x in range(14, 10, -1)], False)
    cx, cz = pg.evaluate("__game.world(12, 17)")
    pg.evaluate(f"__game.cam([{cx}, 30, {cz + 19}, {cx}, 0, {cz + 1}, 50])")
    pg.wait_for_timeout(900); save(pg, '2-boss')
    # 3: the volcano: eel, urchins and a huge claim rising
    pg = level(92, [('eel', 9.5, 10.5), ('urchin', 16.5, 8.5), ('bouncer', 6.5, 6.5), ('urchin', 5.5, 14.5)], 'turtle')
    T(pg, [[x, 22] for x in range(2, 22)], True); pg.wait_for_timeout(420); save(pg, '3-claim')
    # 4: home: levels, Daily and Rush
    pg = fresh(); save(pg, '4-home')
    # 5: skins
    pg = fresh(); pg.evaluate("document.querySelector('[data-act=skins]').click()"); pg.wait_for_timeout(900); save(pg, '5-skins')
    # 6: Daily calendar and trophies
    pg = fresh(); pg.evaluate("document.querySelector('[data-act=trophies]').click()"); pg.wait_for_timeout(1500); save(pg, '6-trophies')
    b.close()
