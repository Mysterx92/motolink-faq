#!/usr/bin/env python3
"""Fetch official Google Play app listing icons at BUILD TIME for MotoLink TEST catalog.
No runtime scraping, external icon host, API credentials or added phone permissions.
A missing or non-icon image must fail the build rather than ship incorrect artwork.
"""
import io
import sys
from pathlib import Path
import urllib.request
from PIL import Image, ImageOps
from google_play_scraper import app as play_app

APPS = [
    ("prezzi_benzina", "org.vernazza.androidfuel"),
    ("restaurant_guru", "restaurant.guru"),
    ("dmd2", "com.thorkracing.dmd2launcher"),
    ("kurviger", "com.kurviger.app"),
    ("rever", "com.reverllc.rever"),
    ("diablo", "it.pirelli.diablosuperbiker"),
    ("meteo_am", "it.meteoam.app"),
    ("luceverde", "it.aci.luceverde.client.mobileapp"),
    ("where_are_u", "it.Beta80Group.whereareu"),
    ("detecht", "se.app.detecht"),
    ("drivvo", "br.com.ctncardoso.ctncar"),
    ("biker_connect", "app.bikerconnect"),
]

target=Path("src/app/src/main/res/drawable-nodpi")
target.mkdir(parents=True, exist_ok=True)
for name, package_id in APPS:
    print("Fetching official Play icon:",name,package_id,flush=True)
    data=play_app(package_id,lang="it",country="it")
    assert data.get("appId")==package_id, (name,data.get("appId"))
    url=data.get("icon")
    assert url and url.startswith("https://"), (name,url)
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (MotoLink catalog image fetch)"})
    with urllib.request.urlopen(req,timeout=35) as res:
        raw=res.read(2_500_000)
    im=Image.open(io.BytesIO(raw))
    im.load()
    assert 96<=im.width<=2048 and 96<=im.height<=2048, (name,im.size)
    assert .80<=im.width/im.height<=1.25, (name,im.size)
    im=ImageOps.fit(im.convert("RGBA"),(192,192),method=Image.Resampling.LANCZOS)
    im.save(target/("app_catalog_"+name+".png"),optimize=True)
    print("ICON_PASS",name,"192x192",flush=True)
print("CATALOG_ICONS_PASS",len(APPS),flush=True)
