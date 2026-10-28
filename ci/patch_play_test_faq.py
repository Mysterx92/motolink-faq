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


# Guide steps live inside the dashboard; add FAQ spotlight and localize Privacy.
faq_step = '''        GuideStep(
            Page.SUPPORT,
            SupportTab.ASSISTANT,
            title = MotoLinkLocale.guideHelpTitle(true),
            body = MotoLinkLocale.guideHelpBody(true),
            target = GuideTarget(594f, 198f, 247f, 78f)
        ),
'''
u = one(u, '''        GuideStep(
            Page.SETTINGS,
            title = "IMPOSTAZIONI · Modalità tasca",''',
        faq_step + '''        GuideStep(
            Page.SETTINGS,
            title = "IMPOSTAZIONI · Modalità tasca",''',
        "FAQ guide spotlight inserted after Assistant")
u = one(u, 'title = "IMPOSTAZIONI · Informativa privacy",',
           'title = MotoLinkLocale.guideHelpTitle(false),',
           "Privacy guide title")
old_privacy = next(line for line in u.splitlines()
    if 'body = "Apri Informativa privacy per leggere quali dati vengono trattati' in line)
u = one(u, old_privacy, "            body = MotoLinkLocale.guideHelpBody(false),", "Privacy guide body")
u = one(u, 'settingCard(IconKind.INFO, "Informativa privacy", "Leggi come vengono trattati i dati.", false, false)',
        'settingCard(IconKind.INFO, MotoLinkLocale.privacyButtonLabel(), MotoLinkLocale.privacyButtonDescription(), false, false)',
        "Privacy settings button translations")

locale_file = root / "app/src/main/java/it/motolink/app/MotoLinkLocale.kt"
assert locale_file.is_file(), "Missing locale source"
loc = locale_file.read_text(encoding="utf-8")
locale_helpers = "    fun guideHelpTitle(faq: Boolean): String = when (language()) {\n        \"it\" -> if (faq) \"SUPPORTO · FAQ\" else \"IMPOSTAZIONI · Privacy\"\n        \"ru\" -> if (faq) \"ПОДДЕРЖКА · FAQ\" else \"НАСТРОЙКИ · Приватность\"\n        \"zh\" -> if (faq) \"支持 · 常见问题\" else \"设置 · 隐私政策\"\n        else -> if (faq) \"SUPPORT · FAQ\" else \"SETTINGS · Privacy\"\n    }\n\n    fun guideHelpBody(faq: Boolean): String = when (language()) {\n        \"it\" -> if (faq) \"In SUPPORTO tocca FAQ, accanto a Log e Assistente, per trovare istruzioni e risposte ai problemi più comuni. Le FAQ si aprono nel browser e vengono aggiornate online. Sono disponibili in italiano e inglese. Esegui la configurazione sempre a moto ferma.\" else \"In IMPOSTAZIONI tocca Informativa privacy per aprire la pagina ufficiale nel browser. Puoi leggerla in italiano o in inglese tramite IT/EN. Se vuoi cancellare la sessione tecnica dell’Assistente, vai invece in Supporto > Log > Pulisci > Elimina sessione.\"\n        \"ru\" -> if (faq) \"В разделе ПОДДЕРЖКА нажмите FAQ рядом с Журналом и Помощником, чтобы найти инструкции и ответы на частые вопросы. Страница открывается в браузере и обновляется онлайн. FAQ доступна на итальянском и английском языках. Настраивайте мотоцикл только на стоянке.\" else \"В разделе НАСТРОЙКИ нажмите «Политика конфиденциальности», чтобы открыть официальную страницу в браузере. Переключатель IT/EN позволяет читать её на итальянском и английском языках. Для удаления технической сессии Помощника откройте Поддержка > Журнал > Очистить > Удалить сессию.\"\n        \"zh\" -> if (faq) \"在“支持”页面点击“常见问题（FAQ）”，即可查看连接步骤和常见问题解答。FAQ 会在浏览器中打开并在线更新，目前提供意大利语和英语。请停车后再设置摩托车。\" else \"在“设置”中点击“隐私政策”，即可在浏览器中打开官方说明。使用 IT/EN 切换意大利语和英语。如需删除助手的技术会话，请前往“支持 > 日志 > 清除 > 删除会话”。\"\n        else -> if (faq) \"In SUPPORT, tap FAQ next to Log and Assistant to find instructions and answers to common problems. The FAQ opens in your browser and is updated online. It is available in Italian and English. Configure your motorcycle only when parked.\" else \"In SETTINGS, tap Privacy policy to open the official information in your browser. Use IT/EN to read it in Italian or English. To delete the Assistant's technical session, go to Support > Log > Clear > Delete session instead.\"\n    }\n\n    fun privacyButtonLabel(): String = when (language()) {\n        \"it\" -> \"Informativa privacy\"\n        \"ru\" -> \"Политика конфиденциальности\"\n        \"zh\" -> \"隐私政策\"\n        else -> \"Privacy policy\"\n    }\n\n    fun privacyButtonDescription(): String = when (language()) {\n        \"it\" -> \"Leggi come vengono trattati i dati.\"\n        \"ru\" -> \"Узнайте, как используются ваши данные.\"\n        \"zh\" -> \"了解您的数据如何处理。\"\n        else -> \"Read how your data is handled.\"\n    }\n\n"
loc = one(loc, '    fun releaseNotes182(): String = when (language()) {',
          locale_helpers + '    fun releaseNotes182(): String = when (language()) {',
          "Four-language guided help and Privacy labels")

# Sanity: the tutorial spotlights FAQ as a real Support button,
# retains the existing Privacy card, and includes four independent languages.
assert 'GuideTarget(594f, 198f, 247f, 78f)' in u
assert 'guideHelpTitle(false)' in u and 'guideHelpBody(false)' in u
assert all(x in loc for x in ['"it" ->', '"ru" ->', '"zh" ->', 'else ->'])

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
b = one(b, "versionCode = 36", "versionCode = 38", "TEST version code")
b = one(b, 'versionName = "1.8.2"', 'versionName = "1.8.2-faq-guide-test"', "TEST version name")
assert "it.motolink.app.preplaytest2" not in b or 'applicationIdSuffix = ".preplaytest2"' in b
assert "https://mysterx92.github.io/motolink-faq/" in m
assert "https://mysterx92.github.io/motolink-privacy/" in m
assert "onFaqClick" in m and "onFaqClick" in u
assert "QUERY_ALL_PACKAGES" not in u  # no new permissions

ui.write_text(u, encoding="utf-8")
main.write_text(m, encoding="utf-8")
build.write_text(b, encoding="utf-8")
locale_file.write_text(loc, encoding="utf-8")
print("PATCH_PASS: FAQ/Privacy guide IT EN RU ZH, Support FAQ button, privacy translations, TEST version 38")
