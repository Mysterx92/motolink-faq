package it.motolink.app

/**
 * Fixed, curated third-party Play Store directory for the isolated TEST build.
 * No referral links, payments, tracking, app installation or background requests.
 * Availability, prices and premium features remain governed by third parties.
 */
object MotoLinkRecommendedApps {
    data class L(val it: String, val en: String, val ru: String, val zh: String) {
        fun get(lang: String): String = when (lang) {
            "it" -> it
            "ru" -> ru
            "zh" -> zh
            else -> en
        }
    }
    data class App(val title: String, val packageId: String, val logoKey: String)
    data class Category(val id: String, val title: L, val apps: List<App>)

    val categories = listOf(
        Category("fuel", L("Stazioni di servizio", "Fuel stations", "Заправочные станции", "加油站"), listOf(
            App("Prezzi Benzina!", "org.vernazza.androidfuel", "prezzi_benzina")
        )),
        Category("restaurants", L("Ristoranti", "Restaurants", "Рестораны", "餐厅"), listOf(
            App("Restaurant Guru", "restaurant.guru", "restaurant_guru")
        )),
        Category("navigation", L("Navigazione moto", "Motorcycle navigation", "Мотонавигация", "摩托车导航"), listOf(
            App("DMD2", "com.thorkracing.dmd2launcher", "dmd2"),
            App("Kurviger", "com.kurviger.app", "kurviger")
        )),
        Category("tracks", L("Tracce e prestazioni", "Ride tracking", "Треки и показатели", "骑行轨迹与数据"), listOf(
            App("REVER", "com.reverllc.rever", "rever"),
            App("DIABLO Super Biker", "it.pirelli.diablosuperbiker", "diablo")
        )),
        Category("weather", L("Meteo", "Weather", "Погода", "天气"), listOf(
            App("Meteo Aeronautica", "it.meteoam.app", "meteoam")
        )),
        Category("traffic", L("Viabilità", "Road conditions", "Дорожная обстановка", "道路交通"), listOf(
            App("Luceverde", "it.aci.luceverde.client.mobileapp", "luceverde")
        )),
        Category("safety", L("Sicurezza ed emergenze", "Safety and emergencies", "Безопасность и помощь", "安全与紧急服务"), listOf(
            App("112 Where ARE U", "it.Beta80Group.whereareu", "whereareu"),
            App("Detecht", "se.app.detecht", "detecht")
        )),
        Category("maintenance", L("Manutenzione moto", "Motorcycle maintenance", "Обслуживание мотоцикла", "摩托车保养"), listOf(
            App("Drivvo", "br.com.ctncardoso.ctncar", "drivvo")
        )),
        Category("community", L("Community e raduni", "Community and rides", "Сообщество и встречи", "骑友社区"), listOf(
            App("Biker Connect", "app.bikerconnect", "bikerconnect")
        ))
    )
    fun isApprovedPackage(id: String): Boolean =
        categories.any { c -> c.apps.any { it.packageId == id } }

    fun uiText(lang: String, key: String): String = when (key) {
        "title" -> L("App consigliate", "Recommended apps", "Рекомендуемые приложения", "推荐应用").get(lang)
        "subtitle" -> L("Scopri app utili per i tuoi viaggi in moto", "Discover useful apps for motorcycle rides", "Полезные приложения для мотопоездок", "发现适合摩托旅行的实用应用").get(lang)
        "back" -> L("INDIETRO", "BACK", "НАЗАД", "返回").get(lang)
        "disclaimer" -> L("App di terze parti. Nessuna affiliazione o compatibilità MotoLink garantita.", "Third-party apps. No affiliation or MotoLink compatibility guaranteed.", "Сторонние приложения. Нет гарантии совместимости или связи с MotoLink.", "第三方应用。MotoLink 不保证兼容性，也不表示与开发商有关联。").get(lang)
        "store" -> L("Apri scheda Google Play", "Open Google Play listing", "Открыть страницу Google Play", "打开 Google Play 页面").get(lang)
        "guideCatsTitle" -> L("APP · Categorie", "APPS · Categories", "ПРИЛОЖЕНИЯ · Категории", "应用 · 分类").get(lang)
        "guideCats" -> L(
            "Nella barra inferiore tocca APP. Troverai le categorie, come Stazioni di servizio, Ristoranti, Navigazione moto, Meteo e Sicurezza. Tocca una categoria con la freccia per vedere le app consigliate.",
            "Tap APP in the bottom bar. Browse categories such as Fuel stations, Restaurants, Motorcycle navigation, Weather and Safety. Tap a category with an arrow to see the recommended apps.",
            "Нажмите APP в нижней панели. Откройте категорию, например заправки, рестораны, мотонавигация, погода или безопасность, нажав строку со стрелкой.",
            "点击底部的 APP。这里按加油站、餐厅、摩托车导航、天气和安全等分类。点击带箭头的分类进入推荐应用列表。"
        ).get(lang)
        "guideDetailTitle" -> L("APP · Apri Google Play", "APPS · Open Google Play", "ПРИЛОЖЕНИЯ · Google Play", "应用 · 打开 Google Play").get(lang)
        "guideDetail" -> L(
            "Dentro ogni categoria trovi 1 o 2 applicazioni selezionate, con logo e nome. Tocca una app per aprire direttamente la sua scheda Google Play. MotoLink non installa niente automaticamente. Alcune app hanno funzioni Premium facoltative; controlla condizioni e compatibilità prima dell'uso.",
            "Each category contains 1 or 2 selected apps, with icon and name. Tap an app to open its Google Play listing directly. MotoLink never installs apps automatically. Some apps offer optional paid features; check terms and compatibility before use.",
            "В каждой категории 1–2 приложения с логотипом и названием. Нажмите приложение, чтобы открыть его страницу в Google Play. MotoLink ничего не устанавливает автоматически. Некоторые функции могут быть платными; проверьте условия и совместимость.",
            "每个分类列出 1–2 款应用，包括图标和名称。点击即可直接打开 Google Play 应用详情。MotoLink 不会自动安装应用。部分高级功能可能收费，请自行检查条款与兼容性。"
        ).get(lang)
        else -> key
    }
}
