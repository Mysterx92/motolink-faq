#!/usr/bin/env python3
"""v40 isolated TEST patch: localized app descriptions and hardware/gesture back navigation.
Run after v38 FAQ patch and v39 APP patch. Original MotoLink release stays unchanged.
"""
from pathlib import Path
root=Path("src")
ui=root/"app/src/main/java/it/motolink/app/TrofeoDashboardView.kt"
main=root/"app/src/main/java/it/motolink/app/MainActivity.kt"
locale=root/"app/src/main/java/it/motolink/app/MotoLinkLocale.kt"
gradle=root/"app/build.gradle.kts"
manifest=root/"app/src/main/AndroidManifest.xml"
def one(s,old,new,label):
    count=s.count(old)
    if count!=1: raise AssertionError(f"{label}: expected one anchor; found {count}")
    return s.replace(old,new,1)
u=ui.read_text(encoding="utf-8")
m=main.read_text(encoding="utf-8")
l=locale.read_text(encoding="utf-8")
b=gradle.read_text(encoding="utf-8")
x=manifest.read_text(encoding="utf-8")

# Each app row preserves the verified Play icon and clickable full-width surface.
old='''                    appRow.addView(text(app.name, 28f, Color.WHITE, true).apply {
                        gravity = Gravity.CENTER_VERTICAL
                        maxLines = 2
                        ellipsize = TextUtils.TruncateAt.END
                    }, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f))
                    appRow.addView(icon(IconKind.CHEVRON, GREEN)'''
new='''                    val labelColumn = LinearLayout(context).apply {
                        orientation = LinearLayout.VERTICAL
                        gravity = Gravity.CENTER_VERTICAL
                    }
                    labelColumn.addView(text(app.name, 26f, Color.WHITE, true).apply {
                        maxLines = 1
                        ellipsize = TextUtils.TruncateAt.END
                    }, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT))
                    labelColumn.addView(text(MotoLinkLocale.appCatalogDescription(app.packageId), 18f, 0xFFBFCAC2.toInt(), false).apply {
                        maxLines = 2
                        ellipsize = TextUtils.TruncateAt.END
                        setLineSpacing(pxH(2f).toFloat(), 1.05f)
                    }, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT).apply {
                        topMargin = pxH(8f)
                    })
                    appRow.addView(labelColumn, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f))
                    appRow.addView(icon(IconKind.CHEVRON, GREEN)'''
u=one(u,old,new,"App icon + title + localized description")
u=one(u,"    private var appCatalogCategoryIndex: Int? = null",
        "    private var appCatalogCategoryIndex: Int? = null\n    private val pageBackStack = ArrayDeque<Page>()",
        "Page history")
u=one(u,'''                    page = target
                    appCatalogCategoryIndex = null
                    if (target != Page.SUPPORT)''',
'''                    if (!guideActive && target != page) {
                        pageBackStack.addLast(page)
                        if (pageBackStack.size > 24) pageBackStack.removeFirst()
                    }
                    page = target
                    appCatalogCategoryIndex = null
                    if (target != Page.SUPPORT)''',"Remember visited pages in bottom bar")
u=one(u,'''    fun startInitialGuide() {
        guideActive = true''',
'''    fun startInitialGuide() {
        pageBackStack.clear()
        guideActive = true''',"Guide resets page back stack")
u=one(u,'''    fun isOnboardingActive(): Boolean = guideActive''',
'''    fun isOnboardingActive(): Boolean = guideActive

    /** Called by Android system Back button and committed edge-swipe gesture. */
    fun navigateSystemBack(): Boolean {
        if (guideActive) {
            if (guideStepIndex > 0) guidePrevious() else finishGuide()
            return true
        }
        if (page == Page.APPS && appCatalogCategoryIndex != null) {
            appCatalogCategoryIndex = null
            rebuild()
            return true
        }
        if (page == Page.SUPPORT && supportTab == SupportTab.ASSISTANT) {
            supportTab = SupportTab.LOG
            rebuild()
            return true
        }
        if (pageBackStack.isNotEmpty()) {
            page = pageBackStack.removeLast()
            appCatalogCategoryIndex = null
            supportTab = SupportTab.LOG
            rebuild()
            return true
        }
        if (page != Page.HOME) {
            page = Page.HOME
            appCatalogCategoryIndex = null
            supportTab = SupportTab.LOG
            rebuild()
            return true
        }
        return false // MainActivity handles a deliberate second Back to leave.
    }''',"System Back navigation")
# Localize all new app descriptions in the same language layer as the other screens.
localeHelpers = "    fun appCatalogDescription(packageName: String): String {\n        val index = when (packageName) {\n            \"org.vernazza.androidfuel\" -> 0\n            \"restaurant.guru\" -> 1\n            \"com.thorkracing.dmd2launcher\" -> 2\n            \"com.kurviger.app\" -> 3\n            \"com.reverllc.rever\" -> 4\n            \"it.pirelli.diablosuperbiker\" -> 5\n            \"it.meteoam.app\" -> 6\n            \"it.aci.luceverde.client.mobileapp\" -> 7\n            \"it.Beta80Group.whereareu\" -> 8\n            \"se.app.detecht\" -> 9\n            \"br.com.ctncardoso.ctncar\" -> 10\n            \"app.bikerconnect\" -> 11\n            else -> return \"\"\n        }\n        val translations = when (language()) {\n            \"it\" -> listOf(\"Trova distributori e confronta i prezzi carburante.\", \"Scopri ristoranti, recensioni e menu lungo il viaggio.\", \"Mappe e percorsi GPS pensati per le moto.\", \"Pianifica itinerari moto ricchi di curve.\", \"Registra viaggi e scopri nuovi itinerari moto.\", \"Registra giri, tempi e angoli di piega.\", \"Previsioni meteo, pioggia e vento.\", \"Controlla traffico, cantieri e viabilità.\", \"Chiama il 112 e invia la posizione dove supportato.\", \"Percorsi moto e rilevamento di possibili incidenti.\", \"Registra tagliandi, consumi e costi della moto.\", \"Organizza uscite e incontra altri motociclisti.\")\n            \"ru\" -> listOf(\"Поиск АЗС и сравнение цен на топливо.\", \"Рестораны, меню и отзывы по пути.\", \"Карты и GPS-маршруты для мотоциклов.\", \"Планирование мотомаршрутов с поворотами.\", \"Запись поездок и поиск мотомаршрутов.\", \"Запись поездок, времени кругов и углов наклона.\", \"Прогноз погоды, осадки и ветер.\", \"Пробки, ремонт дорог и дорожные условия.\", \"Вызов 112 и передача геопозиции, где доступно.\", \"Мотомаршруты и обнаружение возможных аварий.\", \"Учёт обслуживания, расхода топлива и затрат.\", \"Организация поездок и общение с мотоциклистами.\")\n            \"zh\" -> listOf(\"查找加油站并比较燃油价格。\", \"查找沿途餐厅、菜单和评价。\", \"摩托车专用地图与 GPS 路线。\", \"规划弯道丰富的摩托骑行路线。\", \"记录骑行并发现新的摩托路线。\", \"记录骑行、圈速及倾角。\", \"查看天气预报、降雨和风况。\", \"查看交通、道路施工和路况。\", \"在支持地区拨打 112 并共享位置。\", \"摩托路线及潜在事故检测。\", \"记录摩托车保养、油耗和费用。\", \"组织骑行并结识其他摩友。\")\n            else -> listOf(\"Find fuel stations and compare pump prices.\", \"Find restaurants, menus and reviews on your route.\", \"Motorcycle maps and GPS route planning.\", \"Plan scenic motorcycle routes with twisty roads.\", \"Track rides and discover motorcycle routes.\", \"Record rides, lap times and lean angles.\", \"Weather forecasts, rain and wind conditions.\", \"Check traffic, roadworks and road conditions.\", \"Call 112 and share location where supported.\", \"Motorcycle routes and possible crash detection.\", \"Track maintenance, fuel use and motorcycle costs.\", \"Plan rides and connect with other motorcyclists.\")\n        }\n        return translations[index]\n    }\n\n    fun appCatalogExitHint(): String = when (language()) {\n        \"it\" -> \"Premi ancora Indietro per uscire da MotoLink\"\n        \"ru\" -> \"Нажмите «Назад» ещё раз для выхода из MotoLink\"\n        \"zh\" -> \"再次按返回键退出 MotoLink\"\n        else -> \"Press Back again to leave MotoLink\"\n    }\n\n"
l=one(l,"    fun appCatalogCategory(index: Int): String {",
      localeHelpers+"    fun appCatalogCategory(index: Int): String {",
      "Descriptions and exit hint IT EN RU ZH")
l=one(l,'''In ogni categoria trovi soltanto una o due app selezionate.''',
        '''In ogni categoria trovi soltanto una o due app selezionate. Usa Indietro (tasto o gesto Android) per tornare alla schermata precedente.''',
        "IT guide back gesture")
l=one(l,'''Each category contains only one or two carefully selected apps.''',
        '''Each category contains only one or two carefully selected apps. Use the Android Back button or gesture to return to the previous screen.''',
        "EN guide back gesture")
l=one(l,'''В каждой категории одно или два выбранных приложения.''',
        '''В каждой категории одно или два выбранных приложения. Для возврата используйте кнопку или жест «Назад» Android.''',
        "RU guide back gesture")
l=one(l,'''每个分类仅推荐一到两个应用。''',
        '''每个分类仅推荐一到两个应用。使用 Android 返回键或返回手势回到上一个页面。''',
        "ZH guide back gesture")
# Plain Activity: API 33+ uses Android's modern OnBackInvokedCallback,
# older devices use Activity.onBackPressed. All paths share one UI back stack.
m=one(m,"    private lateinit var dashboard: TrofeoDashboardView",
'''    private lateinit var dashboard: TrofeoDashboardView
    private var lastRootBackMs = 0L
    private var platformBackCallback: android.window.OnBackInvokedCallback? = null''',
    "Main Back fields")
m=one(m,'''        setContentView(dashboard)
        refreshFavoriteApps()''',
'''        setContentView(dashboard)
        if (Build.VERSION.SDK_INT >= 33) {
            val callback = android.window.OnBackInvokedCallback { handleSystemBackNavigation() }
            onBackInvokedDispatcher.registerOnBackInvokedCallback(
                android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT, callback
            )
            platformBackCallback = callback
        }
        refreshFavoriteApps()''',"Register gesture callback API 33")
m=one(m,"    private fun startFirstRunExperience() {",
'''    private fun handleSystemBackNavigation() {
        if (::dashboard.isInitialized && dashboard.navigateSystemBack()) {
            lastRootBackMs = 0L
            return
        }
        val now = android.os.SystemClock.elapsedRealtime()
        if (now - lastRootBackMs in 0..2000L) {
            lastRootBackMs = 0L
            moveTaskToBack(true)
        } else {
            lastRootBackMs = now
            android.widget.Toast.makeText(
                this, MotoLinkLocale.appCatalogExitHint(), android.widget.Toast.LENGTH_SHORT
            ).show()
        }
    }

    @Suppress("DEPRECATION")
    override fun onBackPressed() {
        handleSystemBackNavigation()
    }

    private fun startFirstRunExperience() {''',"Back handler all supported versions")
m=one(m,'''    override fun onDestroy() {
        invalidateRecovery()''',
'''    override fun onDestroy() {
        if (Build.VERSION.SDK_INT >= 33) {
            platformBackCallback?.let { onBackInvokedDispatcher.unregisterOnBackInvokedCallback(it) }
            platformBackCallback = null
        }
        invalidateRecovery()''',"Unregister on destruction")
# Explicitly enable modern Back dispatch in the test MainActivity; no new permissions.
x=one(x,'''            android:name=".MainActivity"
            android:exported="false"''',
'''            android:name=".MainActivity"
            android:enableOnBackInvokedCallback="true"
            android:exported="false"''',"Enable Back gesture callback")
b=one(b,"versionCode = 39","versionCode = 40","Version code")
b=one(b,'versionName = "1.8.2-app-catalog-test"','versionName = "1.8.2-app-catalog-back-test"',"Version name")

assert all(item in l for item in ['"it"', '"ru"', '"zh"', 'fun appCatalogDescription', 'fun appCatalogExitHint'])
assert "fun navigateSystemBack()" in u and "OnBackInvokedCallback" in m
assert "setPackage(\"com.android.vending\")" in m
for p,content in [(ui,u),(main,m),(locale,l),(gradle,b),(manifest,x)]:
    p.write_text(content,encoding="utf-8")
print("V40_PATCH_PASS: 12 localized descriptions, back stack, system gesture+button, guide, exit confirmation")
