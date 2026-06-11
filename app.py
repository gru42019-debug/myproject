import streamlit as st
import numpy as np
from PIL import Image
import easyocr  # <--- Увери се, че този ред го има!
import re


# 1. НАСТРОЙКА НА СТРАНИЦАТА
st.set_page_config(page_title="Smart Food Scanner", page_icon="🥗", layout="centered")

# 2. ИНИЦИАЛИЗАЦИЯ НА EASYOCR
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_ocr_reader()

# 3. ЕЗИКОВИ ПРЕВОДИ ЗА ИНТЕРФЕЙСА
LANG_TEXTS = {
    "Български": {
        "title": "🥗 Скенер за вредни съставки в храните",
        "subtitle": "Снимайте или качете етикета със съставките на продукта (текста, не баркода).",
        "method_label": "Изберете метод на сканиране:",
        "cam_opt": "📷 Камера на място",
        "gal_opt": "📁 Снимка от галерия",
        "cam_placeholder": "Снимайте етикета със съставките",
        "gal_placeholder": "Качете снимка на етикета",
        "img_caption": "Качено изображение",
        "loading": "⏳ Текстът се разчита... Моля, изчакайте.",
        "detected_text": "📝 Разчетен текст от етикета:",
        "hazard_found": "⚠️ Внимание! Намерени са вредни съставки:",
        "hazard_clean": "✅ Не са открити критични вредни съставки от нашата база данни в този етикет.",
        "alt_title": "💡 Здравословни алтернативи:",
        "alt_subtitle": "Препоръчваме да замените този продукт с:",
        "alt_generic": "Не можахме да определим точната категория на продукта. Избирайте чисти храни с малко съставки!",
        "no_text": "❌ Не беше намерен текст на снимката. Опитайте отново при по-добра светлина и фокус."
    },
    "English": {
        "title": "🥗 Harmful Ingredients Scanner",
        "subtitle": "Scan or upload the product ingredients label (text, not the barcode).",
        "method_label": "Choose scanning method:",
        "cam_opt": "📷 Live Camera",
        "gal_opt": "📁 Photo from Gallery",
        "cam_placeholder": "Take a photo of the ingredients label",
        "gal_placeholder": "Upload a label image",
        "img_caption": "Uploaded Image",
        "loading": "⏳ Reading text... Please wait.",
        "detected_text": "📝 Extracted text from label:",
        "hazard_found": "⚠️ Warning! Harmful ingredients detected:",
        "hazard_clean": "✅ No critical harmful ingredients found in our database for this label.",
        "alt_title": "💡 Healthy Alternatives:",
        "alt_subtitle": "We recommend replacing this product with:",
        "alt_generic": "Could not determine the exact product category. Choose whole foods with fewer ingredients!",
        "no_text": "❌ No text found in the image. Please try again with better lighting and focus."
    }
}

# 4. ДВУЕЗИЧНА БАЗА ДАННИ СЪС СТРАНИЧНИ ЕФЕКТИ (ИНТЕГРИРАНА ТУК)
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
        "Български": "Натриев бензоат. Странични ефекти: В комбинация с Витамин C образува бензен (канцероген). Уврежда клетките.",
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

# 5. ДВУЕЗИЧНИ ЗАМЕСТИТЕЛИ
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

# 6. ФУНКЦИЯ ЗА АНАЛИЗ НА ТЕКСТА
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

# 7. СЕЛЕКЦИЯ НА ЕЗИК ОТ SIDEBAR
selected_lang = st.sidebar.selectbox("🌐 Изберете език / Choose Language", ("Български", "English"))
t = LANG_TEXTS[selected_lang]

# 8. ПОТРЕБИТЕЛСКИ ИНТЕРФЕЙС
st.title(t["title"])
st.write(t["subtitle"])

source_option = st.radio(t["method_label"], (t["cam_opt"], t["gal_opt"]))

image_file = None
if source_option == t["cam_opt"]:
    image_file = st.camera_input(t["cam_placeholder"])
elif source_option == t["gal_opt"]:
    image_file = st.file_uploader(t["gal_placeholder"], type=["jpg", "jpeg", "png"])

# 9. ОБРАБОТКА И OCR
if image_file is not None:
    image = Image.open(image_file)
    image_np = np.array(image)
    
    st.image(image, caption=t["img_caption"], use_container_width=True)
    
    with st.spinner(t["loading"]):
        ocr_result = reader.readtext(image_np, detail=0)
        full_text = " ".join(ocr_result)
        
    st.subheader(t["detected_text"])
    if full_text.strip():
        st.info(full_text)
        
        # Извикване на локалната функция за анализ
        detected_hazards, alternatives = analyze_text(full_text, selected_lang)
        
        st.divider()
        if detected_hazards:
            st.error(f"{t['hazard_found']} ({len(detected_hazards)})")
            for desc in detected_hazards:
                st.markdown(f"🔴 **{desc}**")
        else:
            st.success(t["hazard_clean"])
            
        st.subheader(t["alt_title"])
        if alternatives:
            st.write(t["alt_subtitle"])
            for alt in alternatives:
                st.markdown(f"🍏 {alt}")
        else:
            st.write(t["alt_generic"])
    else:
        st.warning(t["no_text"])


# 1. НАСТРОЙКА НА СТРАНИЦАТА
st.set_page_config(page_title="Smart Food Scanner", page_icon="🥗", layout="centered")

# 2. ИНИЦИАЛИЗАЦИЯ НА EASYOCR
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_ocr_reader()

# 3. ЕЗИКОВИ ПРЕВОДИ ЗА ИНТЕРФЕЙСА
LANG_TEXTS = {
    "Български": {
        "title": "🥗 Скенер за вредни съставки в храните",
        "subtitle": "Снимайте или качете етикета със съставките на продукта (текста, не баркода).",
        "method_label": "Изберете метод на сканиране:",
        "cam_opt": "📷 Камера на място",
        "gal_opt": "📁 Снимка от галерия",
        "cam_placeholder": "Снимайте етикета със съставките",
        "gal_placeholder": "Качете снимка на етикета",
        "img_caption": "Качено изображение",
        "loading": "⏳ Текстът се разчита... Моля, изчакайте.",
        "detected_text": "📝 Разчетен текст от етикета:",
        "hazard_found": "⚠️ Внимание! Намерени са вредни съставки:",
        "hazard_clean": "✅ Не са открити критични вредни съставки от нашата база данни в този етикет.",
        "alt_title": "💡 Здравословни алтернативи:",
        "alt_subtitle": "Препоръчваме да замените този продукт с:",
        "alt_generic": "Не можахме да определим точната категория на продукта. Избирайте чисти храни с малко съставки!",
        "no_text": "❌ Не беше намерен текст на снимката. Опитайте отново при по-добра светлина и фокус."
    },
    "English": {
        "title": "🥗 Harmful Ingredients Scanner",
        "subtitle": "Scan or upload the product ingredients label (text, not the barcode).",
        "method_label": "Choose scanning method:",
        "cam_opt": "📷 Live Camera",
        "gal_opt": "📁 Photo from Gallery",
        "cam_placeholder": "Take a photo of the ingredients label",
        "gal_placeholder": "Upload a label image",
        "img_caption": "Uploaded Image",
        "loading": "⏳ Reading text... Please wait.",
        "detected_text": "📝 Extracted text from label:",
        "hazard_found": "⚠️ Warning! Harmful ingredients detected:",
        "hazard_clean": "✅ No critical harmful ingredients found in our database for this label.",
        "alt_title": "💡 Healthy Alternatives:",
        "alt_subtitle": "We recommend replacing this product with:",
        "alt_generic": "Could not determine the exact product category. Choose whole foods with fewer ingredients!",
        "no_text": "❌ No text found in the image. Please try again with better lighting and focus."
    }
}

# 4. ДВУЕЗИЧНА БАЗА ДАННИ СЪС СТРАНИЧНИ ЕФЕКТИ (ИНТЕГРИРАНА ТУК)
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
        "Български": "Натриев бензоат. Странични ефекти: В комбинация с Витамин C образува бензен (канцероген). Уврежда клетките.",
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

# 5. ДВУЕЗИЧНИ ЗАМЕСТИТЕЛИ
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

# 6. ФУНКЦИЯ ЗА АНАЛИЗ НА ТЕКСТА
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

# 7. СЕЛЕКЦИЯ НА ЕЗИК ОТ SIDEBAR
selected_lang = st.sidebar.selectbox("🌐 Изберете език / Choose Language", ("Български", "English"))
t = LANG_TEXTS[selected_lang]

# 8. ПОТРЕБИТЕЛСКИ ИНТЕРФЕЙС
st.title(t["title"])
st.write(t["subtitle"])

source_option = st.radio(t["method_label"], (t["cam_opt"], t["gal_opt"]))

image_file = None
if source_option == t["cam_opt"]:
    image_file = st.camera_input(t["cam_placeholder"])
elif source_option == t["gal_opt"]:
    image_file = st.file_uploader(t["gal_placeholder"], type=["jpg", "jpeg", "png"])

# 9. ОБРАБОТКА И OCR
if image_file is not None:
    image = Image.open(image_file)
    image_np = np.array(image)
    
    st.image(image, caption=t["img_caption"], use_container_width=True)
    
    with st.spinner(t["loading"]):
        ocr_result = reader.readtext(image_np, detail=0)
        full_text = " ".join(ocr_result)
        
    st.subheader(t["detected_text"])
    if full_text.strip():
        st.info(full_text)
        
        # Извикване на локалната функция за анализ
        detected_hazards, alternatives = analyze_text(full_text, selected_lang)
        
        st.divider()
        if detected_hazards:
            st.error(f"{t['hazard_found']} ({len(detected_hazards)})")
            for desc in detected_hazards:
                st.markdown(f"🔴 **{desc}**")
        else:
            st.success(t["hazard_clean"])
            
        st.subheader(t["alt_title"])
        if alternatives:
            st.write(t["alt_subtitle"])
            for alt in alternatives:
                st.markdown(f"🍏 {alt}")
        else:
            st.write(t["alt_generic"])
    else:
        st.warning(t["no_text"])


# 1. НАСТРОЙКА НА СТРАНИЦАТА
st.set_page_config(page_title="Smart Food Scanner", page_icon="🥗", layout="centered")

# 2. ИНИЦИАЛИЗАЦИЯ НА EASYOCR
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_ocr_reader()

# 3. ЕЗИКОВИ ПРЕВОДИ ЗА ИНТЕРФЕЙСА
LANG_TEXTS = {
    "Български": {
        "title": "🥗 Скенер за вредни съставки в храните",
        "subtitle": "Снимайте или качете етикета със съставките на продукта (текста, не баркода).",
        "method_label": "Изберете метод на сканиране:",
        "cam_opt": "📷 Камера на място",
        "gal_opt": "📁 Снимка от галерия",
        "cam_placeholder": "Снимайте етикета със съставките",
        "gal_placeholder": "Качете снимка на етикета",
        "img_caption": "Качено изображение",
        "loading": "⏳ Текстът се разчита... Моля, изчакайте.",
        "detected_text": "📝 Разчетен текст от етикета:",
        "hazard_found": "⚠️ Внимание! Намерени са вредни съставки:",
        "hazard_clean": "✅ Не са открити критични вредни съставки от нашата база данни в този етикет.",
        "alt_title": "💡 Здравословни алтернативи:",
        "alt_subtitle": "Препоръчваме да замените този продукт с:",
        "alt_generic": "Не можахме да определим точната категория на продукта. Избирайте чисти храни с малко съставки!",
        "no_text": "❌ Не беше намерен текст на снимката. Опитайте отново при по-добра светлина и фокус."
    },
    "English": {
        "title": "🥗 Harmful Ingredients Scanner",
        "subtitle": "Scan or upload the product ingredients label (text, not the barcode).",
        "method_label": "Choose scanning method:",
        "cam_opt": "📷 Live Camera",
        "gal_opt": "📁 Photo from Gallery",
        "cam_placeholder": "Take a photo of the ingredients label",
        "gal_placeholder": "Upload a label image",
        "img_caption": "Uploaded Image",
        "loading": "⏳ Reading text... Please wait.",
        "detected_text": "📝 Extracted text from label:",
        "hazard_found": "⚠️ Warning! Harmful ingredients detected:",
        "hazard_clean": "✅ No critical harmful ingredients found in our database for this label.",
        "alt_title": "💡 Healthy Alternatives:",
        "alt_subtitle": "We recommend replacing this product with:",
        "alt_generic": "Could not determine the exact product category. Choose whole foods with fewer ingredients!",
        "no_text": "❌ No text found in the image. Please try again with better lighting and focus."
    }
}

# 4. ДВУЕЗИЧНА БАЗА ДАННИ СЪС СТРАНИЧНИ ЕФЕКТИ (ИНТЕГРИРАНА ТУК)
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
        "Български": "Натриев бензоат. Странични ефекти: В комбинация с Витамин C образува бензен (канцероген). Уврежда клетките.",
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

# 5. ДВУЕЗИЧНИ ЗАМЕСТИТЕЛИ
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

# 6. ФУНКЦИЯ ЗА АНАЛИЗ НА ТЕКСТА
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

# 7. СЕЛЕКЦИЯ НА ЕЗИК ОТ SIDEBAR
selected_lang = st.sidebar.selectbox("🌐 Изберете език / Choose Language", ("Български", "English"))
t = LANG_TEXTS[selected_lang]

# 8. ПОТРЕБИТЕЛСКИ ИНТЕРФЕЙС
st.title(t["title"])
st.write(t["subtitle"])

source_option = st.radio(t["method_label"], (t["cam_opt"], t["gal_opt"]))

image_file = None
if source_option == t["cam_opt"]:
    image_file = st.camera_input(t["cam_placeholder"])
elif source_option == t["gal_opt"]:
    image_file = st.file_uploader(t["gal_placeholder"], type=["jpg", "jpeg", "png"])

# 9. ОБРАБОТКА И OCR
if image_file is not None:
    image = Image.open(image_file)
    image_np = np.array(image)
    
    st.image(image, caption=t["img_caption"], use_container_width=True)
    
    with st.spinner(t["loading"]):
        ocr_result = reader.readtext(image_np, detail=0)
        full_text = " ".join(ocr_result)
        
    st.subheader(t["detected_text"])
    if full_text.strip():
        st.info(full_text)
        
        # Извикване на локалната функция за анализ
        detected_hazards, alternatives = analyze_text(full_text, selected_lang)
        
        st.divider()
        if detected_hazards:
            st.error(f"{t['hazard_found']} ({len(detected_hazards)})")
            for desc in detected_hazards:
                st.markdown(f"🔴 **{desc}**")
        else:
            st.success(t["hazard_clean"])
            
        st.subheader(t["alt_title"])
        if alternatives:
            st.write(t["alt_subtitle"])
            for alt in alternatives:
                st.markdown(f"🍏 {alt}")
        else:
            st.write(t["alt_generic"])
    else:
        st.warning(t["no_text"])
