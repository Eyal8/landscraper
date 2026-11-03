# Test bot: plays levels headless and prints win rate, time and causes of death per level.
# Usage: npm run build; python3 scripts/bot/runbot.py [levels comma-separated, 0-based] [runs per level]
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
levels = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else list(range(100))
runs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width":200,"height":400})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://" + str(pathlib.Path(__file__).resolve().parents[2] / "www/index.html")); await pg.wait_for_timeout(300)
        await pg.evaluate("__game.unlockAll(); const p=JSON.parse(localStorage.getItem('ls_prog')); p.seen=['rush','bouncer','eater','saw','zipper','splitter','hunter','inker','magnet','jelly','crab','eel','urchin','boss','bstar','boct','bjelly','beel','p-life','p-slow','p-freeze','p-shield','p-bomb','p-lure','p-time','trap']; localStorage.setItem('ls_prog', JSON.stringify(p))")
        await pg.reload(); await pg.wait_for_timeout(800)
        await pg.add_script_tag(path=str(pathlib.Path(__file__).with_name("bot.js")))
        for lv in levels:
            res = []
            for r in range(runs):
                out = await pg.evaluate(f"runBot({lv}, 200)")
                res.append(out)
            wins = sum(1 for o in res if o['win'])
            print(json.dumps({"lv": lv, "wins": wins, "runs": runs, "t": [round(o['t']) for o in res], "deaths": [o['deaths'] for o in res], "pct": [o.get("pct") for o in res], "why": [o.get("why") for o in res]}), flush=True)
        print("errors", errs[:3], flush=True); await b.close()
asyncio.run(main())
