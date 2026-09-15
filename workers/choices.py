PROVINCE_CHOICES = [
    ("Central", "Central"),
    ("Copperbelt", "Copperbelt"),
    ("Eastern", "Eastern"),
    ("Luapula", "Luapula"),
    ("Lusaka", "Lusaka"),
    ("Muchinga", "Muchinga"),
    ("Northern", "Northern"),
    ("North-Western", "North-Western"),
    ("Southern", "Southern"),
    ("Western", "Western"),
]

PROVINCE_DISTRICTS = {
    "Central": [
        "Chibombo",
        "Chisamba",
        "Chitambo",
        "Itezhi-Tezhi",
        "Kabwe",
        "Kapiri Mposhi",
        "Luano",
        "Mkushi",
        "Mumbwa",
        "Ngabwe",
        "Serenje",
        "Shibuyunji",
    ],
    "Copperbelt": [
        "Chililabombwe",
        "Chingola",
        "Kalulushi",
        "Kitwe",
        "Luanshya",
        "Lufwanyama",
        "Masaiti",
        "Mpongwe",
        "Mufulira",
        "Ndola",
    ],
    "Eastern": [
        "Chadiza",
        "Chasefu",
        "Chipangali",
        "Chipata",
        "Kasenengwa",
        "Katete",
        "Lumezi",
        "Lundazi",
        "Lusangazi",
        "Mambwe",
        "Nyimba",
        "Petauke",
        "Sinda",
        "Vubwi",
    ],
    "Luapula": [
        "Chembe",
        "Chiengi",
        "Chifunabuli",
        "Chipili",
        "Kawambwa",
        "Lunga",
        "Mansa",
        "Milenge",
        "Mwansabombwe",
        "Mwense",
        "Nchelenge",
        "Samfya",
    ],
    "Lusaka": [
        "Chilanga",
        "Chirundu",
        "Chongwe",
        "Kafue",
        "Luangwa",
        "Lusaka",
        "Rufunsa",
    ],
    "Muchinga": [
        "Chama",
        "Chinsali",
        "Isoka",
        "Kanchibiya",
        "Lavushimanda",
        "Mafinga",
        "Mpika",
        "Nakonde",
        "Shiwang'andu",
    ],
    "Northern": [
        "Chilubi",
        "Kaputa",
        "Kasama",
        "Lunte",
        "Lupososhi",
        "Luwingu",
        "Mbala",
        "Mporokoso",
        "Mpulungu",
        "Mungwi",
        "Nsama",
        "Senga Hill",
    ],
    "North-Western": [
        "Chavuma",
        "Ikelenge",
        "Kabompo",
        "Kalumbila",
        "Kasempa",
        "Manyinga",
        "Mufumbwe",
        "Mushindamo",
        "Mwinilunga",
        "Solwezi",
        "Zambezi",
    ],
    "Southern": [
        "Chikankata",
        "Choma",
        "Gwembe",
        "Kalomo",
        "Kazungula",
        "Livingstone",
        "Mazabuka",
        "Monze",
        "Namwala",
        "Pemba",
        "Siavonga",
        "Sinazongwe",
        "Zimba",
    ],
    "Western": [
        "Kalabo",
        "Kaoma",
        "Limulunga",
        "Luampa",
        "Lukulu",
        "Mitete",
        "Mongu",
        "Mulobezi",
        "Mwandi",
        "Nalolo",
        "Nkeyema",
        "Senanga",
        "Sesheke",
        "Shangombo",
        "Sikongo",
        "Sioma",
    ],
}

DISTRICT_CHOICES = [
    (district, district)
    for province, _label in PROVINCE_CHOICES
    for district in PROVINCE_DISTRICTS[province]
]

GROUPED_DISTRICT_CHOICES = [
    (province, [(district, district) for district in PROVINCE_DISTRICTS[province]])
    for province, _label in PROVINCE_CHOICES
]

GENDER_CHOICES = [
    ("female", "Female"),
    ("male", "Male"),
    ("non_binary", "Non-binary"),
    ("prefer_not_to_say", "Prefer not to say"),
]

EMPLOYMENT_STATUS_CHOICES = [
    ("formal", "Formal employment"),
    ("informal", "Informal employment"),
    ("self_employed", "Self-employed"),
    ("apprenticeship", "Apprenticeship"),
    ("unemployed", "Unemployed"),
    ("retired", "Retired"),
]

SECTOR_CHOICES = [
    ("agriculture", "Agriculture"),
    ("mining", "Mining"),
    ("manufacturing", "Manufacturing"),
    ("construction", "Construction"),
    ("transport", "Transport"),
    ("education", "Education"),
    ("health", "Health"),
    ("hospitality", "Hospitality"),
    ("public_service", "Public service"),
    ("commerce", "Commerce"),
    ("domestic_work", "Domestic work"),
    ("other", "Other"),
]

UNION_MEMBERSHIP_CHOICES = [
    ("member", "Union member"),
    ("not_member", "Not a union member"),
    ("unknown", "Unknown"),
]

DISABILITY_TYPE_CHOICES = [
    ("physical", "Physical impairment"),
    ("visual", "Visual impairment"),
    ("hearing", "Hearing impairment"),
    ("intellectual", "Intellectual disability"),
    ("psychosocial", "Psychosocial disability"),
    ("albinism", "Albinism"),
    ("multiple", "Multiple disabilities"),
    ("other", "Other"),
]

SEVERITY_CHOICES = [
    ("mild", "Mild"),
    ("moderate", "Moderate"),
    ("severe", "Severe"),
    ("profound", "Profound"),
]

WASHINGTON_GROUP_CHOICES = [
    (0, "No difficulty"),
    (1, "Some difficulty"),
    (2, "A lot of difficulty"),
    (3, "Cannot do at all"),
]

ACCESSIBILITY_STATUS_CHOICES = [
    ("accessible", "Accessible"),
    ("partially_accessible", "Partially accessible"),
    ("not_accessible", "Not accessible"),
    ("not_assessed", "Not yet assessed"),
]

COMMON_UNIONS = [
    "ZCTU",
    "MUZ",
    "BETUZ",
    "NUPSW",
    "ZUFIAW",
    "ZULAWU",
    "NAQEZ",
    "SESTUZ",
    "ZRAWU",
]
