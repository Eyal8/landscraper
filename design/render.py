# Renders the app icon, adaptive-icon foreground, splash and the Play feature graphic from design/art.html.
# Then run `npx @capacitor/assets generate` to update the native icons and splash.
import pathlib
from PIL import Image
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent
assets = root.parent / 'assets'
store = root.parent / 'store' / 'android'
store.mkdir(parents=True, exist_ok=True)
jobs = [('icon', 1024, 1024, assets / 'icon-only.png', False), ('fg', 1024, 1024, assets / 'icon-foreground.png', True),
        ('splash', 2732, 2732, assets / 'splash.png', False), ('feature', 1024, 500, store / 'feature-graphic.png', False)]
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    for mode, w, h, out, transparent in jobs:
        pg = b.new_page(viewport={'width': w, 'height': h})
        pg.on('pageerror', lambda e: print('JS error:', e))
        pg.goto(f'file://{root}/art.html?mode={mode}')
        pg.wait_for_function('document.title === "ready"', timeout=20000)
        pg.wait_for_timeout(800)
        pg.screenshot(path=str(out), omit_background=transparent)
        if not transparent: Image.open(out).convert('RGB').save(out)
        print('wrote', out.name)
    b.close()
# Play icon: 512 x 512, no alpha
Image.open(assets / 'icon-only.png').convert('RGB').resize((512, 512), Image.LANCZOS).save(store / 'play-icon-512.png')
# Adaptive icon background: the sky gradient as a flat image
Image.open(assets / 'icon-only.png').convert('RGB').crop((0, 0, 4, 4)).resize((1024, 1024)).save(assets / 'icon-background.png')
print('wrote play-icon-512.png, icon-background.png')
