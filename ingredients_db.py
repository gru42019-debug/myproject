import re

# ДВУЕЗИЧНА БАЗА ДАННИ СЪС СТРАНИЧНИ ЕФЕКТИ
HAZARDOUS_INGREDIENTS = {
    "E102": {
        "Български": "Тартразин. Странични ефекти: Предизвиква хиперактивност при деца, кожни обриви и астматични симптоми.",
        "English": "Tartrazine. Side effects: Triggers hyperactivity in children, skin rashes, and asthma symptoms."
    },
    "E110": {
        "Български": "Сънсет жълто. Странични ефекти: Алергични реакции, стомашни неразположения и хиперактивност при деца.",
        "English": "Sunset Yellow. Side effects: Allergic reactions, gastric upset, and hyperactivity in children."
    },
    "E122": {
        "Български": "Азорубин. Странични ефекти: Силен алерген. Може да причини кожни реакции при чувствителност към аспирин.",
        "English": "Azorubine. Side effects: Strong allergen. Can cause skin reactions in people sensitive to aspirin."
    },
    "E124": {
        "Български": "Понсо 4R. Странични ефекти: Потенциален канцероген; засилва симптомите на астма и алергии.",
        "English": "Ponceau 4R. Side effects: Potential carcinogen; exacerbates asthma and allergy symptoms."
    },
    "E129": {
        "Български": "Алура червено. Странични ефекти: Риск от неврологични смущения и дефицит на вниманието при деца.",
        "English": "Allura Red. Side effects: Risk of neurological disturbances and ADHD symptoms in children."
    },
    "E133": {
        "Български": "Брилянтно синьо. Странични ефекти: Риск от хромозомни увреждания при натрупване в организма.",
        "English": "Brilliant Blue. Side effects: Risk of chromosomal damage with long-term accumulation."
    },
    "E211": {
        "Български": "Натриев бензоат. Странични ефекти: С Витамин C образува бензен (канцероген). Уврежда клетките.",
        "English": "Sodium Benzoate. Side effects: Forms benzene (carcinogen) when combined with Vitamin C. Damages DNA."
    },
    "E250": {
        "Български": "Натриев нитрит. Странични ефекти: Образува нитрозамини. Увеличава риска от рак на дебелото черво.",
        "English": "Sodium Nitrite. Side effects: Forms nitrosamines. Increases risk of colorectal cancer."
    },
    "sodium nitrite": {
        "Български": "Натриев нитрит. Странични ефекти: Канцерогенен консервант, срещан масово в колбасите.",
        "English": "Sodium Nitrite. Side effects: Carcinogenic preservative widely used in processed meats."
    },
    "E621": {
        "Български": "Мононатриев глутамат (MSG). Странични ефекти: Предизвиква главоболие, сърцебиене, гадене и замаяност.",
        "English": "Monosodium Glutamate (MSG). Side effects: Causes headaches, heart palpitations, nausea, and dizziness."
    },
    "msg": {
        "Български": "Мононатриев глутамат. Странични ефекти: Невротоксичен ефект при редовна консумация.",
        "English": "Monosodium Glutamate. Side effects: Neurotoxic effects with regular consumption."
    },
    "glutamate": {
        "Български": "Глутамат. Странични ефекти: Овкусител, изкуствено засилващ апетита, натоварва нервната система.",
        "English": "Glutamate. Side effects: Flavor enhancer that artificially boosts appetite and strains the nervous system."
    },
    "E951": {
        "Български": "Аспартам. Странични ефекти: Свързва се с мигрена, промени в настроението. Потенциален канцероген.",
        "English": "Aspartame. Side effects: Linked to migraines, mood swings, and classified as a potential carcinogen."
    },
    "aspartame": {
        "Български": "Аспартам. Странични ефекти: Изкуствен подсладител, свързан с неврологични оплаквания.",
        "English": "Aspartame. Side effects: Artificial sweetener linked to neurological complaints."
    },
    "хидрогенирано": {
        "Български": "Хидрогенирани мазнини (Трансмазнини). Странични ефекти: Повишават LDL холестерола и риска от инфаркт.",
        "English": "Hydrogenated Fats (Trans Fats). Side effects: Raise LDL cholesterol and increase heart attack risk."
    },
    "hydrogenated": {
        "Български": "Хидрогенирани мазнини (Трансмазнини). Странични ефекти: Причиняват хронични възпаления и запушват артериите.",
        "English": "Hydrogenated Fats (Trans Fats). Side effects: Cause chronic inflammation and clog arteries."
    },
    "палмово масло": {
        "Български": "Рафинирано палмово масло. Странични ефекти: Богата на наситени мазнини, уврежда сърдечно-съдовата система.",
        "English": "Refined Palm Oil. Side effects: High in saturated fats, damages the cardiovascular system."
    },
    "palm oil": {
        "Български": "Палмово масло. Странични ефекти: Натоварва черния дроб и увеличава плаките в кръвоносните съдове.",
        "English": "Palm Oil. Side effects: Strains the liver and increases arterial plaque buildup."
    },
    "глюкозо-фруктозен": {
        "Български": "Глюкозо-фруктозен сироп. Странични ефекти: Води до затлъстяване и омазняване на черния дроб.",
        "English": "Glucose-Fructose Syrup. Side effects: Leads to rapid obesity and fatty liver disease."
    },
    "fructose syrup": {
        "Български": "Високофруктозен сироп. Странични ефекти: Метаболизира се в мазнини, водещи до диабет тип 2.",
        "English": "High-Fructose Corn Syrup. Side effects: Converts directly into liver fat, leading to type 2 diabetes."
    }
}

# ДВУЕЗИЧНИ ЗАМЕСТИТЕЛИ
REPLACEMENT_SUGGESTIONS = {
    "чипс": {"Български": ["Чипс от печена елда", "Домашен чипс на фурна"], "English": ["Baked chickpea chips", "Homemade baked potato chips"]},
    "chips": {"Български": ["Чипс от печена елда", "Домашен чипс на фурна"], "English": ["Baked chickpea chips", "Homemade baked potato chips"]},
    "кола": {"Български": ["Газирана вода с лимон", "Студен каркаде чай"], "English": ["Sparkling water with lemon", "Iced hibiscus tea"]},
    "cola": {"Български": ["Газирана вода с лимон", "Студен каркаде чай"], "English": ["Sparkling water with lemon", "Iced hibiscus tea"]},
    "вафла": {"Български": ["Суров бар от фурми", "Черен шоколад >70%"], "English": ["Raw date & nut bar", "Dark chocolate >70%"]},
    "waffle": {"Български": ["Суров бар от фурми", "Черен шоколад >70%"], "English": ["Raw date & nut bar", "Dark chocolate >70%"]},
    "chocolate": {"Български": ["Черен шоколад без захар"], "English": ["Sugar-free dark chocolate"]},
    "шоколад": {"Български": ["Черен шоколад без захар"], "English": ["Sugar-free dark chocolate"]},
    "колбас": {"Български": ["Печено пуешко филе"], "English": ["Baked turkey fillet"]},
    "sausage": {"Български": ["Печено пуешко филе"], "English": ["Baked turkey fillet"]}
}

# ФУНКЦИЯ ЗА АНАЛИЗ
def analyze_text(text, lang):
    found_bad_stuff = []
    text_lower = text.lower()
    
    for ingredient, translations in HAZARDOUS_INGREDIENTS.items():
        if re.search(r'\b' + re.escape(ingredient.lower()) + r'\b', text_lower) or ingredient.lower() in text_lower:
            found_bad_stuff.append(translations[lang])
            
    suggested_alternatives = []
    for category, alternatives in REPLACEMENT_SUGGESTIONS.items():
        if category in text_lower:
            suggested_alternatives.extend(alternatives[lang])
            
    return found_bad_stuff, list(set(suggested_alternatives))
