#!/usr/bin/env python3
"""V42: direct PayPal NCP + optional supporter sticker mail request, manual verification.
Preserves V41 one-shot invitation, original app core and non-verified return semantics.
"""
from pathlib import Path
root=Path("src")
main=root/"app/src/main/java/it/motolink/app/MainActivity.kt"
locale=root/"app/src/main/java/it/motolink/app/MotoLinkLocale.kt"
gradle=root/"app/build.gradle.kts"

def one(s,old,new,label):
    n=s.count(old)
    if n != 1:
        raise AssertionError(f"{label}: wanted exactly one anchor; found {n}")
    return s.replace(old,new,1)

m=main.read_text(encoding="utf-8")
l=locale.read_text(encoding="utf-8")
b=gradle.read_text(encoding="utf-8")

# One direct external checkout. PayPal-hosted NCP button is a real-money payment page.
m=one(m,
'''        val donationUrl = "https://mysterx92.github.io/motolink-faq/sostieni-test/"''',
'''        val donationUrl = "https://www.paypal.com/ncp/payment/FF47AQ6KB4QFC"''',
"direct PayPal NCP link")
m=one(m,
'''            AppLog.add("DONAZIONI V41 TEST: apertura pagina ponte PayPal; nessuna conferma transazione")''',
'''            AppLog.add("DONAZIONI V42 TEST: apertura PayPal diretta; nessuna conferma transazione")''',
"direct log")

m=one(m,
'''    private fun showPayPalReturnUnverified() {
        AppLog.add("DONAZIONI V41 TEST: ritorno browser osservato; esito pagamento UNKNOWN; zero verifica server")
        NeonDialogs.showInfo(this,
            MotoLinkLocale.donationReturnTitle(),
            MotoLinkLocale.donationReturnBody(),
            MotoLinkLocale.donationContinue())
    }''',
'''    private fun showPayPalReturnUnverified() {
        // Anyone can invoke this intent. No transaction proof is received in the app.
        // Thank the supporter without claiming confirmed payment; sticker is manual-only.
        AppLog.add("DONAZIONI V42 TEST: ritorno browser; pagamento UNKNOWN; eventuale adesivo soggetto a verifica manuale")
        NeonDialogs.showConfirm(this,
            MotoLinkLocale.donationThanksTitle(),
            MotoLinkLocale.donationThanksBody(),
            MotoLinkLocale.stickerRequestButton(),
            MotoLinkLocale.stickerDeclineButton(),
            onPositive = { openStickerRequestEmail() },
            onNegative = { }
        )
    }

    private fun openStickerRequestEmail() {
        // Personal details remain in the chosen external email app. Never stored by MotoLink.
        val intent = Intent(Intent.ACTION_SENDTO).apply {
            data = Uri.parse("mailto:motolinkofficial.app@gmail.com")
            putExtra(Intent.EXTRA_SUBJECT, MotoLinkLocale.stickerMailSubject())
            putExtra(Intent.EXTRA_TEXT, MotoLinkLocale.stickerMailBody())
        }
        try {
            startActivity(intent)
            AppLog.add("DONAZIONI V42 TEST: aperta app email esterna, nessun dato personale registrato")
        } catch (_: Throwable) {
            NeonDialogs.showInfo(this,
                MotoLinkLocale.stickerMailErrorTitle(),
                MotoLinkLocale.stickerMailErrorBody())
        }
    }''',
"thanks and email on unverified return")

for old,new in [("TEST v41: PayPal","TEST v42: PayPal"),
                ("ТЕСТ v41: PayPal","ТЕСТ v42: PayPal"),
                ("测试版 v41：PayPal","测试版 v42：PayPal")]:
    l=l.replace(old,new)
extra='''    fun donationThanksTitle(): String = when(language()) {
        "it" -> "Grazie di cuore! 💚"
        "ru" -> "Большое спасибо! 💚"
        "zh" -> "衷心感谢！💚"
        else -> "Thank you so much! 💚"
    }

    fun donationThanksBody(): String = when(language()) {
        "it" -> "Grazie per aver scelto di sostenere MotoLink! Se hai completato una donazione, puoi richiedere il nostro adesivo SOSTENITORE da 6 cm. La richiesta viene gestita via email e la donazione sarà controllata manualmente prima di un eventuale invio. Questo rientro da PayPal non è una conferma automatica di pagamento. L'adesivo è un omaggio facoltativo, soggetto a disponibilità."
        "ru" -> "Спасибо за поддержку MotoLink! Если вы завершили пожертвование, вы можете по электронной почте запросить наклейку SOSTENITORE диаметром 6 см. Перед отправкой пожертвование проверяется вручную. Возврат из PayPal сам по себе не подтверждает оплату. Наклейка доступна при наличии."
        "zh" -> "感谢支持 MotoLink！如果你已完成捐赠，可以通过电子邮件申请 6 厘米 SOSTENITORE 贴纸。寄送前会人工核实捐赠。返回 PayPal 页面本身不代表付款成功。贴纸为自愿赠品，数量有限。"
        else -> "Thank you for supporting MotoLink! If you completed a donation, you can request our 6 cm SOSTENITORE sticker by email. Payment is checked manually before any shipment. Returning from PayPal is not automatic proof of payment. Stickers are optional gifts, subject to availability."
    }

    fun stickerRequestButton(): String = when(language()) {
        "it" -> "RICHIEDI ADESIVO"
        "ru" -> "ЗАПРОСИТЬ НАКЛЕЙКУ"
        "zh" -> "申请贴纸"
        else -> "REQUEST STICKER"
    }
    fun stickerDeclineButton(): String = when(language()) {
        "it" -> "NO GRAZIE"
        "ru" -> "НЕТ, СПАСИБО"
        "zh" -> "不用了，谢谢"
        else -> "NO THANKS"
    }
    fun stickerMailSubject(): String = when(language()) {
        "it" -> "Richiesta adesivo MotoLink Sostenitore"
        "ru" -> "Запрос наклейки MotoLink Sostenitore"
        "zh" -> "申请 MotoLink Sostenitore 贴纸"
        else -> "MotoLink Sostenitore sticker request"
    }
    fun stickerMailBody(): String = when(language()) {
        "it" -> "Buongiorno!\\nHo effettuato una donazione per sostenere il progetto MotoLink e vorrei richiedere, se disponibile, l'adesivo MotoLink SOSTENITORE da 6 cm.\\n\\nDati per la spedizione (compilare solo se si desidera la spedizione):\\nNome:\\nCognome:\\nIndirizzo completo (abitazione oppure punto di ritiro):\\nRiferimento transazione PayPal (facoltativo, NON inserire credenziali):\\n\\nGrazie e complimenti per il progetto MotoLink!"
        "ru" -> "Здравствуйте!\\nЯ поддержал(а) MotoLink пожертвованием и хочу попросить наклейку MotoLink SOSTENITORE 6 см, если она доступна.\\n\\nИмя:\\nФамилия:\\nАдрес доставки / пункт выдачи:\\nНомер транзакции PayPal (необязательно; без паролей):\\n\\nСпасибо!"
        "zh" -> "你好！\\n我已捐赠支持 MotoLink，希望申请一张 6 厘米 MotoLink SOSTENITORE 贴纸（如有库存）。\\n\\n姓名：\\n收件地址或自提点：\\nPayPal 交易编号（选填，请勿填写密码）：\\n\\n谢谢！"
        else -> "Hello!\\nI made a donation to support MotoLink and would like to request the 6 cm MotoLink SOSTENITORE sticker, if available.\\n\\nFirst name:\\nLast name:\\nShipping address or pickup point:\\nPayPal transaction reference (optional; never share passwords):\\n\\nThank you!"
    }

    fun stickerMailErrorTitle(): String = when(language()) {
        "it" -> "Nessuna app email"
        "ru" -> "Нет почтового приложения"
        "zh" -> "未找到邮件应用"
        else -> "No email app found"
    }
    fun stickerMailErrorBody(): String = when(language()) {
        "it" -> "Configura un'app email sul telefono e riprova, oppure scrivi a motolinkofficial.app@gmail.com."
        "ru" -> "Настройте почтовое приложение или напишите на motolinkofficial.app@gmail.com."
        "zh" -> "请设置邮件应用，或发送邮件至 motolinkofficial.app@gmail.com。"
        else -> "Set up an email app on your phone or email motolinkofficial.app@gmail.com."
    }

'''
l=one(l,"    fun donationReturnTitle(): String = when(language()) {",
      extra+"    fun donationReturnTitle(): String = when(language()) {",
      "four-language thank-you and email content")

b=one(b,"versionCode = 41","versionCode = 42","v42 versionCode")
b=one(b,'versionName = "1.8.2-donation-return-test"','versionName = "1.8.2-paypal-direct-sticker-test"',"v42 versionName")
for p,content in [(main,m),(locale,l),(gradle,b)]:
    p.write_text(content,encoding="utf-8")
assert "FF47AQ6KB4QFC" in m
assert "https://mysterx92.github.io/motolink-faq/sostieni-test/" not in m
assert "Intent.ACTION_SENDTO" in m and "motolinkofficial.app@gmail.com" in m
assert "donationThanksTitle()" in l and "stickerMailBody()" in l
assert "versionCode = 42" in b
print("V42_PATCH_PASS: PayPal direct, manual-only sticker request, email intent, IT EN RU ZH")
