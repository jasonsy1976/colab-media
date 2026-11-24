import sys,asyncio
from playwright.async_api import async_playwright
async def main(ts):
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--allow-file-access-from-files"])
        pg=await b.new_page(viewport={"width":1920,"height":1080})
        await pg.goto("file:///home/claude/v2/v2.html"); await pg.wait_for_timeout(500)
        for t in ts:
            await pg.evaluate(f"setTime({t})")
            await pg.screenshot(path=f"stills/t{float(t):06.1f}.jpg",type="jpeg",quality=85)
        await b.close()
asyncio.run(main(sys.argv[1:]))
