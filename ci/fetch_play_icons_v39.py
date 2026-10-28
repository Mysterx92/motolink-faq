#!/usr/bin/env python3
"""Fetch public Play listing icons as static artwork for the curated directory.
Unsuccessful requests produce explicit, test-only placeholders; never guess logos.
Nothing runs on the phone and no API credentials are used.
"""
import html, io, re, urllib.request, pathlib, json, time
from html.parser import HTMLParser
from PIL import Image, ImageDraw, ImageFont

entries=[
("prezzi_benzina","org.vernazza.androidfuel","PB"),
("restaurant_guru","restaurant.guru","RG"),
("dmd2","com.thorkracing.dmd2launcher","D2"),
("kurviger","com.kurviger.app","K"),
("rever","com.reverllc.rever","R"),
("diablo","it.pirelli.diablosuperbiker","DS"),
("meteo_am","it.meteoam.app","AM"),
("luceverde","it.aci.luceverde.client.mobileapp","LV"),
("where_are_u","it.Beta80Group.whereareu","112"),
("detecht","se.app.detecht","DT"),
("drivvo","br.com.ctncardoso.ctncar","DV"),
("biker_connect","app.bikerconnect","BC"),
]
dest=pathlib.Path("src/app/src/main/res/drawable-nodpi")
dest.mkdir(parents=True,exist_ok=True)
class Metas(HTMLParser):
    def __init__(self):super().__init__();self.v=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()!="meta":return
        d=dict(attrs)
        if d.get("property") in ("og:image","twitter:image") or d.get("name")=="twitter:image":
            u=d.get("content")
            if u and u.startswith("https://"):self.v.append(u)
def get(url):
    req=urllib.request.Request(url,headers={
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept-Language":"it-IT,it;q=0.9,en-US;q=0.7"})
    with urllib.request.urlopen(req, timeout=15) as r:return r.read()
report=[]
for name,pkg,label in entries:
    ok=False;reason=""
    try:
        page=get("https://play.google.com/store/apps/details?id="+pkg+"&hl=it&gl=IT").decode("utf-8","replace")
        parser=Metas();parser.feed(page)
        # Icon is the first image associated with the Play Store listing.
        urls=[html.unescape(u) for u in parser.v if "googleusercontent.com" in u]
        if not urls:raise ValueError("No Play Store og:image found")
        raw=get(urls[0])
        pic=Image.open(io.BytesIO(raw)).convert("RGBA")
        if min(pic.size)<64:raise ValueError("icon source too small")
        pic.thumbnail((192,192),Image.Resampling.LANCZOS)
        canvas=Image.new("RGBA",(192,192),(0,0,0,0));canvas.alpha_composite(pic,((192-pic.width)//2,(192-pic.height)//2))
        canvas.save(dest/("app_catalog_"+name+".png"),format="PNG",optimize=True)
        ok=True
    except Exception as e:
        reason=type(e).__name__+": "+str(e)[:180]
        pic=Image.new("RGB",(192,192),(13,32,20))
        dr=ImageDraw.Draw(pic)
        dr.rounded_rectangle([3,3,188,188],radius=32,outline=(71,173,91),width=6)
        try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",53)
        except OSError:font=ImageFont.load_default()
        box=dr.textbbox((0,0),label,font=font)
        dr.text(((192-(box[2]-box[0]))/2,(192-(box[3]-box[1]))/2-box[1]),label,fill=(115,238,138),font=font)
        pic.save(dest/("app_catalog_"+name+".png"),format="PNG",optimize=True)
    report.append({"package":pkg,"logo":name,"official_play_icon":ok,"fallback_reason":reason})
    print(("ICON_OK" if ok else "FALLBACK")+" "+pkg+" "+reason,flush=True)
pathlib.Path("PLAY_ICON_AUDIT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("OFFICIAL_PLAY_ICONS "+str(sum(x["official_play_icon"] for x in report))+"/12",flush=True)
