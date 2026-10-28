#!/usr/bin/env python3
"""V43 test: user-facing donation invitation and decline copy, no changes to logic.
Apply after v42. UI wording only plus Android app versionCode/versionName.
"""
from pathlib import Path

source=Path("src/app/src/main/java/it/motolink/app/MotoLinkLocale.kt")
gradle=Path("src/app/build.gradle.kts")
s=source.read_text(encoding="utf-8")
b=gradle.read_text(encoding="utf-8")

def replace_one(original, before, after, label):
    count=original.count(before)
    if count!=1:
        raise AssertionError(f"{label}: expected one occurrence, got {count}")
    return original.replace(before,after,1)

invite='''    fun donationInviteBody(): String = when(language()) {
        "it" -> "MotoLink nasce dalla passione per le moto ed è gratuita, senza pubblicità e senza abbonamenti.\\n\\nSe ti è utile e vuoi sostenere il progetto, puoi fare una donazione dell'importo che preferisci. Ogni contributo aiuta a migliorare MotoLink e a mantenerla accessibile a tutti.\\n\\nGrazie per far parte di questa avventura! 💚"
        "ru" -> "MotoLink создан из любви к мотоциклам и остаётся бесплатным, без рекламы и подписок.\\n\\nЕсли приложение вам полезно, вы можете поддержать проект добровольным пожертвованием на любую сумму. Каждый вклад помогает развивать MotoLink и сохранять его доступным для всех.\\n\\nСпасибо, что вы с нами! 💚"
        "zh" -> "MotoLink 源于对摩托车的热爱，始终免费、无广告、无订阅。\\n\\n如果你喜欢 MotoLink，欢迎自愿选择任意金额支持项目。每一份心意都帮助我们持续改进，让更多人免费使用。\\n\\n感谢你一路同行！💚"
        else -> "MotoLink was born from a passion for motorcycles. It's free, with no ads and no subscriptions.\\n\\nIf you enjoy using it and would like to support the project, you can make a voluntary donation of any amount. Every contribution helps MotoLink improve and stay accessible to everyone.\\n\\nThank you for being part of the journey! 💚"
    }
'''
decline='''    fun donationDeclineBody(): String = when(language()) {
        "it" -> "Grazie per aver scelto MotoLink! 💚\\n\\nIl fatto che tu la utilizzi è già una grande soddisfazione. Continua a goderti tutte le sue funzioni gratuitamente e buon viaggio!\\n\\nSe un giorno vorrai sostenere il progetto, troverai sempre FAI UNA DONAZIONE nella sezione CREDITI."
        "ru" -> "Спасибо, что выбрали MotoLink! 💚\\n\\nТо, что вы пользуетесь приложением, уже очень приятно. Наслаждайтесь всеми функциями бесплатно и счастливого пути!\\n\\nЕсли позже захотите поддержать проект, кнопка пожертвования всегда доступна в разделе «Авторы»."
        "zh" -> "感谢你选择 MotoLink！💚\\n\\n能陪伴你的骑行就是很大的鼓励。请继续免费享用所有功能，祝你一路平安！\\n\\n如果以后想支持项目，随时可以在“致谢”页面找到捐赠按钮。"
        else -> "Thank you for choosing MotoLink! 💚\\n\\nKnowing that you enjoy using the app already means a lot. Keep enjoying every feature for free, and have a great ride!\\n\\nIf you ever want to support the project, you'll always find DONATE in Credits."
    }
'''

start_invite='    fun donationInviteBody(): String = when(language()) {'
end_invite='    fun donationAction(): String = when(language()) {'
i,j=s.index(start_invite),s.index(end_invite)
if i<0 or j<i: raise AssertionError("invite boundaries")
s=replace_one(s,s[i:j],invite+"\n","invite popup only")

start_decline='    fun donationDeclineBody(): String = when(language()) {'
end_decline='    fun donationReturnTitle(): String = when(language()) {'
i,j=s.index(start_decline),s.index(end_decline)
if i<0 or j<i: raise AssertionError("decline boundaries")
s=replace_one(s,s[i:j],decline+"\n","decline popup only")

b=replace_one(b,"versionCode = 42","versionCode = 43","versionCode")
b=replace_one(b,'versionName = "1.8.2-paypal-direct-sticker-test"',
              'versionName = "1.8.2-user-facing-support-copy-test"',"versionName")

for func,stop in [(start_invite,end_invite),(start_decline,end_decline)]:
    body=s[s.index(func):s.index(stop)]
    assert "TEST v" not in body and "ТЕСТ v" not in body and "测试版" not in body
    assert all(x in body for x in ['"it"', '"ru"', '"zh"', 'else'])
assert "versionCode = 43" in b
assert 'fun donationThanksBody()' in s and 'fun stickerMailBody()' in s
source.write_text(s,encoding="utf-8")
gradle.write_text(b,encoding="utf-8")
print("V43_PATCH_PASS: ONLY invitation/decline copy IT-EN-RU-ZH and version metadata updated")
