# App Store / Play review screenshots for each in-app purchase (iPhone 6.7", 1290 x 2796). Run `npm run build` first.
import pathlib
from PIL import Image
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent
out = root / 'store' / 'iap'; out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    def shot(name, js):
        pg = b.new_page(viewport={'width': 430, 'height': 932}, device_scale_factor=3)
        pg.goto(f'file://{root}/www/index.html'); pg.wait_for_function('window.__game'); pg.wait_for_timeout(300)
        pg.evaluate("const p={v:2,done:{},stars:{},best:{},seen:[],skin:'boat',daily:{}}; __game.levels.slice(0,30).forEach(id=>{p.done[id]=true;p.stars[id]=3}); localStorage.setItem('ls_prog', JSON.stringify(p))")
        pg.reload(); pg.wait_for_function('window.__game'); pg.wait_for_timeout(1500)
        for step in js: pg.evaluate(step); pg.wait_for_timeout(900)
        f = out / f'{name}.png'; pg.screenshot(path=str(f)); Image.open(f).convert('RGB').save(f); print('wrote', f.name); pg.close()
    shot('shop-no-ads-everything', ["document.querySelector('[data-act=shop]').click()"])
    for pack, skin in (('sea', 'sub'), ('space', 'ufo'), ('pool', 'swan')):
        shot(f'pack-{pack}', ["document.querySelector('[data-act=skins]').click()", f"document.querySelector('[data-skin={skin}]').click()"])
    shot('all-skins', ["document.querySelector('[data-act=skins]').click()"])
    b.close()
