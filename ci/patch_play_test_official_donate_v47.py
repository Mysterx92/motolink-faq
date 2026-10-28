#!/usr/bin/env python3
"""MotoLink Play TEST v47: restore official v1.8.2 PayPal Donate URL.

Authoritative public source:
Mysterx1992/MotoLink main app/src/main/java/it/motolink/app/MainActivity.kt
openPayPalDonation() URL: https://www.paypal.com/donate/?hosted_button_id=N7BM2VCKWWKNN

Both Credits donation button and the one-shot donation popup call the same
openPayPalDonation() function. Keep user-facing texts and the unverified
return/sticker behavior unchanged. No real payment confirmation inferred.
"""
from pathlib import Path

root = Path("src")
main = root / "app/src/main/java/it/motolink/app/MainActivity.kt"
gradle = root / "app/build.gradle.kts"
m = main.read_text(encoding="utf-8")
b = gradle.read_text(encoding="utf-8")

def once(text: str, old: str, new: str, tag: str) -> str:
    n = text.count(old)
    if n != 1:
        raise AssertionError(f"V47 {tag}: expected one match, found {n}")
    return text.replace(old, new, 1)

m = once(
    m,
    'val donationUrl = "https://www.paypal.com/ncp/payment/FF47AQ6KB4QFC"',
    'val donationUrl = "https://www.paypal.com/donate/?hosted_button_id=N7BM2VCKWWKNN"',
    "official donation URL from public release",
)
m = once(
    m,
    'AppLog.add("DONAZIONI V42 TEST: apertura PayPal diretta; nessuna conferma transazione")',
    'AppLog.add("DONAZIONI V47 TEST: apertura PayPal Donate ufficiale; nessuna conferma transazione")',
    "non-transaction-claiming diagnostic log",
)
b = once(b, "versionCode = 46", "versionCode = 47", "versionCode")
b = once(
    b,
    'versionName = "1.8.2-calimoto-navigation-test"',
    'versionName = "1.8.2-calimoto-official-donate-test"',
    "versionName",
)

assert 'val donationUrl = "https://www.paypal.com/donate/?hosted_button_id=N7BM2VCKWWKNN"' in m
assert "https://www.paypal.com/ncp/payment/FF47AQ6KB4QFC" not in m
assert "onCreditsDonateClick = { openPayPalDonation() }" in m
assert "onPositive = { openPayPalDonation() }" in m
assert "showPayPalReturnUnverified()" in m
assert "openStickerRequestEmail()" in m
assert "v43_support_prompt_once" in m
assert "versionCode = 47" in b

main.write_text(m, encoding="utf-8")
gradle.write_text(b, encoding="utf-8")
print("V47_PATCH_PASS: Credits and popup use official release PayPal Donate URL, unverified-return/sticker semantics unchanged")
