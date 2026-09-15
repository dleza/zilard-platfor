"""Seed the public website with ZILARD's own documented content.

Sourced from the ZILARD Company Profile (institutional overview, thematic
areas, research portfolio, team) plus the three publicly-hosted reports
identified in prior research (FES, SASK). Everything here is meant as a
verified starting point that ZILARD's content owner can edit through the
Django admin -- not a final, un-editable copy.

Safe to re-run: uses get_or_create/update on slugs, so it will not create
duplicates.
"""
from datetime import date

from django.core.management.base import BaseCommand

from website.models import (
    HomeSlide,
    NewsArticle,
    Partner,
    Publication,
    ResearchActivity,
    SiteSetting,
    TeamMember,
    ThematicArea,
)

THEMES = [
    {
        "slug": "labour-market-research-and-analysis",
        "title": "Labour Market Research and Analysis",
        "summary": "Employment dynamics, productivity, wages, and skills across Zambia's formal and informal sectors.",
        "body": (
            "This theme covers employment dynamics in both the formal and informal sectors, labour "
            "productivity and enterprise competitiveness, wage trends and income inequality, and "
            "skills development and labour-force transitions. It draws on ZILARD's baseline and "
            "sector studies of Zambia's labour market."
        ),
        "order": 1,
    },
    {
        "slug": "trade-union-support-and-organising-strategies",
        "title": "Trade Union Support and Organising Strategies",
        "summary": "Power-resource mapping, union capacity building, and organising precarious and informal workers.",
        "body": (
            "This theme covers power-resource mapping and union capacity development, organising "
            "precarious and informal workers, gender equality in collective bargaining, and worker "
            "education and rights awareness. It underpins tools such as ZILARD's shop-steward "
            "organising manual."
        ),
        "order": 2,
    },
    {
        "slug": "labour-policy-and-institutional-development",
        "title": "Labour Policy and Institutional Development",
        "summary": "Technical input into labour legislation, social dialogue mechanisms, and sectoral bargaining.",
        "body": (
            "This theme covers technical inputs into labour legislation and regulations, "
            "public-private-social dialogue mechanisms, labour inspection and enforcement systems, "
            "and support to sectoral bargaining structures."
        ),
        "order": 3,
    },
    {
        "slug": "youth-employment-gender-and-informality",
        "title": "Youth Employment, Gender, and Informality",
        "summary": "Youth transitions, gender gaps in employment, and strategies for formalising informal work.",
        "body": (
            "This theme covers research on the future of work and youth transitions, gender gaps in "
            "employment, pay and access to leadership, and strategies for formalising informal work "
            "and protecting informal workers. Disability-inclusive employment and social protection "
            "for informal workers are researched within this and related themes."
        ),
        "order": 4,
    },
]

RESEARCH_ACTIVITIES = [
    {
        "slug": "zctu-affiliate-membership-data-2018",
        "title": "Disaggregation of Data by Age and Sex of All ZCTU Affiliates",
        "year": 2018,
        "status": "completed",
        "purpose": (
            "Analysed membership demographics across all ZCTU affiliates to inform targeted labour "
            "policies and promote inclusive representation."
        ),
        "funder_collaborators": "Funded by the Zambia Congress of Trade Unions (ZCTU)",
        "theme": "labour-market-research-and-analysis",
        "available_outputs": "Summary only",
    },
    {
        "slug": "minimum-wage-study-domestic-workers-2019",
        "title": "Study on the Minimum Wage",
        "year": 2019,
        "status": "completed",
        "purpose": (
            "Examined the impact of minimum-wage legislation on domestic workers in Zambia, "
            "highlighting challenges in enforcement and compliance within the informal sector."
        ),
        "funder_collaborators": "Funded by the Zambia Congress of Trade Unions (ZCTU)",
        "theme": "labour-policy-and-institutional-development",
        "available_outputs": "Summary only",
    },
    {
        "slug": "informal-economy-baseline-2020",
        "title": "Baseline Study to Map Existing Informal Economy Structures in Zambia and their Specific Needs",
        "year": 2020,
        "status": "completed",
        "purpose": (
            "Identified key stakeholders and assessed social-protection mechanisms for informal "
            "workers across five provinces, revealing a significant informal sector characterised "
            "by a weak regulatory framework."
        ),
        "geographic_coverage": "Five provinces of Zambia",
        "funder_collaborators": "Funded by the Friedrich-Ebert-Stiftung (FES)",
        "theme": "youth-employment-gender-and-informality",
        "available_outputs": "Full report",
    },
    {
        "slug": "trade-unions-and-trade-2021",
        "title": "Trade Unions and Trade",
        "year": 2021,
        "status": "completed",
        "purpose": (
            "Examined continental free-trade agreements and informal employment in Zambia's "
            "manufacturing sector -- informal workers' participation, representation, access to "
            "finance, labour rights, and social protection in the context of trade integration."
        ),
        "funder_collaborators": "Prepared with ITUC-Africa cooperation and SASK support",
        "theme": "labour-market-research-and-analysis",
        "available_outputs": "Full report",
    },
    {
        "slug": "disability-rights-working-life-2022",
        "title": "Study on Rights of Persons with Disabilities in Working Life in Zambia",
        "year": 2022,
        "status": "completed",
        "purpose": (
            "Researched employment barriers, discrimination, workplace accessibility, career "
            "development, and trade-union representation for persons with disabilities, to promote "
            "inclusive employment practices."
        ),
        "funder_collaborators": "Funded by the Trade Union Solidarity Centre of Finland (SASK), with member unions JHL and OAJ",
        "theme": "youth-employment-gender-and-informality",
        "available_outputs": "Full report",
    },
    {
        "slug": "chinese-investment-working-conditions-2023",
        "title": "Study on Chinese Investment and Working Conditions",
        "year": 2023,
        "status": "completed",
        "purpose": (
            "Examined labour practices within Chinese-run enterprises in Zambia, highlighting poor "
            "health and safety standards and excessive working hours."
        ),
        "funder_collaborators": "Funded by the Solidarity Centre",
        "theme": "labour-policy-and-institutional-development",
        "available_outputs": "Summary only",
    },
    {
        "slug": "belt-and-road-workers-rights-2024",
        "title": "Advancing Workers' Rights on China's Belt and Road Initiative in Zambia",
        "year": 2024,
        "status": "completed",
        "purpose": (
            "Explored the implications of Chinese investment under the Belt and Road Initiative for "
            "labour rights in Zambia, addressing concerns about working conditions and labour "
            "standards."
        ),
        "funder_collaborators": "Funded by the Solidarity Centre",
        "theme": "labour-policy-and-institutional-development",
        "available_outputs": "Summary only",
    },
    {
        "slug": "rural-sugar-plantation-workers-2024",
        "title": "Organizing Workers in the Rural Economy and Plantations in Zambia: A Focus on Sugar Plantations",
        "year": 2024,
        "status": "completed",
        "purpose": (
            "Aimed to improve labour conditions and organisation among workers in Zambia's rural "
            "sugar plantations, contributing to efforts to enhance living standards in rural areas."
        ),
        "funder_collaborators": "Funded by the International Labour Organization (ILO)",
        "theme": "trade-union-support-and-organising-strategies",
        "available_outputs": "Summary only",
    },
    {
        "slug": "shop-steward-organizing-tool-2025",
        "title": "Development of the Shop Steward Organizing Tool",
        "year": 2025,
        "status": "completed",
        "purpose": (
            "Developed a shop-steward organising manual to strengthen worker representation and "
            "workplace organising -- equipping shop stewards with practical guidance, strategies, "
            "and resources to mobilise workers, address labour grievances, and promote workers' "
            "rights within workplaces and trade unions."
        ),
        "funder_collaborators": "Funded by the Solidarity Centre",
        "theme": "trade-union-support-and-organising-strategies",
        "available_outputs": "Manual (pending release)",
    },
    {
        "slug": "lobito-corridor-assessment-2026",
        "title": "Assessment of Labour Rights, Occupational Health and Safety, and Environmental Impacts along the Lobito Corridor",
        "year": 2026,
        "status": "ongoing",
        "purpose": (
            "Assessing the extent to which workers' rights are protected along the Lobito Corridor "
            "(Angola, Zambia, DRC) -- compliance with labour laws, working conditions, wages, "
            "freedom of association, and social protection in sectors linked to transport, mining, "
            "and infrastructure development."
        ),
        "geographic_coverage": "Angola, Zambia, and the Democratic Republic of Congo",
        "funder_collaborators": "Funded by the Southern African Trade Union Coordination Council (SATUCC)",
        "theme": "labour-policy-and-institutional-development",
        "available_outputs": "Status to be confirmed",
    },
]

PUBLICATIONS = [
    {
        "slug": "rights-based-social-protection-in-africa-2020",
        "title": "Rights-Based Social Protection in Africa: Zambia Baseline Study",
        "authors": "Trywell Kalusopa, Grayson Koyi, Francis J. Phiri",
        "publication_date": date(2020, 1, 1),
        "publication_type": "report",
        "theme": "youth-employment-gender-and-informality",
        "research_activity": "informal-economy-baseline-2020",
        "summary": (
            "A baseline study mapping existing informal-economy structures in Zambia and assessing "
            "their specific needs, including social-protection options for informal workers such as "
            "market traders."
        ),
        "external_url": "",
        "acknowledgements": "Hosted by the Friedrich-Ebert-Stiftung (FES). ZILARD Secretariat.",
        "is_featured": True,
    },
    {
        "slug": "trade-unions-and-trade-report-2021",
        "title": "Trade Unions and Trade",
        "authors": "ZILARD Secretariat",
        "publication_date": date(2021, 11, 1),
        "publication_type": "report",
        "theme": "labour-market-research-and-analysis",
        "research_activity": "trade-unions-and-trade-2021",
        "summary": (
            "Research examining continental free-trade agreements and informal employment in "
            "Zambia's manufacturing sector, focusing on informal workers' participation, "
            "representation, access to finance, labour rights, and social protection."
        ),
        "external_url": "",
        "acknowledgements": "Prepared with ITUC-Africa cooperation and SASK support. A related summary was published 29 March 2022.",
        "is_featured": True,
    },
    {
        "slug": "disability-rights-working-life-report-2023",
        "title": "Study on Rights of Persons with Disabilities in Working Life in Zambia",
        "authors": "Trywell Kalusopa, Stanley Zulu Jr, Francis Jaman Phiri",
        "publication_date": date(2023, 3, 29),
        "publication_type": "report",
        "theme": "youth-employment-gender-and-informality",
        "research_activity": "disability-rights-working-life-2022",
        "summary": (
            "Research on employment barriers, discrimination, workplace accessibility, career "
            "development, and trade-union representation for persons with disabilities in Zambia, "
            "informing a pilot initiative on disability-inclusive working life."
        ),
        "external_url": "",
        "acknowledgements": "Hosted by SASK. Commissioned with SASK member unions JHL and OAJ.",
        "is_featured": True,
    },
]

NEWS_ARTICLES = [
    {
        "slug": "chongwe-municipal-council-disability-inclusion-2024",
        "title": "Chongwe Municipal Council engages ZILARD on workplace accessibility",
        "category": "media",
        "published_date": date(2024, 10, 21),
        "location": "Chongwe, Zambia",
        "source_name": "Chongwe Municipal Council",
        "summary": (
            "Chongwe Municipal Council reported a visit by ZILARD concerning disability inclusion "
            "and workplace accessibility, covering ramps, toilets, transport, communication, and "
            "inclusive attitudes towards workers with disabilities."
        ),
        "theme": "youth-employment-gender-and-informality",
    },
    {
        "slug": "sask-zilard-programme-2026-2029",
        "title": "SASK-supported programme (2026-2029) launched with ZILARD",
        "category": "media",
        "published_date": date(2026, 1, 1),
        "source_name": "Zambia News and Information Services (ZANIS)",
        "summary": (
            "ZANIS reported the launch of a Trade Union Solidarity Centre of Finland (SASK) "
            "programme for 2026-2029, focused on strengthening workers' rights, disability "
            "inclusion, workplace safety, and decent employment, with support from the Government "
            "of Finland."
        ),
        "theme": "trade-union-support-and-organising-strategies",
    },
]

HOME_SLIDES = [
    {
        "title": "Evidence for Decent Work and Inclusive Development",
        "caption": "Explore ZILARD's research across labour markets, trade unions, policy, and youth employment.",
        "link_url": "/our-work/",
        "order": 1,
    },
    {
        "title": "Nine research activities since 2018",
        "caption": "From ZCTU affiliate data to the Lobito Corridor assessment -- browse the research portfolio.",
        "link_url": "/research/",
        "order": 2,
    },
    {
        "news_article_slug": "sask-zilard-programme-2026-2029",
        "order": 3,
    },
    {
        "title": "Prof. Trywell Kalusopa",
        "caption": "Executive Director -- founding and current head of ZILARD, based at the University of Zambia.",
        "photo_path": "team/trywell-kalusopa.jpg",
        "link_url": "/about/",
        "order": 4,
    },
    {
        "title": "Francis Jamani Phiri",
        "caption": "Programmes and Communications Manager -- leads communication strategy, research, and programme implementation.",
        "photo_path": "team/francis-phiri.jpg",
        "link_url": "/about/",
        "order": 5,
    },
    {
        "title": "Stanley Zulu",
        "caption": "Labour Economist -- report writing, policy analysis, and policy briefs.",
        "photo_path": "team/stanley-zulu.jpg",
        "link_url": "/about/",
        "order": 6,
    },
    {
        "title": "Mercy Mwale",
        "caption": "Research Administrative Manager -- manages research administration and organisational affairs.",
        "photo_path": "team/mercy-mwale.jpg",
        "link_url": "/about/",
        "order": 7,
    },
]

TEAM_MEMBERS = [
    {
        "full_name": "Prof. Trywell Kalusopa",
        "position": "Executive Director",
        "group": "management",
        "order": 1,
        "photo": "team/trywell-kalusopa.jpg",
        "bio": (
            "Professor Trywell Kalusopa is a distinguished labour and employment scholar, academic, "
            "and researcher based in Zambia. He is the founding and current Executive Director of "
            "ZILARD and serves at the University of Zambia. He has previously held academic and "
            "professional positions at the University of Botswana, University of Zululand (South "
            "Africa), and the Southern African Trade Union Co-ordination Council (SATUCC). He holds "
            "a PhD from the University of South Africa (UNISA), specialising in labour market "
            "information support systems, and has authored and edited numerous research articles, "
            "technical reports, and book chapters on labour and employment in Africa."
        ),
    },
    {
        "full_name": "Francis Jamani Phiri",
        "position": "Programmes and Communications Manager",
        "group": "management",
        "order": 2,
        "photo": "team/francis-phiri.jpg",
        "bio": (
            "Mr. Phiri is a development communication and research professional with over eight "
            "years of experience in research, programme management, communication, and policy "
            "analysis. He holds a Master of Communication for Development (MCD) and contributes to "
            "labour research, workers' education and training, advocacy, and programme "
            "implementation, working closely with trade unions, government institutions, the media, "
            "and other labour-focused organisations."
        ),
    },
    {
        "full_name": "Stanley Zulu",
        "position": "Labour Economist",
        "group": "staff",
        "order": 3,
        "photo": "team/stanley-zulu.jpg",
        "bio": (
            "Mr. Zulu holds a Master's Degree in Economics and Finance from the University of Lusaka "
            "and an Honours Degree in Economics from the University of Namibia, and is currently "
            "pursuing a second Master's degree at the University of the Witwatersrand, South Africa. "
            "He brings report writing, policy analysis, and policy-brief expertise to ZILARD."
        ),
    },
    {
        "full_name": "Mercy Mwale",
        "position": "Research Administrative Manager",
        "group": "staff",
        "order": 4,
        "photo": "team/mercy-mwale.jpg",
        "bio": (
            "Ms. Mwale holds a Master of Arts in Public Administration and a Bachelor's Degree in "
            "Mass Communication, both from the University of Zambia. With three years of "
            "administration experience, she manages the research administration and organisational "
            "affairs of ZILARD."
        ),
    },
]

PARTNERS = [
    {
        "name": "University of Zambia (Department of Economics & Institute of Economic and Social Research)",
        "relationship": "Institutional partnership supporting ZILARD's research capacity and academic affiliation.",
        "order": 1,
    },
    {
        "name": "Zambia Statistics Agency (ZamStats)",
        "relationship": "Data alignment and methodology coordination.",
        "order": 2,
    },
    {
        "name": "Zambia Congress of Trade Unions (ZCTU)",
        "relationship": "Institutional partnership; funded ZILARD's 2018 affiliate membership study and 2019 minimum-wage study.",
        "order": 3,
    },
    {
        "name": "Zambia Federation of Employers (ZFE)",
        "relationship": "Institutional partnership.",
        "order": 4,
    },
    {
        "name": "Friedrich-Ebert-Stiftung (FES)",
        "relationship": "Funded and hosted the 2020 informal-economy baseline study.",
        "related_publication": "rights-based-social-protection-in-africa-2020",
        "period": "2020",
        "order": 5,
    },
    {
        "name": "Trade Union Solidarity Centre of Finland (SASK)",
        "relationship": "Supported the 2021 trade-union research and commissioned the 2022-2023 disability-inclusion study.",
        "related_publication": "disability-rights-working-life-report-2023",
        "period": "2021-2023",
        "order": 6,
    },
    {
        "name": "ITUC-Africa",
        "relationship": "Cooperation on the 2021 Trade Unions and Trade research.",
        "related_publication": "trade-unions-and-trade-report-2021",
        "period": "2021",
        "order": 7,
    },
    {
        "name": "Solidarity Centre",
        "relationship": "Funded the 2023-2025 studies on Chinese investment, the Belt and Road Initiative, and the shop-steward organising tool.",
        "period": "2023-2025",
        "order": 8,
    },
    {
        "name": "International Labour Organization (ILO)",
        "relationship": "Funded the 2024 rural sugar-plantation workers study.",
        "period": "2024",
        "order": 9,
    },
    {
        "name": "Southern African Trade Union Coordination Council (SATUCC)",
        "relationship": "Funding the 2026 Lobito Corridor labour-rights assessment.",
        "period": "2026",
        "order": 10,
    },
]


class Command(BaseCommand):
    help = "Seed the public website with ZILARD's documented institutional content."

    def handle(self, *args, **options):
        theme_by_slug = {}
        for data in THEMES:
            theme, created = ThematicArea.objects.update_or_create(
                slug=data["slug"], defaults={k: v for k, v in data.items() if k != "slug"}
            )
            theme_by_slug[data["slug"]] = theme
            self.stdout.write(("Created" if created else "Updated") + f" theme: {theme.title}")

        activity_by_slug = {}
        for data in RESEARCH_ACTIVITIES:
            payload = {k: v for k, v in data.items() if k not in {"slug", "theme"}}
            payload["theme"] = theme_by_slug.get(data.get("theme"))
            activity, created = ResearchActivity.objects.update_or_create(
                slug=data["slug"], defaults=payload
            )
            activity_by_slug[data["slug"]] = activity
            self.stdout.write(("Created" if created else "Updated") + f" research activity: {activity.title}")

        for data in PUBLICATIONS:
            payload = {k: v for k, v in data.items() if k not in {"slug", "theme", "research_activity"}}
            payload["theme"] = theme_by_slug.get(data.get("theme"))
            payload["research_activity"] = activity_by_slug.get(data.get("research_activity"))
            pub, created = Publication.objects.update_or_create(slug=data["slug"], defaults=payload)
            self.stdout.write(("Created" if created else "Updated") + f" publication: {pub.title}")

        for data in NEWS_ARTICLES:
            payload = {k: v for k, v in data.items() if k not in {"slug", "theme"}}
            payload["theme"] = theme_by_slug.get(data.get("theme"))
            article, created = NewsArticle.objects.update_or_create(slug=data["slug"], defaults=payload)
            self.stdout.write(("Created" if created else "Updated") + f" news article: {article.title}")

        for data in HOME_SLIDES:
            payload = {k: v for k, v in data.items() if k not in {"news_article_slug", "photo_path"}}
            article_slug = data.get("news_article_slug")
            payload["news_article"] = NewsArticle.objects.filter(slug=article_slug).first() if article_slug else None
            slide, created = HomeSlide.objects.update_or_create(order=data["order"], defaults=payload)
            photo_path = data.get("photo_path")
            if photo_path and not slide.image:
                slide.image.name = photo_path
                slide.save(update_fields=["image"])
            self.stdout.write(("Created" if created else "Updated") + f" home slide: {slide.display_title}")

        for data in TEAM_MEMBERS:
            payload = {k: v for k, v in data.items() if k != "photo"}
            member, created = TeamMember.objects.update_or_create(
                full_name=data["full_name"], defaults=payload
            )
            if data.get("photo") and not member.photo:
                member.photo.name = data["photo"]
                member.save(update_fields=["photo"])
            self.stdout.write(("Created" if created else "Updated") + f" team member: {member.full_name}")

        for data in PARTNERS:
            payload = {k: v for k, v in data.items() if k not in {"name", "related_publication"}}
            pub_slug = data.get("related_publication")
            payload["related_publication"] = (
                Publication.objects.filter(slug=pub_slug).first() if pub_slug else None
            )
            partner, created = Partner.objects.update_or_create(name=data["name"], defaults=payload)
            self.stdout.write(("Created" if created else "Updated") + f" partner: {partner.name}")

        settings_obj = SiteSetting.load()
        if not settings_obj.office_address:
            settings_obj.office_address = "Plot 260, Twin Palm Road, Ibex Hill, Lusaka, Zambia"
            settings_obj.phone = "+260 211 269 783"
            settings_obj.mobile = "+260 977 704 973"
            settings_obj.save()
            self.stdout.write("Set default site contact details (please verify and update in the admin).")

        self.stdout.write(self.style.SUCCESS("Website content seeded."))
