#!/usr/bin/env python3
"""Isolated v41 TEST patch: voluntary one-shot donation invitation + neutral PayPal return.
Requires FAQ v38, APP v39, and Back v40 patches first. Does not touch official release.
No real-payment claims, no payment records, no sensitive input and no broker/backend.
"""
from pathlib import Path
root=Path("src")
main=root/"app/src/main/java/it/motolink/app/MainActivity.kt"
locale=root/"app/src/main/java/it/motolink/app/MotoLinkLocale.kt"
gradle=root/"app/build.gradle.kts"
manifest=root/"app/src/main/AndroidManifest.xml"
bridge=root/"app/src/main/java/it/motolink/app/DonationReturnActivity.kt"

def one(s,old,new,label):
    n=s.count(old)
    if n!=1: raise AssertionError(f"{label}: expected one anchor, found {n}")
    return s.replace(old,new,1)

m=main.read_text(encoding="utf-8")
l=locale.read_text(encoding="utf-8")
b=gradle.read_text(encoding="utf-8")
x=manifest.read_text(encoding="utf-8")

m=one(m,'''        private const val PREF_SAFETY_NOTICE_SUPPRESSED = "safety_notice_suppressed"''',
'''        private const val PREF_SAFETY_NOTICE_SUPPRESSED = "safety_notice_suppressed"
        private const val PREF_SUPPORT_V41_ALREADY_SHOWN = "v41_support_prompt_once"
        const val EXTRA_PAYPAL_RETURN_UNVERIFIED = "motolink_paypal_return_unverified"''',"v41 prefs")

m=one(m,'''        dashboard.post { startFirstRunExperience() }''',
'''        dashboard.post {
            if (intent?.getBooleanExtra(EXTRA_PAYPAL_RETURN_UNVERIFIED, false) == true) {
                intent?.removeExtra(EXTRA_PAYPAL_RETURN_UNVERIFIED)
                showPayPalReturnUnverified()
            } else {
                startFirstRunExperience()
            }
        }''',"v41 fresh launch return")
m=one(m,"    private fun startFirstRunExperience() {",
'''    override fun onNewIntent(newIntent: Intent) {
        super.onNewIntent(newIntent)
        setIntent(newIntent)
        if (newIntent.getBooleanExtra(EXTRA_PAYPAL_RETURN_UNVERIFIED, false)) {
            newIntent.removeExtra(EXTRA_PAYPAL_RETURN_UNVERIFIED)
            if (::dashboard.isInitialized) {
                dashboard.post { showPayPalReturnUnverified() }
            }
        }
    }

    private fun showPayPalReturnUnverified() {
        AppLog.add("DONAZIONI V41 TEST: ritorno browser osservato; esito pagamento UNKNOWN; zero verifica server")
        NeonDialogs.showInfo(this,
            MotoLinkLocale.donationReturnTitle(),
            MotoLinkLocale.donationReturnBody(),
            MotoLinkLocale.donationContinue())
    }

    private fun showSupportInvitationOnce() {
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        if (prefs.getBoolean(PREF_SUPPORT_V41_ALREADY_SHOWN, false)) return
        // Consume before display, so upgrades/restarts never generate repeated requests.
        prefs.edit().putBoolean(PREF_SUPPORT_V41_ALREADY_SHOWN, true).apply()
        AppLog.add("DONAZIONI V41 TEST: invito volontario one-shot; pagamento non verificato")
        NeonDialogs.showConfirm(this,
            MotoLinkLocale.donationInviteTitle(),
            MotoLinkLocale.donationInviteBody(),
            MotoLinkLocale.donationAction(),
            MotoLinkLocale.donationNotNow(),
            onPositive = { openPayPalDonation() },
            onNegative = { showSupportThanksAnyway() }
        )
    }

    private fun showSupportThanksAnyway() {
        NeonDialogs.showInfo(this,
            MotoLinkLocale.donationDeclineTitle(),
            MotoLinkLocale.donationDeclineBody(),
            MotoLinkLocale.donationContinue())
    }

    private fun startFirstRunExperience() {''',"v41 no-verify return and popup")

m=one(m,'''        if (prefs.getBoolean(PREF_SAFETY_NOTICE_SUPPRESSED, false)) return
        SafetyNoticeDialog.show(this) { suppressFuture ->''',
'''        if (prefs.getBoolean(PREF_SAFETY_NOTICE_SUPPRESSED, false)) {
            showSupportInvitationOnce()
            return
        }
        SafetyNoticeDialog.show(this) { suppressFuture ->''',"safety suppression order")
m=one(m,'''                AppLog.add("SICUREZZA: avviso guida confermato; verrà mostrato ai prossimi avvii")
            }
        }
    }''',
'''                AppLog.add("SICUREZZA: avviso guida confermato; verrà mostrato ai prossimi avvii")
            }
            showSupportInvitationOnce()
        }
    }''',"safety accepted -> voluntary invitation")

m=one(m,'''        val donationUrl = "https://www.paypal.com/donate/?hosted_button_id=N7BM2VCKWWKNN"''',
'''        // Stable first-party TEST redirect: the public v40 payment link remains untouched.
        // The linked NCP PayPal button is REAL, so never simulate an actual payment.
        val donationUrl = "https://mysterx92.github.io/motolink-faq/sostieni-test/"''',"donation URL in v41")
m=one(m,'''            AppLog.add("CREDITI: apertura pagina PayPal Sostieni MotoLink")''',
'''            AppLog.add("DONAZIONI V41 TEST: apertura pagina ponte PayPal; nessuna conferma transazione")''',"donation log")

helper='''    fun donationInviteTitle(): String = when(language()) {
        "it" -> "Ti piace MotoLink? 💚"
        "ru" -> "Нравится MotoLink? 💚"
        "zh" -> "喜欢 MotoLink 吗？💚"
        else -> "Enjoying MotoLink? 💚"
    }

    fun donationInviteBody(): String = when(language()) {
        "it" -> "Ho creato MotoLink con passione e tante ore di lavoro, per offrirti un'app gratuita, senza pubblicità e senza abbonamenti. Se ti è utile e vuoi ringraziarmi, puoi lasciare una donazione libera. Il tuo sostegno mi aiuta a mantenerla così e a migliorarla. Grazie di cuore!\\n\\nTEST v41: PayPal è reale; scegli tu l'importo e non è necessario pagare per provare il collegamento."
        "ru" -> "Я создал MotoLink с любовью и потратил много времени, чтобы приложение оставалось бесплатным, без рекламы и подписок. Если оно полезно, вы можете поддержать проект добровольным пожертвованием. Спасибо!\\n\\nТЕСТ v41: PayPal настоящий, сумму выбираете вы. Для проверки ссылки платить не нужно."
        "zh" -> "我投入了大量时间和热情开发 MotoLink，希望它始终免费、无广告、无订阅。如果它对你有帮助，你可以自愿捐赠支持项目。衷心感谢！\\n\\n测试版 v41：PayPal 为真实支付页面，金额由你决定。测试链接无需付款。"
        else -> "I created MotoLink with passion and many hours of work, to keep it free, ad-free and without subscriptions. If you find it useful, you can choose to leave a voluntary donation. Your support helps me improve it. Thank you!\\n\\nTEST v41: PayPal is real and you choose the amount. No payment is needed to test the link."
    }

    fun donationAction(): String = when(language()) {
        "it" -> "FAI UNA DONAZIONE"
        "ru" -> "ПОДДЕРЖАТЬ"
        "zh" -> "自愿捐赠"
        else -> "DONATE"
    }
    fun donationNotNow(): String = when(language()) {
        "it" -> "NON ORA"
        "ru" -> "НЕ СЕЙЧАС"
        "zh" -> "暂时不"
        else -> "NOT NOW"
    }
    fun donationDeclineTitle(): String = when(language()) {
        "it" -> "Grazie comunque! 💚"
        "ru" -> "Всё равно спасибо! 💚"
        "zh" -> "依然感谢你！💚"
        else -> "Thank you anyway! 💚"
    }
    fun donationDeclineBody(): String = when(language()) {
        "it" -> "Il fatto che tu abbia scelto MotoLink è già una grande soddisfazione. Continua a usarla liberamente e goditi i tuoi viaggi in moto! Se un giorno cambi idea, troverai sempre il pulsante FAI UNA DONAZIONE nella sezione CREDITI."
        "ru" -> "То, что вы выбрали MotoLink, уже очень много значит. Пользуйтесь приложением свободно и наслаждайтесь поездками! Поддержать проект позже можно в разделе «Авторы»."
        "zh" -> "你选择 MotoLink 本身就是对我的鼓励。欢迎继续免费使用，享受骑行！以后如果改变主意，可在“致谢”中找到捐赠按钮。"
        else -> "Choosing MotoLink already means a lot to me. Keep using it freely and enjoy your rides! You can always find DONATE in Credits if you change your mind."
    }
    fun donationReturnTitle(): String = when(language()) {
        "it" -> "Rientro da PayPal"
        "ru" -> "Возврат из PayPal"
        "zh" -> "从 PayPal 返回"
        else -> "Back from PayPal"
    }
    fun donationReturnBody(): String = when(language()) {
        "it" -> "Sei tornato da PayPal. Questo NON conferma che la donazione sia stata completata. La verifica del pagamento non è ancora attiva nella TEST v41; nessuna richiesta di adesivo viene abilitata automaticamente."
        "ru" -> "Вы вернулись из PayPal. Это НЕ подтверждает оплату. Проверка платежей в ТЕСТ v41 пока недоступна; запрос наклейки не открывается автоматически."
        "zh" -> "你已从 PayPal 返回，但这并不代表付款成功。测试版 v41 尚未启用付款核验，不会自动开放贴纸申请。"
        else -> "You have returned from PayPal. This does NOT prove a donation was completed. Payment verification is not yet available in TEST v41, and sticker requests will not be enabled automatically."
    }
    fun donationContinue(): String = when(language()) {
        "it" -> "CONTINUA SU MOTOLINK"
        "ru" -> "ПРОДОЛЖИТЬ"
        "zh" -> "返回 MotoLink"
        else -> "CONTINUE TO MOTOLINK"
    }

'''
l=one(l,'    fun releaseNotes182(): String = when (language()) {',helper+'    fun releaseNotes182(): String = when (language()) {',"v41 locale 4 languages")

b=one(b,"versionCode = 40","versionCode = 41","v41 version code")
b=one(b,'versionName = "1.8.2-app-catalog-back-test"','versionName = "1.8.2-donation-return-test"',"v41 version name")

x=one(x,'''        <activity
            android:name=".InternalQrScannerActivity"''',
'''        <!-- Only neutral donation return; no transaction success inference from an external URI. -->
        <activity
            android:name=".DonationReturnActivity"
            android:exported="true"
            android:excludeFromRecents="true">
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="motolink-test" android:host="donazione" android:path="/ritorno" />
            </intent-filter>
        </activity>

        <activity
            android:name=".InternalQrScannerActivity"''',"separate deep link activity")

assert not bridge.exists(), "Bridge already exists; abort"
bridge.write_text('''package it.motolink.app

import android.app.Activity
import android.content.Intent
import android.os.Bundle

/** Browser return bridge only; any caller can invoke this URI.
 * Therefore the browser return is NEVER treated as verified payment.
 */
class DonationReturnActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val target = Intent(this, MainActivity::class.java).apply {
            putExtra(MainActivity.EXTRA_PAYPAL_RETURN_UNVERIFIED, true)
            addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)
        }
        startActivity(target)
        finish()
    }
}
''',encoding="utf-8")

for f,s in [(main,m),(locale,l),(gradle,b),(manifest,x)]:
    f.write_text(s,encoding="utf-8")
assert "v41_support_prompt_once" in m and "showPayPalReturnUnverified()" in m
assert "onNewIntent(newIntent: Intent)" in m and "showSupportInvitationOnce()" in m
assert "https://mysterx92.github.io/motolink-faq/sostieni-test/" in m
assert "motolink-test" in x and "android:exported=\"false\"" in x
assert "versionCode = 41" in b
assert all(a in l for a in ["donationInviteTitle", "donationReturnBody", "donationDeclineBody"])
print("V41_PATCH_PASS: One-shot, safety ordering, four locales, stable PayPal TEST, neutral deep link.")
