import sys,asyncio,subprocess,os
from playwright.async_api import async_playwright
FPS=30
B=[0,12.25,38.95,74.85,112.55,138.45,173.15,198.75,217.65]
END=7566  # frames (252.2 s)
fb=[round(x*FPS) for x in B]+[END]
async def main(idx):
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--allow-file-access-from-files"])
        pg=await b.new_page(viewport={"width":1920,"height":1080})
        await pg.goto("file:///home/claude/v2/v2.html"); await pg.wait_for_timeout(600)
        for i in idx:
            a,z=fb[i],fb[i+1]; tmp=f"seg/s{i}.tmp.mp4"
            ff=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","image2pipe","-framerate",str(FPS),"-c:v","mjpeg","-i","-","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p","-r",str(FPS),tmp],stdin=subprocess.PIPE)
            for f in range(a,z):
                await pg.evaluate(f"setTime({f/FPS})")
                ff.stdin.write(await pg.screenshot(type="jpeg",quality=92))
            ff.stdin.close(); ff.wait()
            if ff.returncode==0: os.rename(tmp,f"seg/s{i}.mp4"); print("done",i,z-a,flush=True)
        await b.close()
asyncio.run(main([int(x) for x in sys.argv[1:]]))
