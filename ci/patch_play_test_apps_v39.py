#!/usr/bin/env python3
"""V39 build-only navigation/categorized-apps patch applied AFTER v38 source patch."""
from pathlib import Path
root=Path("src")
ui=root/"app/src/main/java/it/motolink/app/TrofeoDashboardView.kt"
main=root/"app/src/main/java/it/motolink/app/MainActivity.kt"
locale=root/"app/src/main/java/it/motolink/app/MotoLinkLocale.kt"
gradle=root/"app/build.gradle.kts"
def one(s, old, new, label):
    n=s.count(old)
    if n!=1: raise AssertionError(f"{label}: expected 1 anchor got {n}")
    return s.replace(old,new,1)
u=ui.read_text(encoding="utf-8")
u=one(u,"enum class Page { HOME, GARAGE, FAVORITES, SUPPORT, SETTINGS, CREDITS }","enum class Page { HOME, GARAGE, FAVORITES, APPS, SUPPORT, SETTINGS, CREDITS }","Page APPS")
u=one(u,"    var onFaqClick: (() -> Unit)? = null","    var onFaqClick: (() -> Unit)? = null\n    var onRecommendedAppClick: ((String) -> Unit)? = null","APP callback")
u=one(u,"    private var supportTab = SupportTab.LOG","    private var supportTab = SupportTab.LOG\n    private var appCatalogCategoryIndex: Int? = null","Catalog view")
u=one(u,"            Page.FAVORITES -> buildFavorites()","            Page.FAVORITES -> buildFavorites()\n            Page.APPS -> buildAppCatalog()","Page build")
u=one(u,'            Triple(Page.FAVORITES, IconKind.STAR, "Preferite"),','            Triple(Page.FAVORITES, IconKind.STAR, "Preferite"),\n            Triple(Page.APPS, IconKind.APPS, "APP"),',"Bottom nav")
u=one(u,'                    page = target\n                    if (target != Page.SUPPORT)', '                    page = target\n                    appCatalogCategoryIndex = null\n                    if (target != Page.SUPPORT)',"Nav resets category")
u=one(u,"            item.addView(text(label, 16.5f,", "            item.addView(text(label, 14.6f,","Seven nav labels responsive")
u=one(u,"        IconKind.STAR -> 1.04f", "        IconKind.STAR -> 1.04f\n        IconKind.APPS -> 1.05f","Icon size")
u=one(u,"        HOME, GARAGE, STAR, HEADSET, GEAR, INFO,", "        HOME, GARAGE, STAR, APPS, HEADSET, GEAR, INFO,","Icon enum")
u=one(u, "                IconKind.STAR -> drawStar(c,cx,cy,s*.34f,s*.15f)",
'''                IconKind.STAR -> drawStar(c,cx,cy,s*.34f,s*.15f)
                IconKind.APPS -> {
                    val edge=s*.30f; val boxSize=s*.24f
                    for (xx in listOf(-edge,edge-boxSize)) {
                        for (yy in listOf(-edge,edge-boxSize)) {
                            c.drawRoundRect(cx+xx,cy+yy,cx+xx+boxSize,cy+yy+boxSize,s*.04f,s*.04f,p)
                        }
                    }
                }''',"Native APP 2x2 icon")
u=one(u,"    private fun buildCredits() {", "        private data class AppCatalogEntry(val name: String, val packageId: String, val iconId: Int)

        private val appCatalogEntries: List<List<AppCatalogEntry>> = listOf(
            listOf(AppCatalogEntry("Prezzi Benzina!", "org.vernazza.androidfuel", R.drawable.app_catalog_prezzi_benzina)),
            listOf(AppCatalogEntry("Restaurant Guru", "restaurant.guru", R.drawable.app_catalog_restaurant_guru)),
            listOf(
                AppCatalogEntry("DMD2", "com.thorkracing.dmd2launcher", R.drawable.app_catalog_dmd2),
                AppCatalogEntry("Kurviger", "com.kurviger.app", R.drawable.app_catalog_kurviger)
            ),
            listOf(
                AppCatalogEntry("REVER", "com.reverllc.rever", R.drawable.app_catalog_rever),
                AppCatalogEntry("DIABLO Super Biker", "it.pirelli.diablosuperbiker", R.drawable.app_catalog_diablo)
            ),
            listOf(AppCatalogEntry("Meteo Aeronautica", "it.meteoam.app", R.drawable.app_catalog_meteo_am)),
            listOf(AppCatalogEntry("Luceverde", "it.aci.luceverde.client.mobileapp", R.drawable.app_catalog_luceverde)),
            listOf(
                AppCatalogEntry("112 Where ARE U", "it.Beta80Group.whereareu", R.drawable.app_catalog_where_are_u),
                AppCatalogEntry("Detecht", "se.app.detecht", R.drawable.app_catalog_detecht)
            ),
            listOf(AppCatalogEntry("Drivvo", "br.com.ctncardoso.ctncar", R.drawable.app_catalog_drivvo)),
            listOf(AppCatalogEntry("Biker Connect", "app.bikerconnect", R.drawable.app_catalog_biker_connect))
        )

        // Full native page: category -> its curated 1-2 apps -> real Play Store app details.
        // No remote HTML, no installers, no WebView, no added permissions.
        private fun buildAppCatalog() {
            bodyHost.addView(sectionTitle("APP"), lp(58f, 47f, 824f, 135f))
            val scroll = ScrollView(context).apply {
                fillViewport = false
                isVerticalScrollBarEnabled = true
                overScrollMode = View.OVER_SCROLL_IF_CONTENT_SCROLLS
            }
            val column = LinearLayout(context).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(pxX(2f), pxH(4f), pxX(2f), pxH(30f))
            }
            val selected = appCatalogCategoryIndex
            if (selected == null) {
                appCatalogEntries.forEachIndexed { index, apps ->
                    val category = MotoLinkLocale.appCatalogCategory(index)
                    val row = LinearLayout(context).apply {
                        orientation = LinearLayout.HORIZONTAL
                        gravity = Gravity.CENTER_VERTICAL
                        background = roundedBg(0xF509120D.toInt(), 0xFF385C42.toInt(), 25f, 1.2f)
                        setPadding(pxX(30f), 0, pxX(18f), 0)
                        isClickable = true
                        isFocusable = true
                        contentDescription = category
                        setOnClickListener {
                            appCatalogCategoryIndex = index
                            rebuild()
                        }
                    }
                    row.addView(text(category, 29f, Color.WHITE, true).apply {
                        gravity = Gravity.CENTER_VERTICAL
                        maxLines = 2
                        ellipsize = TextUtils.TruncateAt.END
                    }, LinearLayout.LayoutParams(0, LayoutParams.MATCH_PARENT, 1f))
                    row.addView(icon(IconKind.CHEVRON, GREEN), LinearLayout.LayoutParams(pxX(64f), pxH(64f)))
                    column.addView(row, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, pxH(145f)).apply {
                        bottomMargin = pxH(19f)
                    })
                }
            } else {
                val category = MotoLinkLocale.appCatalogCategory(selected)
                val backRow = LinearLayout(context).apply {
                    orientation = LinearLayout.HORIZONTAL
                    gravity = Gravity.CENTER_VERTICAL
                    setPadding(pxX(18f), 0, pxX(12f), 0)
                    background = roundedBg(0xF509120D.toInt(), 0xFF385C42.toInt(), 25f, 1.2f)
                    isClickable = true
                    isFocusable = true
                    setOnClickListener {
                        appCatalogCategoryIndex = null
                        rebuild()
                    }
                }
                backRow.addView(icon(IconKind.CHEVRON, GREEN), LinearLayout.LayoutParams(pxX(60f), pxH(60f)).apply {
                    rotation = 180f
                })
                backRow.addView(text(MotoLinkLocale.appCatalogBack(), 24f, GREEN, true).apply {
                    gravity = Gravity.CENTER_VERTICAL
                }, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f))
                column.addView(backRow, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, pxH(104f)).apply {
                    bottomMargin = pxH(30f)
                })
                column.addView(text(category, 33f, GREEN, true).apply {
                    gravity = Gravity.CENTER_VERTICAL
                }, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, pxH(90f)).apply {
                    bottomMargin = pxH(22f)
                })
                appCatalogEntries[selected].forEach { app ->
                    val appRow = LinearLayout(context).apply {
                        orientation = LinearLayout.HORIZONTAL
                        gravity = Gravity.CENTER_VERTICAL
                        setPadding(pxX(22f), 0, pxX(18f), 0)
                        background = roundedBg(0xF509120D.toInt(), 0xFF385C42.toInt(), 26f, 1.2f)
                        isClickable = true
                        isFocusable = true
                        contentDescription = app.name
                        setOnClickListener { onRecommendedAppClick?.invoke(app.packageId) }
                    }
                    appRow.addView(ImageView(context).apply {
                        setImageResource(app.iconId)
                        scaleType = ImageView.ScaleType.FIT_CENTER
                        contentDescription = app.name
                    }, LinearLayout.LayoutParams(pxX(104f), pxH(104f)).apply {
                        rightMargin = pxX(26f)
                    })
                    appRow.addView(text(app.name, 28f, Color.WHITE, true).apply {
                        gravity = Gravity.CENTER_VERTICAL
                        maxLines = 2
                        ellipsize = TextUtils.TruncateAt.END
                    }, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.MATCH_PARENT, 1f))
                    appRow.addView(icon(IconKind.CHEVRON, GREEN), LinearLayout.LayoutParams(pxX(54f), pxH(54f)))
                    column.addView(appRow, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, pxH(165f)).apply {
                        bottomMargin = pxH(24f)
                    })
                }
            }
            scroll.addView(column, ScrollView.LayoutParams(ScrollView.LayoutParams.MATCH_PARENT, ScrollView.LayoutParams.WRAP_CONTENT))
            bodyHost.addView(scroll, lp(58f, 210f, 824f, 1300f))
        }

\n    private fun buildCredits() {","Native catalog")
# The tour is contiguous and non-invasive: original FAQ and Privacy steps remain.
guide_steps='''        GuideStep(
            Page.APPS,
            title = MotoLinkLocale.appCatalogGuideTitle(true),
            body = MotoLinkLocale.appCatalogGuideBody(true),
            target = GuideTarget(58f, 210f, 824f, 145f)
        ),
        GuideStep(
            Page.APPS,
            title = MotoLinkLocale.appCatalogGuideTitle(false),
            body = MotoLinkLocale.appCatalogGuideBody(false),
            target = GuideTarget(58f, 445f, 824f, 165f)
        ),
'''
u=one(u,'''        GuideStep(
            Page.SETTINGS,
            title = "IMPOSTAZIONI · Modalità tasca",''', guide_steps+'''        GuideStep(
            Page.SETTINGS,
            title = "IMPOSTAZIONI · Modalità tasca",''',"guide APP after FAQ")
u=one(u,'''        if (step.page == Page.SUPPORT) supportTab = step.supportTab ?: SupportTab.LOG
        else supportTab = SupportTab.LOG
        rebuild()''','''        if (step.page == Page.SUPPORT) supportTab = step.supportTab ?: SupportTab.LOG
        else supportTab = SupportTab.LOG
        appCatalogCategoryIndex = if (step.page == Page.APPS && step.title == MotoLinkLocale.appCatalogGuideTitle(false)) 0 else null
        rebuild()''',"guide open first category")
u=one(u,'''        page = Page.HOME
        supportTab = SupportTab.LOG
        rebuild()''','''        page = Page.HOME
        supportTab = SupportTab.LOG
        appCatalogCategoryIndex = null
        rebuild()''',"finish guide")
u=one(u,'''        row.addView(text("''','''        row.addView(text("''',"noop placeholder") if False else u
m=main.read_text(encoding="utf-8")
m=one(m,"            onFaqClick = { openFaqPage() }","            onFaqClick = { openFaqPage() }\n            onRecommendedAppClick = { packageName -> openRecommendedPlayApp(packageName) }","Main callback")
m=one(m,"    private fun openFaqPage() {",'''    private fun openRecommendedPlayApp(packageName: String) {
        val allowed = setOf(
            "org.vernazza.androidfuel", "restaurant.guru",
            "com.thorkracing.dmd2launcher", "com.kurviger.app",
            "com.reverllc.rever", "it.pirelli.diablosuperbiker",
            "it.meteoam.app", "it.aci.luceverde.client.mobileapp",
            "it.Beta80Group.whereareu", "se.app.detecht",
            "br.com.ctncardoso.ctncar", "app.bikerconnect"
        )
        if (packageName !in allowed) return
        try {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=" + packageName)).apply {
                setPackage("com.android.vending")
            })
        } catch (_: Throwable) {
            try {
                startActivity(Intent(Intent.ACTION_VIEW,
                    Uri.parse("https://play.google.com/store/apps/details?id=" + packageName)))
            } catch (_: Throwable) {
                NeonDialogs.showInfo(this, "Google Play",
                    MotoLinkLocale.appCatalogStoreError())
            }
        }
    }

    private fun openFaqPage() {''',"Play store direct detail")
l=locale.read_text(encoding="utf-8")
locale_helpers="    fun appCatalogCategory(index: Int): String {
        val labels = when(language()) {
            "it" -> listOf("Stazioni di servizio", "Ristoranti", "Navigazione moto", "Tracciamento e prestazioni", "Meteo", "Viabilità", "Sicurezza", "Manutenzione moto", "Community e raduni")
            "ru" -> listOf("Заправочные станции", "Рестораны", "Мотонавигация", "Треки и показатели поездки", "Погода", "Дорожная обстановка", "Безопасность", "Обслуживание мотоцикла", "Мотосообщество и встречи")
            "zh" -> listOf("加油站", "餐厅", "摩托车导航", "骑行轨迹与性能", "天气", "道路与交通", "安全", "摩托车保养", "摩友社区与活动")
            else -> listOf("Fuel stations", "Restaurants", "Motorcycle navigation", "Ride tracking and performance", "Weather", "Traffic and roads", "Safety", "Motorcycle maintenance", "Rider community and events")
        }
        return labels.getOrElse(index) { "" }
    }

    fun appCatalogBack(): String = when(language()) {
        "it" -> "Indietro"
        "ru" -> "Назад"
        "zh" -> "返回"
        else -> "Back"
    }

    fun appCatalogStoreError(): String = when(language()) {
        "it" -> "Impossibile aprire Google Play. Verifica la connessione Internet."
        "ru" -> "Не удалось открыть Google Play. Проверьте подключение к Интернету."
        "zh" -> "无法打开 Google Play。请检查网络连接。"
        else -> "Unable to open Google Play. Check your Internet connection."
    }

    fun appCatalogGuideTitle(categories: Boolean): String = when(language()) {
        "it" -> if(categories) "APP · Categorie" else "APP · Applicazioni"
        "ru" -> if(categories) "ПРИЛОЖЕНИЯ · Категории" else "ПРИЛОЖЕНИЯ · Приложения"
        "zh" -> if(categories) "应用 · 分类" else "应用 · 推荐应用"
        else -> if(categories) "APPS · Categories" else "APPS · Applications"
    }

    fun appCatalogGuideBody(categories: Boolean): String = when(language()) {
        "it" -> if(categories) "Tocca APP nella barra inferiore. Scegli una categoria usando il pulsante con la freccia: stazioni di servizio, ristoranti, navigatori per moto e altre utilità. In ogni categoria trovi soltanto una o due app selezionate." else "Tocca il logo o il nome di un'app per aprire direttamente la sua scheda su Google Play. L'installazione è facoltativa e gestita da Google Play. Le funzioni a pagamento nelle app di terzi restano facoltative; le app non sono necessariamente compatibili con il TFT MotoLink."
        "ru" -> if(categories) "Нажмите APP на нижней панели. Откройте категорию с помощью стрелки: заправки, рестораны, мотонавигация и другие полезные инструменты. В каждой категории одно или два выбранных приложения." else "Нажмите логотип или название приложения, чтобы открыть его страницу в Google Play. Установка необязательна и выполняется через Google Play. Платные функции сторонних приложений необязательны; совместимость с экраном MotoLink не гарантируется."
        "zh" -> if(categories) "点击底部的 APP，使用分类右侧的箭头进入加油站、餐厅、摩托车导航及其他实用工具。每个分类仅推荐一到两个应用。" else "点击应用图标或名称，直接打开对应的 Google Play 页面。安装完全自愿，由 Google Play 管理。第三方应用的付费功能为可选项目；不代表已通过 MotoLink 车机屏幕兼容性测试。"
        else -> if(categories) "Tap APP in the bottom bar. Open a category with its arrow to find fuel stations, restaurants, motorcycle navigation and other useful tools. Each category contains only one or two carefully selected apps." else "Tap an app logo or name to open its Google Play listing directly. Installation is optional and handled by Google Play. Optional premium features belong to third-party apps; MotoLink TFT compatibility is not implied."
    }

"
l=one(l,'    fun releaseNotes182(): String = when (language()) {',
          locale_helpers+'    fun releaseNotes182(): String = when (language()) {',"Locale 4 languages")
b=gradle.read_text(encoding="utf-8")
b=one(b,"versionCode = 38","versionCode = 39","v39")
b=one(b,'versionName = "1.8.2-faq-guide-test"','versionName = "1.8.2-app-catalog-test"',"v39 name")
assert "Page.APPS" in u and "appCatalogCategoryIndex" in u
assert "onRecommendedPlayApp" not in m and "openRecommendedPlayApp" in m
assert all(x in l for x in ['"it"','"ru"','"zh"'])
ui.write_text(u,encoding="utf-8")
main.write_text(m,encoding="utf-8")
locale.write_text(l,encoding="utf-8")
gradle.write_text(b,encoding="utf-8")
print("V39_PATCH_PASS native categories 9, apps 12, IT/EN/RU/ZH guide 2 steps, Play only")
