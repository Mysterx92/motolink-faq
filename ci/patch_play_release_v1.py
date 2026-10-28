#!/usr/bin/env python3
"""Produce the isolated MotoLink 1.0 Play release from the frozen TEST v47 sources.

Run after all v38-v47 patches. No source code, logo, intro or voice changes.
Creates an unsigned release bundle; upload signing is a separate offline step.
"""
from pathlib import Path
import hashlib
import json

root = Path("src")
gradle_path = root / "app/build.gradle.kts"
manifest_path = root / "app/src/main/AndroidManifest.xml"
intro = root / "app/src/main/res/raw/motolink_intro.mp4"
voice = root / "app/src/main/res/raw/motolink_connect_voice.mp3"
foreground = root / "app/src/main/res/drawable-nodpi/ic_launcher_foreground.png"
launcher = root / "app/src/main/res/mipmap-xxxhdpi/ic_launcher.png"
main = root / "app/src/main/java/it/motolink/app/MainActivity.kt"

EXPECTED = {
    "intro_original_v47": (intro, "e56d2e412bce7c41ad27d5c796b7437035aced3fa7897b22aa0f4f78fd84874a"),
    "voice_original_v47": (voice, "8d81c6f980a969d28615be8105d2fd530b9a00a957d448609597475b3a68785e"),
    "icon_foreground_original_v47": (foreground, "dae2e4be7740de927e8986743cbbba5faa7a2b633224be30687e48ae4d83a3f8"),
    "icon_launcher_original_v47": (launcher, "96b928b8d7039a61ca2b48ff9c9862012fe524cc715fb7ceeda360f5e926129c"),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def replace_one(data, old, new, label):
    count = data.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, found {count}")
    return data.replace(old, new, 1)

for label, (path, expected) in EXPECTED.items():
    actual = sha(path)
    if actual != expected:
        raise AssertionError(f"{label} changed: {actual} != {expected}")

gradle = gradle_path.read_text(encoding="utf-8")
manifest = manifest_path.read_text(encoding="utf-8")
src = main.read_text(encoding="utf-8")

gradle = replace_one(gradle, 'applicationId = "it.motolink.app"', 'applicationId = "it.motolink.app.play"', "isolated Play applicationId")
gradle = replace_one(gradle, "versionCode = 47", "versionCode = 1", "Play versionCode")
gradle = replace_one(
    gradle, 'versionName = "1.8.2-calimoto-official-donate-test"',
    'versionName = "1.0"', "Play versionName"
)
# Preserve the source namespace, Kotlin/Java class names, app data formats and
# version-47 behaviors. Release has no debug applicationIdSuffix.
manifest = replace_one(
    manifest, 'android:taskAffinity="it.motolink.app.proximitygate"',
    'android:taskAffinity="it.motolink.app.play.proximitygate"',
    "avoid task collisions with installed official MotoLink"
)
manifest = replace_one(
    manifest, 'android:scheme="motolink-test"',
    'android:scheme="motolink-play"',
    "isolate the optional unverified PayPal-return deep link"
)
assert 'https://www.paypal.com/donate/?hosted_button_id=N7BM2VCKWWKNN' in src
assert 'https://mysterx92.github.io/motolink-privacy/' in src
assert 'https://mysterx92.github.io/motolink-faq/' in src
assert 'openStickerRequestEmail()' in src
assert 'showPayPalReturnUnverified()' in src
assert 'onPrivacyClick = { openPrivacyPolicy() }' in src
assert 'private fun openPrivacyPolicy()' in src
assert 'motolink-test' not in manifest
assert 'android:usesCleartextTraffic="true"' in manifest  # Wi-Fi motorcycle local network must remain functional
assert 'targetSdk = 36' in gradle
assert 'minSdk = 29' in gradle
assert 'namespace = "it.motolink.app"' in gradle

gradle_path.write_text(gradle, encoding="utf-8")
manifest_path.write_text(manifest, encoding="utf-8")
record = {
    "release_scope": "PLAY_1_0_FROM_FROZEN_TEST_V47",
    "application_id": "it.motolink.app.play",
    "namespace": "it.motolink.app",
    "version_code": 1,
    "version_name": "1.0",
    "target_sdk": 36,
    "min_sdk": 29,
    "kind": "UNSIGNED_RELEASE_AAB_SIGNING_REQUIRED",
    "release_changes_after_v47": [
        "app/build.gradle.kts applicationId/versionCode/versionName",
        "app/src/main/AndroidManifest.xml taskAffinity and legacy test-only URI scheme"
    ],
    "original_resource_sha256": {key: sha(path) for key, (path, _) in EXPECTED.items()},
    "verified_privacy_page": "https://mysterx92.github.io/motolink-privacy/",
    "paypal_donation_url": "https://www.paypal.com/donate/?hosted_button_id=N7BM2VCKWWKNN",
}
Path("PLAY_V1_SOURCE_AUDIT.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print("PLAY_V1_SOURCE_GATE_PASS", json.dumps(record, ensure_ascii=False))
