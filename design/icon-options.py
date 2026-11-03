# Renders app icon options from the real game (www/index.html). Run `npm run build` first.
# Usage: python3 design/icon-options.py [out_dir]
import pathlib, sys
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'design' / 'icon-options'; out.mkdir(parents=True, exist_ok=True)
SEEN = "['rush','bouncer','eater','saw','zipper','splitter','hunter','inker','magnet','jelly','crab','eel','urchin','boss','bstar','boct','bjelly','beel','p-life','p-slow','p-freeze','p-shield','p-bomb','p-lure','p-time','trap']"
HIDE = '#hud,#pad,#dpad,#panel,#coach,.hint,#power,#flash,#vignette,.pop,.tplus{display:none!important}'

with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    def scene(lv, monsters, setup):
        pg = b.new_page(viewport={'width': 1024, 'height': 1024}, device_scale_factor=1)
        pg.on('pageerror', lambda e: print('JS error:', e))
        pg.goto(f'file://{root}/www/index.html'); pg.wait_for_function('window.__game'); pg.wait_for_timeout(300)
        pg.evaluate(f"__game.unlockAll(); const p=JSON.parse(localStorage.getItem('ls_prog')); p.seen={SEEN}; localStorage.setItem('ls_prog', JSON.stringify(p))")
        pg.reload(); pg.wait_for_function('window.__game'); pg.wait_for_timeout(500)
        pg.add_style_tag(content=HIDE)
        pg.evaluate(f"__game.startLevel({lv - 1})"); pg.wait_for_timeout(200); pg.evaluate("__game.skipIntro()")
        pg.wait_for_function('!__game.snap().entering', timeout=90000); pg.wait_for_timeout(600)
        pg.evaluate("__game.freeze(true); __game.clearMonsters()")
        for k, x, y in monsters: pg.evaluate(f"__game.addMonster('{k}', {x}, {y})")
        setup(pg); return pg
    T = lambda pg, cells, close: pg.evaluate('([c, k]) => __game.trail(c, k)', [cells, close])
    def cam(pg, eye, look, fov=40):
        pg.evaluate(f"__game.cam([{eye[0]},{eye[1]},{eye[2]},{look[0]},{look[1]},{look[2]},{fov}])")

    # A: the boat coming toward you, its dashed line back to the land it left
    def a(pg):
        T(pg, [[x, 26] for x in range(2, 22)], True); pg.wait_for_timeout(1800)
        T(pg, [[12, y] for y in range(25, 18, -1)], False); pg.wait_for_timeout(400)
        bx, bz = pg.evaluate("__game.world(12, 19)")
        cam(pg, (bx + 2.6, 5.2, bz - 4.6), (bx - 0.3, 0.2, bz + 1.6), 46); pg.wait_for_timeout(900)
    pg = scene(3, [('bouncer', 8.5, 17.5), ('bouncer', 17.5, 9.5)], a); pg.screenshot(path=str(out / 'icon-a-boat.png')); pg.close()

    # B: the boat and the King Puffer
    def bb(pg):
        T(pg, [[x, 26] for x in range(2, 22)], True); pg.wait_for_timeout(1800)
        T(pg, [[10, y] for y in range(25, 18, -1)], False); pg.wait_for_timeout(400)
        bx, bz = pg.evaluate("__game.world(11.5, 19)")
        cam(pg, (bx + 1.5, 6.0, bz - 6.0), (bx, 0.3, bz + 1.0), 44); pg.wait_for_timeout(900)
    pg = scene(20, [('boss', 14.5, 18.5), ('bouncer', 6.5, 12.5)], bb); pg.screenshot(path=str(out / 'icon-b-boss.png')); pg.close()

    # C: from above: land claimed in two cuts, a third line on its way
    def c(pg):
        T(pg, [[9, y] for y in range(35, 1, -1)], True); pg.wait_for_timeout(1800)
        T(pg, [[x, 28] for x in range(10, 22)], True); pg.wait_for_timeout(1800)
        T(pg, [[x, 18] for x in range(10, 16)], False); pg.wait_for_timeout(300)
        cx, cz = pg.evaluate("__game.world(12, 21)")
        cam(pg, (cx, 24, cz + 6), (cx, 0, cz), 40); pg.wait_for_timeout(900)
    pg = scene(4, [('bouncer', 16.5, 11.5), ('bouncer', 18.5, 23.5)], c); pg.screenshot(path=str(out / 'icon-c-island.png')); pg.close()
    b.close()
