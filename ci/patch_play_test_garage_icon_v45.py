#!/usr/bin/env python3
"""TEST v45: replace Garage add-profile QR icon with plus, remove plus from title.

Runs AFTER v44, on isolated throwaway MotoLink source tree.
Do not modify application behavior or published MotoLink release.
"""
from pathlib import Path

root = Path("src")
ui = root / "app/src/main/java/it/motolink/app/TrofeoDashboardView.kt"
gradle = root / "app/build.gradle.kts"
u = ui.read_text(encoding="utf-8")
b = gradle.read_text(encoding="utf-8")

def exactly_one(source: str, old: str, new: str, tag: str) -> str:
    n = source.count(old)
    if n != 1:
        raise AssertionError(f"v45 {tag}: expected 1 match, got {n}")
    return source.replace(old, new, 1)

# Existing LineIconView has a native PLUS icon; reuse it in the left icon slot.
# The existing QR icon in QR scanner menus elsewhere remains untouched.
u = exactly_one(
    u,
    "row.addView(icon(IconKind.QR, GREEN), LinearLayout.LayoutParams(pxX(112f), pxH(112f)))",
    "row.addView(icon(IconKind.PLUS, GREEN), LinearLayout.LayoutParams(pxX(112f), pxH(112f)))",
    "left Garage tile QR -> PLUS",
)
# No plus at the end of the title: there must be one visible '+' at LEFT only.
u = exactly_one(
    u,
    'text("Aggiungi un altro profilo +", 30f, Color.WHITE, true)',
    'text("Aggiungi un altro profilo", 30f, Color.WHITE, true)',
    "title without trailing plus",
)
u = exactly_one(
    u,
    "usa Aggiungi un altro profilo + per aggiungerne un'altra.",
    "usa Aggiungi un altro profilo per aggiungerne un'altra.",
    "onboarding text",
)
b = exactly_one(b, "versionCode = 44", "versionCode = 45", "versionCode")
b = exactly_one(
    b,
    'versionName = "1.8.2-garage-empty-card-test"',
    'versionName = "1.8.2-garage-plus-icon-test"',
    "versionName",
)

assert "IconKind.PLUS ->" in u, "native plus icon must be implemented"
assert "row.addView(icon(IconKind.PLUS, GREEN), LinearLayout.LayoutParams(pxX(112f), pxH(112f)))" in u
assert 'text("Aggiungi un altro profilo", 30f, Color.WHITE, true)' in u
assert 'text("Con QR o profilo locale", 22f, 0xFFB7B7B7.toInt(), false)' in u
assert "bikeProfiles.isNotEmpty() && bikeProfiles.size < 3 && y < 1160f" in u
assert "setOnClickListener { onQrClick?.invoke() }" in u
assert "versionCode = 45" in b
ui.write_text(u, encoding="utf-8")
gradle.write_text(b, encoding="utf-8")
print("V45_PATCH_PASS: large plus icon left; title has no plus; all Garage actions unchanged")
