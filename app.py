import streamlit as st
import easyocr
import numpy as np
from PIL import Image
# Импортираме анализатора от нашата собствена библиотека
from ingredients_db import analyze_text

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

# 4. СЕЛЕКЦИЯ НА ЕЗИК
selected_lang = st.sidebar.selectbox("🌐 Изберете език / Choose Language", ("Български", "English"))
t = LANG_TEXTS[selected_lang]

# 5. ПОТРЕБИТЕЛСКИ ИНТЕРФЕЙС
st.title(t["title"])
st.write(t["subtitle"])

source_option = st.radio(t["method_label"], (t["cam_opt"], t["gal_opt"]))

image_file = None
if source_option == t["cam_opt"]:
    image_file = st.camera_input(t["cam_placeholder"])
elif source_option == t["gal_opt"]:
    image_file = st.file_uploader(t["gal_placeholder"], type=["jpg", "jpeg", "png"])

# 6. ОБРАБОТКА И OCR
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
        
        # Извикване на функцията от нашата библиотека
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
