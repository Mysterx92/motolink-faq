#!/usr/bin/env python3
"""Build-only patch for the isolated MotoLink Play TEST source checkout.
Never changes the official release branch, trading logic, or credentials.
"""
from pathlib import Path

root = Path("src")
ui = root / "app/src/main/java/it/motolink/app/TrofeoDashboardView.kt"
main = root / "app/src/main/java/it/motolink/app/MainActivity.kt"
build = root / "app/build.gradle.kts"
assert ui.is_file() and main.is_file() and build.is_file(), "Unexpected source tree"

def one(source, old, new, label):
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one anchor, found {count}")
    return source.replace(old, new, 1)

u = ui.read_text(encoding="utf-8")
u = one(u, "    var onPrivacyClick: (() -> Unit)? = null", "    var onPrivacyClick: (() -> Unit)? = null\n    var onFaqClick: (() -> Unit)? = null", "UI callback")
old = '''        row.addView(ai, LinearLayout.LayoutParams(0, LayoutParams.MATCH_PARENT, 1f))
        return row
    }

    private fun buildSupportLog()'''
new = '''        row.addView(ai, LinearLayout.LayoutParams(0, LayoutParams.MATCH_PARENT, 1f))
        val faq = text("FAQ", 23f, GREEN, false).apply {
            gravity = Gravity.CENTER
            isClickable = true
            isFocusable = true
            contentDescription = "FAQ MotoLink"
            setOnClickListener { onFaqClick?.invoke() }
        }
        row.addView(faq, LinearLayout.LayoutParams(0, LayoutParams.MATCH_PARENT, 1f))
        return row
    }

    private fun buildSupportLog()'''
u = one(u, old, new, "Support FAQ tab button")

m = main.read_text(encoding="utf-8")
m = one(m, "            onPrivacyClick = { openPrivacyPolicy() }", "            onPrivacyClick = { openPrivacyPolicy() }\n            onFaqClick = { openFaqPage() }", "Main FAQ callback")
m = one(m,
 "https://github.com/Mysterx1992/MotoLink/blob/main/PRIVACY.md",
 "https://mysterx92.github.io/motolink-privacy/",
 "Official Privacy URL")
m = one(m,
 "Impossibile aprire la pagina. Consulta PRIVACY.md nel repository ufficiale MotoLink su GitHub.",
 "Impossibile aprire la pagina Privacy. Verifica la connessione Internet e riprova.",
 "Privacy error text")
m = one(m,
 "    private fun openPrivacyPolicy() {",
 '''    private fun openFaqPage() {
        val faqUrl = "https://mysterx92.github.io/motolink-faq/"
        try {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(faqUrl)))
            AppLog.add("FAQ: apertura pagina di supporto richiesta dall'utente")
        } catch (t: Throwable) {
            AppLog.add("FAQ: apertura pagina non riuscita ${t.javaClass.simpleName}")
            NeonDialogs.showInfo(
                this,
                "FAQ MotoLink",
                "Impossibile aprire le FAQ. Verifica la connessione Internet e riprova."
            )
        }
    }

    private fun openPrivacyPolicy() {''',
 "Open FAQ function")

b = build.read_text(encoding="utf-8")
b = one(b, "versionCode = 36", "versionCode = 37", "TEST version code")
b = one(b, 'versionName = "1.8.2"', 'versionName = "1.8.2-faqtest"', "TEST version name")
assert "it.motolink.app.preplaytest2" not in b or 'applicationIdSuffix = ".preplaytest2"' in b
assert "https://mysterx92.github.io/motolink-faq/" in m
assert "https://mysterx92.github.io/motolink-privacy/" in m
assert "onFaqClick" in m and "onFaqClick" in u
assert "QUERY_ALL_PACKAGES" not in u  # no new permissions

ui.write_text(u, encoding="utf-8")
main.write_text(m, encoding="utf-8")
build.write_text(b, encoding="utf-8")
print("PATCH_PASS: Support FAQ button, external FAQ URL, Privacy URL, isolated TEST version 37")
