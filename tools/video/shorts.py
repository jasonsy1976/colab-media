import json, subprocess, sys, os
W = json.load(open('wordtimes.json'))
SRC = 'Video2_111_Personalized_Emails.mp4'
SHORTS = [
 ("Short1_Stop_Writing_Emails_One_by_One", "Stop writing sales emails one by one.",
  [(1.9,11.8),(19.5,32.6),(74.9,79.2),(92.2,95.9),(103.0,107.9),(108.1,111.9)]),
 ("Short2_One_Rule_AI_Emails_Safe", "The one rule that keeps AI emails safe.",
  [(112.6,119.5),(138.5,148.0),(148.2,153.9),(156.4,161.8),(217.7,226.6)]),
 ("Short3_Never_Send_100_At_Once", "Never send 100 emails at once.",
  [(173.2,180.0),(180.1,187.2),(187.7,193.6),(193.9,198.5),(198.8,217.4)]),
]
END = 2.5
MERGE = [(("one","hundred","eleven"),"111"),(("p","d","fs"),"PDFs"),(("p","d","f"),"PDF"),
 (("g","mail"),"Gmail"),(("co","lab"),"CoLab"),(("a","i"),"AI"),(("spam","er"),"spammer"),
 (("twenty","five"),"25"),(("eight","thirty"),"8:30"),(("twelve","thirty"),"12:30"),
 (("twenty",),"20"),(("fifteen",),"15")]

def segs_for(ranges):
    out = []
    for a, b in ranges:
        idx = [i for i, x in enumerate(W) if a - 0.05 <= x[1] <= b + 0.05]
        i0, i1 = idx[0], idx[-1]
        s = W[i0][1] - 0.15
        e = W[i1][2] + 0.15
        if i0 > 0: s = max(s, (W[i0-1][2] + W[i0][1]) / 2)
        if i1 + 1 < len(W): e = min(e, (W[i1][2] + W[i1+1][1]) / 2)
        out.append((round(s, 3), round(e, 3), i0, i1))
    return out

def tokens(segs):
    toks = []; off = 0.0
    for s, e, i0, i1 in segs:
        ws = [(W[i][0], W[i][1]-s+off, W[i][2]-s+off) for i in range(i0, i1+1)]
        j = 0
        while j < len(ws):
            for pat, rep in MERGE:
                n = len(pat)
                if tuple(w[0] for w in ws[j:j+n]) == pat:
                    toks.append([rep, ws[j][1], ws[j+n-1][2]]); j += n; break
            else:
                toks.append([ws[j][0], ws[j][1], ws[j][2]]); j += 1
        off += e - s
    return toks, off

def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def ass(hook, toks, dur):
    total = dur + END
    L = ["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 0","",
     "[V4+ Styles]",
     "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
     "Style: Hook,Poppins,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,8,70,70,250,1",
     "Style: Cap,Poppins,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,2,2,60,60,430,1",
     "Style: Tag,Poppins,40,&H00F0D23A,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,6,0,1,0,0,8,60,60,150,1",
     "Style: End,Poppins,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,4,5,80,80,0,1",
     "Style: Box,Poppins,10,&H00140D06,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
     "","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    L.append(f"Dialogue: 1,{ts(0)},{ts(dur)},Tag,,0,0,0,,AI SALES OFFICE PH")
    L.append(f"Dialogue: 1,{ts(0)},{ts(dur)},Hook,,0,0,0,,{{\\fscx55\\fscy55\\t(0,260,\\fscx108\\fscy108)\\t(260,400,\\fscx100\\fscy100)}}{hook}")
    # captions: groups of 3, current word yellow
    groups = [toks[i:i+3] for i in range(0, len(toks), 3)]
    for g in range(len(groups)):
        grp = groups[g]
        gend = groups[g+1][0][1] if g+1 < len(groups) else dur
        if gend - grp[-1][2] > 0.6: gend = grp[-1][2] + 0.4
        for k, w in enumerate(grp):
            st = w[1]; en = grp[k+1][1] if k+1 < len(grp) else gend
            words = []
            for m, x in enumerate(grp):
                t = x[0].upper()
                words.append(("{\\c&H3DC8FF&}" + t + "{\\c&HFFFFFF&}") if m == k else t)
            L.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{' '.join(words)}")
    # end card
    L.append(f"Dialogue: 2,{ts(dur)},{ts(total)},Box,,0,0,0,,{{\\1a&H30&\\p1}}m 0 0 l 1080 0 1080 1920 0 1920{{\\p0}}")
    L.append(f"Dialogue: 3,{ts(dur)},{ts(total)},End,,0,0,0,,{{\\fad(200,0)\\fscx70\\fscy70\\t(0,250,\\fscx100\\fscy100)}}Full video\\Non my channel")
    L.append(f"Dialogue: 3,{ts(dur+0.3)},{ts(total)},Tag,,0,0,1180,,{{\\fad(200,0)\\fs52}}AI SALES OFFICE PH")
    return "\n".join(L) + "\n"

for name, hook, ranges in SHORTS:
    segs = segs_for(ranges)
    toks, dur = tokens(segs)
    open(f'{name}.ass', 'w').write(ass(hook, toks, dur))
    parts=[]
    for i,(s0,e0,_,_) in enumerate(segs):
        p=f'cut_{name[:6]}_{i}.mp4'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',f'{s0:.3f}','-i',SRC,'-t',f'{e0-s0:.3f}',
          '-af',f'afade=t=in:d=0.03,afade=t=out:st={e0-s0-0.04:.3f}:d=0.04','-c:v','libx264','-preset','veryfast','-crf','16',
          '-r','30','-c:a','pcm_s16le','-ar','48000','-ac','2',p.replace('.mp4','.mov')],check=True)
        parts.append(p.replace('.mp4','.mov'))
    open('cl.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i','cl.txt','-c','copy','joined.mov'],check=True)
    SRCJ='joined.mov'
    fc=[f"[0:v]tpad=stop_mode=clone:stop_duration={END},split[b][f]",
        "[b]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,gblur=sigma=12,scale=1080:1920,eq=brightness=-0.18[bg]",
        "[f]scale=1080:608[fg]",
        f"[bg][fg]overlay=0:656,ass={name}.ass,fps=30,format=yuv420p[vo]",
        f"[0:a]apad=pad_dur={END}[ao]"]
    tmp = f'{name}.tmp.mp4'
    cmd = ['ffmpeg','-hide_banner','-loglevel','error','-y','-i',SRCJ,'-filter_complex',';'.join(fc),
           '-map','[vo]','-map','[ao]','-t',f'{dur+END:.3f}','-c:v','libx264','-preset','veryfast','-crf','18',
           '-c:a','aac','-b:a','192k','-movflags','+faststart',tmp]
    r = subprocess.run(cmd)
    if r.returncode == 0:
        os.rename(tmp, f'{name}.mp4'); print(name, round(dur+END, 2))
    else:
        sys.exit(1)
