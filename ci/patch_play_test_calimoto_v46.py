#!/usr/bin/env python3
"""MotoLink TEST v46: add calimoto to the existing Navigation app catalog.

Applied after v45, only to isolated Play TEST source checkout.
No change to existing recommended apps, Garage, donations, mirroring, permissions,
original MotoLink release, or signing. No third-party code embedded in APK.
"""
from pathlib import Path

root = Path("src")
ui = root / "app/src/main/java/it/motolink/app/TrofeoDashboardView.kt"
main = root / "app/src/main/java/it/motolink/app/MainActivity.kt"
locale = root / "app/src/main/java/it/motolink/app/MotoLinkLocale.kt"
gradle = root / "app/build.gradle.kts"
icon_loader = Path("ci/fetch_play_icons_v39.py")

u = ui.read_text(encoding="utf-8")
m = main.read_text(encoding="utf-8")
l = locale.read_text(encoding="utf-8")
b = gradle.read_text(encoding="utf-8")
i = icon_loader.read_text(encoding="utf-8")

def once(text: str, old: str, new: str, tag: str) -> str:
    n = text.count(old)
    if n != 1:
        raise AssertionError(f"V46 {tag}: expected exactly one anchor, got {n}")
    return text.replace(old, new, 1)

# Keep DMD2 and Kurviger; append calimoto in the SAME category (index 2).
u = once(
    u,
    'AppCatalogEntry("Kurviger", "com.kurviger.app", R.drawable.app_catalog_kurviger)',
    'AppCatalogEntry("Kurviger", "com.kurviger.app", R.drawable.app_catalog_kurviger),\n'
    '                AppCatalogEntry("calimoto", "com.calimoto.calimoto", R.drawable.app_catalog_calimoto)',
    "Navigation entry",
)

# Only this exact verified Google Play package identifier may open the Play listing.
m = once(
    m,
    '"com.thorkracing.dmd2launcher", "com.kurviger.app",',
    '"com.thorkracing.dmd2launcher", "com.kurviger.app", "com.calimoto.calimoto",',
    "Google Play allowlist",
)

# Existing 12 descriptions and their indices remain identical. Add calimoto at 12.
l = once(
    l,
    '            "app.bikerconnect" -> 11\n            else -> return ""',
    '            "app.bikerconnect" -> 11\n'
    '            "com.calimoto.calimoto" -> 12\n'
    '            else -> return ""',
    "description dispatch",
)
for tag, original, added in (
    ("Italian", '"Organizza uscite e incontra altri motociclisti.")',
     '"Organizza uscite e incontra altri motociclisti.", "Pianifica itinerari moto panoramici e ricchi di curve.")'),
    ("Russian", '"Организация поездок и общение с мотоциклистами.")',
     '"Организация поездок и общение с мотоциклистами.", "Планируйте живописные маршруты для мотоциклов с множеством поворотов.")'),
    ("Chinese", '"组织骑行并结识其他摩友。")',
     '"组织骑行并结识其他摩友。", "规划风景优美、弯道丰富的摩托车路线。")'),
    ("English", '"Plan rides and connect with other motorcyclists.")',
     '"Plan rides and connect with other motorcyclists.", "Plan scenic motorcycle rides with plenty of curves.")'),
):
    l = once(l, original, added, f"{tag} description")

# Existing tour copy said 1-2 recommended apps per category; navigation now has 3.
for tag, old, new in (
    ("IT guide count", "In ogni categoria trovi soltanto una o due app selezionate.", "In ogni categoria trovi app selezionate."),
    ("RU guide count", "В каждой категории одно или два выбранных приложения.", "В каждой категории представлены выбранные приложения."),
    ("ZH guide count", "每个分类仅推荐一到两个应用。", "每个分类都有精选应用。"),
    ("EN guide count", "Each category contains only one or two carefully selected apps.", "Each category contains carefully selected apps."),
):
    l = once(l, old, new, tag)

# Existing icon fetcher obtains the public Play listing's icon at BUILD time only.
# Its test-only fallback produces a branded-neutral "CM" placeholder if unavailable.
i = once(
    i,
    '("biker_connect","app.bikerconnect","BC"),\n]',
    '("biker_connect","app.bikerconnect","BC"),\n'
    '("calimoto","com.calimoto.calimoto","CM"),\n]',
    "icon fetch list",
)
i = once(
    i,
    '+"/12",flush=True)',
    '+"/13",flush=True)',
    "icon audit total",
)

b = once(b, "versionCode = 45", "versionCode = 46", "versionCode")
b = once(
    b,
    'versionName = "1.8.2-garage-plus-icon-test"',
    'versionName = "1.8.2-calimoto-navigation-test"',
    "versionName",
)

assert "AppCatalogEntry(\"DMD2\"" in u
assert "AppCatalogEntry(\"Kurviger\"" in u
assert "AppCatalogEntry(\"calimoto\", \"com.calimoto.calimoto\", R.drawable.app_catalog_calimoto)" in u
assert 'text("Aggiungi un altro profilo", 30f, Color.WHITE, true)' in u
assert "versionCode = 46" in b
assert "com.calimoto.calimoto" in m and "com.calimoto.calimoto" in i
assert all(s in l for s in ("Pianifica itinerari moto panoramici", "Планируйте живописные", "规划风景优美", "Plan scenic motorcycle"))
ui.write_text(u, encoding="utf-8")
main.write_text(m, encoding="utf-8")
locale.write_text(l, encoding="utf-8")
gradle.write_text(b, encoding="utf-8")
icon_loader.write_text(i, encoding="utf-8")
print("V46_PATCH_PASS: verified calimoto in navigation, +1 Play allowlist, +1 official icon, 4 locales, no core changes")
