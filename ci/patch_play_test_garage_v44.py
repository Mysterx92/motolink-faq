#!/usr/bin/env python3
"""MotoLink Play TEST v44: remove duplicated add-with-QR tile ONLY in empty Garage.

Preserves the empty "Nessun profilo moto" click handler, ability to add second/third
bike, maximum-three gate, QR scanner, saved profiles, on-disk state, and all v43 flows.
Run after v43 on the read-only MotoLink source checkout inside the isolated CI.
"""
from pathlib import Path

root = Path("src")
ui = root / "app/src/main/java/it/motolink/app/TrofeoDashboardView.kt"
gradle = root / "app/build.gradle.kts"

u = ui.read_text(encoding="utf-8")
b = gradle.read_text(encoding="utf-8")

def once(source: str, before: str, after: str, purpose: str) -> str:
    count = source.count(before)
    if count != 1:
        raise AssertionError(f"V44 {purpose}: expected exactly one anchor, found {count}")
    return source.replace(before, after, 1)

# Empty Garage already has a fully clickable card "Nessun profilo moto",
# bound to the same onQrClick handler. No second tile is needed in that state.
u = once(
    u,
    "        if (bikeProfiles.size < 3 && y < 1160f) {",
    "        if (bikeProfiles.isNotEmpty() && bikeProfiles.size < 3 && y < 1160f) {",
    "only show the add tile for 1 or 2 saved profiles",
)

# The one-shot tour must spotlight the remaining first-profile entry point,
# rather than pointing to a tile removed from the empty-Garage screen.
u = once(
    u,
    """            if (bikeProfiles.size >= 3 || qrY >= 1160f) {
                GuideTarget(58f, 188f, 824f, 92f)
            } else {
                GuideTarget(58f, qrY, 824f, 215f)
            }""",
    """            if (bikeProfiles.isEmpty()) {
                GuideTarget(58f, 285f, 824f, 295f)
            } else if (bikeProfiles.size >= 3 || qrY >= 1160f) {
                GuideTarget(58f, 188f, 824f, 92f)
            } else {
                GuideTarget(58f, qrY, 824f, 215f)
            }""",
    "guide target with zero saved bikes",
)
u = once(
    u,
    "Usa Aggiungi con QR quando la moto mostra un codice QR compatibile.",
    "Se non hai ancora profili, tocca Nessun profilo moto per aggiungere la prima moto. Se hai già una moto salvata, usa Aggiungi con QR per aggiungerne un'altra.",
    "guide text for add-bike action",
)

b = once(b, "versionCode = 43", "versionCode = 44", "versionCode")
b = once(
    b,
    'versionName = "1.8.2-user-facing-support-copy-test"',
    'versionName = "1.8.2-garage-empty-card-test"',
    "versionName",
)

assert "setOnClickListener { onQrClick?.invoke() }" in u
assert "bodyHost.addView(emptyGarageCard(), lp(58f, y, 824f, 295f))" in u
assert "val add = addQrCard()" in u
assert "bikeProfiles.isNotEmpty() && bikeProfiles.size < 3 && y < 1160f" in u
assert "GuideTarget(58f, 285f, 824f, 295f)" in u
assert "versionCode = 44" in b
ui.write_text(u, encoding="utf-8")
gradle.write_text(b, encoding="utf-8")
print("V44_PATCH_PASS: no duplicate QR tile on empty Garage; add-second/third, QR, saved profiles and onboarding preserved")
