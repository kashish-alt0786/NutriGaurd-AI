import streamlit as st
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
import pandas as pd
import datetime

st.set_page_config(page_title="NutriGuard AI", page_icon="🛡️", layout="centered")

# --- 1. Cached Vision Model ---
@st.cache_resource
def load_vision_model():
    model_name = "nlpconnect/vit-gpt2-image-captioning"
    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    feature_extractor = ViTImageProcessor.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    device = torch.device("cpu") # Force CPU for Streamlit Cloud
    model.to(device)
    return model, feature_extractor, tokenizer, device

with st.spinner("🧠 Loading open-source Vision Engine (first run 1-2 min)..."):
    model, feature_extractor, tokenizer, device = load_vision_model()

st.title("🛡️ NutriGuard AI")
st.caption("Educational Nutrition Analysis for Diabetes Management | Python + Streamlit + Open-Source Vision")

# BOLD DISCLAIMER
st.error("⚠️ EDUCATIONAL ONLY: Not a clinical tool. No insulin calculation. Does not replace medical advice. Data: USDA, ICMR-NIN, RDA Korea.")

# --- 2. Nutrition DB ---
nutrition_db = {
    'rice': {'carbs': 45, 'gi': 73, 'gl': 28, 'impact': 'High', 'fiber': 'Low', 'reason': 'Refined white grains'},
    'cake': {'carbs': 80, 'gi': 85, 'gl': 40, 'impact': 'High', 'fiber': 'Low', 'reason': 'High sugar + refined flour'},
    'chapati': {'carbs': 15, 'gi': 45, 'gl': 10, 'impact': 'Low', 'fiber': 'High', 'reason': 'Whole wheat'},
    'kimchi': {'carbs': 2, 'gi': 15, 'gl': 1, 'impact': 'Low', 'fiber': 'High', 'reason': 'Fermented low-carb'},
    'dal': {'carbs': 20, 'gi': 35, 'gl': 8, 'impact': 'Low', 'fiber': 'High', 'reason': 'Protein + fiber'},
    'paratha': {'carbs': 45, 'gi': 75, 'gl': 28, 'impact': 'High', 'fiber': 'Low', 'reason': 'Oil fried + refined wheat'},
}

# --- 3. Upload ---
uploaded_file = st.file_uploader("📸 Upload your lunch / breakfast / dinner", type=["jpg","jpeg","png"])

detected_text = ""
selected_food = None

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Meal", width=400)

    if image.mode!= "RGB":
        image = image.convert("RGB")

    st.write("🧠 Local AI Vision Engine processing...")
    pixel_values = feature_extractor(images=[image], return_tensors="pt").pixel_values.to(device)

    with torch.no_grad():
        output_ids = model.generate(pixel_values, max_length=16, num_beams=2) # beams 2 = faster

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    detected_text = preds[0].lower()
    st.success(f"🍽 Food Recognition Output: '{detected_text}'")

    # Routing to DB
    for key in nutrition_db.keys():
        if key in detected_text:
            selected_food = key
            break

# Manual fallback (for GKS demo if model says "a plate of food")
manual = st.selectbox("Or manually select to test Indo-Korean focus:", ["-- Choose --","paratha","chapati","white rice bibimbap (maps to rice)","brown rice bibimbap (maps to chapati)","kimchi","dal","tteokbokki (maps to cake)"])
if manual!= "-- Choose --":
    m = manual.split()[0] # get first word
    if "tteokbokki" in manual: m="cake"
    if "white" in manual: m="rice"
    if "brown" in manual: m="chapati"
    selected_food = m

# --- 4. Glycemic Dashboard ---
if selected_food and selected_food in nutrition_db:
    data = nutrition_db[selected_food]
    st.divider()
    st.subheader(f"📊 Educational Glycemic Estimation: {selected_food.title()}")

    c1,c2,c3 = st.columns(3)
    c1.metric("GI", data['gi'])
    c2.metric("GL", data['gl'])
    c3.metric("Impact Label", data['impact'])

    st.subheader("🧠 Explainable Health Feature")
    if data['impact']=='High':
        st.error(f"• Why High? {data['reason']}\n• Low dietary fiber\n• High refined carbs ({data['carbs']}g)")
    else:
        st.success(f"• Why {data['impact']}? {data['reason']}\n• Balanced fiber\n• Carbs: {data['carbs']}g")

    st.caption(f"Transparency Metrics: Refined Grains: {data['reason']} | Carbs: {data['carbs']}g | Fiber: {data['fiber']}")

    # Comparison Screen
    st.subheader("🔄 Comparison: Swap to Lower-Glycemic")
    if selected_food == "paratha":
        df = pd.DataFrame([{"Food":"Paratha (High)","GI":75,"GL":28},{"Food":"Chapati (Low)","GI":45,"GL":10}])
        st.table(df)
        st.info("🇮🇳 Swap: Paratha → Whole-wheat Chapati")
    elif selected_food == "rice":
        df = pd.DataFrame([{"Food":"White Rice Bibimbap (High)","GI":73,"GL":28},{"Food":"Brown Rice Bibimbap (Mod)","GI":50,"GL":18}])
        st.table(df)
        st.info("🇰🇷 Swap: White Rice Bibimbap → Brown Rice Bibimbap")

    # Meal History Chart
    st.divider()
    st.subheader("📈 Meal History (Weekly Trends)")
    if 'history' not in st.session_state: st.session_state.history=[]
    if st.button("Add to History"):
        st.session_state.history.append({"date": datetime.datetime.now().strftime("%m/%d"), "food": selected_food, "gl": data['gl']})
    if st.session_state.history:
        hist_df = pd.DataFrame(st.session_state.history)
        st.bar_chart(hist_df, x="date", y="gl")

st.divider()
st.subheader("📚 Learning Corner")
st.markdown("- What is GI/GL? GI = speed, GL = amount. Lower = steadier.\n- [American Diabetes Association](https://diabetes.org/health-wellness/food-nutrition)\n- [Korean Diabetes Association](https://www.diabetes.or.kr/english/)")

st.subheader("System Architecture")
st.code("""
[ User Uploads Meal Photo ]
          │
          ▼
[ Open-Source ViT-GPT2 Vision Engine ]
          │
          ▼
[ Food Identification & Extraction ]
          │
          ▼
[ Public DBs: USDA / ICMR-NIN / RDA ]
          │
          ▼
[ Nutritional Analysis Block ]
          │
          ▼
[ GI / GL Impact Estimation ]
          │
          ▼
[ Comparison Dashboard & Swaps ]
          │
          ▼
[ Streamlit Meal History Graphing ]
""")

st.caption("Scientific Limitations: Depends on image clarity, recipe variations affect GI, standard portions used.")
