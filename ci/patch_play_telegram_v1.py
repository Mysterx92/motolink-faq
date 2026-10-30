#!/usr/bin/env python3
"""Minimal MotoLink PLAY 1.0 community migration (v47 source, post release patch).
Only official Telegram link, related user-facing copy and two visible icons.
"""
from pathlib import Path
import json

root = Path("src/app/src/main/java/it/motolink/app")
main = root / "MainActivity.kt"
dashboard = root / "TrofeoDashboardView.kt"
locale = root / "MotoLinkLocale.kt"

OLD_URL = "https://chat.whatsapp.com/BNTmFxXQuOkGdYWHrX2rV0?s=cl&p=a&mlu=4"
NEW_URL = "https://t.me/+HV4qZqQ6iEg3ZjM0"

def once(text, old, new, name):
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{name}: expected exactly 1 occurrence of {old!r}, found {count}")
    return text.replace(old, new)

m = main.read_text(encoding="utf-8")
m = once(m, OLD_URL, NEW_URL, "Telegram invite URL")
if m.count("openWhatsAppGroup()") != 3:
    raise AssertionError("Unexpected WhatsApp group method call count")
m = m.replace("openWhatsAppGroup()", "openTelegramGroup()")
m = m.replace("gruppo WhatsApp MotoLink Mirroring", "gruppo Telegram MotoLink Community")
m = m.replace("gruppo WhatsApp", "gruppo Telegram")
m = m.replace("collegamento WhatsApp", "collegamento Telegram")
m = m.replace('"MotoLink Mirroring", "Impossibile aprire il collegamento Telegram', '"MotoLink Community", "Impossibile aprire il collegamento Telegram')
assert OLD_URL not in m and NEW_URL in m
assert "private fun openTelegramGroup()" in m
main.write_text(m, encoding="utf-8")

d = dashboard.read_text(encoding="utf-8")
# Preserve the layout and callbacks; replace only the two externally visible
# WhatsApp glyphs with the existing neutral SEND/paper-plane icon.
d = once(d, 'actionButton(IconKind.WHATSAPP, "Apri gruppo WhatsApp")',
            'actionButton(IconKind.SEND, "Apri gruppo Telegram")', "Assistant community button")
d = once(d, 'actionButton(IconKind.WHATSAPP, "Entra nel gruppo")',
            'actionButton(IconKind.SEND, "Entra nel gruppo")', "Credits community button")
d = d.replace("gruppo WhatsApp “MotoLink Mirroring”",
              "community Telegram “MotoLink Community”")
d = d.replace("gruppo WhatsApp MotoLink Mirroring",
              "gruppo Telegram MotoLink Community")
assert "Apri gruppo WhatsApp" not in d
assert "actionButton(IconKind.WHATSAPP" not in d
dashboard.write_text(d, encoding="utf-8")

l = locale.read_text(encoding="utf-8")
assert "WhatsApp" in l
l = l.replace("WhatsApp", "Telegram")
l = l.replace("MotoLink Mirroring", "MotoLink Community")
assert "WhatsApp" not in l
locale.write_text(l, encoding="utf-8")

# The post-release patch is deliberately confined to the three UI source
# files already changed in v47 patch replay. All approved multimedia stays frozen.
audit = Path("PLAY_V1_SOURCE_AUDIT.json")
data = json.loads(audit.read_text(encoding="utf-8"))
data["official_community_url"] = NEW_URL
data["community_ui"] = "Telegram (Credits, Assistant, help, locale); SEND icon in both visible buttons"
data["release_changes_after_v47"].append(
    "replace public WhatsApp community link/copy/two visible icons with MotoLink Community Telegram"
)
audit.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("PLAY_TELEGRAM_COMMUNITY_PATCH_PASS", NEW_URL)
