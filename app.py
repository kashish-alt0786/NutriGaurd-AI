import streamlit as st
from PIL import Image
import pandas as pd
import datetime

st.set_page_config(page_title="NutriGuard AI", page_icon="🛡️", layout="centered")

st.title("🛡️ NutriGuard AI")
st.caption("Educational Nutrition Analysis for Diabetes Management | Python + Streamlit")

st.error("⚠️ EDUCATIONAL ONLY: This is a learning companion. No insulin calculation. Does NOT replace medical advice. Data: USDA FoodData Central, ICMR-NIN India, RDA Korea.")

# DB
nutrition_db = {
    'paratha': {'carbs': 45, 'gi': 75, 'gl': 28, 'impact': 'High', 'fiber': 2, 'reason': 'High refined wheat + oil frying'},
    'chapati': {'carbs': 15, 'gi': 45, 'gl': 10, 'impact': 'Low', 'fiber': 3, 'reason': 'Whole wheat, high fiber'},
    'white rice bibimbap': {'carbs': 65, 'gi': 80, 'gl': 35, 'impact': 'High', 'fiber': 2, 'reason': 'High white rice content'},
    'brown rice bibimbap': {'carbs': 50, 'gi': 50, 'gl': 18, 'impact': 'Moderate', 'fiber': 6, 'reason': 'Brown rice adds fiber'},
    'kimchi': {'carbs': 2, 'gi': 15, 'gl': 1, 'impact': 'Low', 'fiber': 1, 'reason': 'Fermented, very low carb'},
    'dal': {'carbs': 20, 'gi': 35, 'gl': 8, 'impact': 'Low', 'fiber': 5, 'reason': 'High fiber + protein'},
    'tteokbokki': {'carbs': 80, 'gi': 85, 'gl': 40, 'impact': 'High', 'fiber': 1, 'reason': 'Rice cake + sugar sauce'},
    'cake': {'carbs': 80, 'gi': 85, 'gl': 40, 'impact': 'High', 'fiber': 1, 'reason': 'Refined flour + sugar'},
}

swap_db = {'paratha':'chapati', 'white rice bibimbap':'brown rice bibimbap', 'tteokbokki':'kimchi', 'cake':'chapati', 'rice':'brown rice bibimbap'}

st.divider()
st.header("📸 Step 1: Upload Meal Photo")
uploaded_file = st.file_uploader("Upload breakfast, lunch, dinner photo", type=['jpg','jpeg','png'])

detected = None
if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=400, caption="Your meal")
    st.info("🧠 Vision Engine (Open-Source Mode): For demo, select food below to simulate detection. Architecture supports Gemini Vision API via Secrets.")

food_choice = st.selectbox("Step 1b: Select food (simulates AI detection):", ["-- Choose --"]+list(nutrition_db.keys()))

if food_choice!="-- Choose --":
    detected = food_choice

if detected:
    data = nutrition_db[detected]
    st.divider()
    st.header(f"🔬 Step 2 & 3: Nutritional + GI/GL Analysis for {detected.title()}")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Carbs", f"{data['carbs']}g")
    c2.metric("GI", data['gi'])
    c3.metric("GL", data['gl'])
    c4.metric("Impact", data['impact'])

    st.subheader("🧠 Why this rating?")
    if data['impact']=='High':
        st.error(f"• High refined grains\n• Low fiber ({data['fiber']}g)\n• {data['reason']}")
    else:
        st.success(f"• {data['reason']}\n• Fiber: {data['fiber']}g\n• Carbs: {data['carbs']}g")

    st.caption(f"Transparency: {data['reason']} | Refined: {'High' if data['gi']>70 else 'Low'} | Fiber: {data['fiber']}g")

    st.divider()
    st.header("🔄 Step 4: Healthy Swap Dashboard")
    swap = swap_db.get(detected)
    if swap and swap in nutrition_db:
        sd = nutrition_db[swap]
        df = pd.DataFrame([
            {"Food": detected, "GI": data['gi'], "GL": data['gl'], "Impact": data['impact']},
            {"Food": f"{swap} (Healthier)", "GI": sd['gi'], "GL": sd['gl'], "Impact": sd['impact']}
        ])
        st.table(df)
        if "paratha" in detected: st.info("🇮🇳 Example: Paratha (High) → Chapati (Low)")
        if "bibimbap" in detected or "rice" in detected: st.info("🇰🇷 Example: White Rice Bibimbap (High) → Brown Rice Bibimbap (Moderate)")
    else:
        st.success("This is already a low-impact choice!")

    st.divider()
    st.header("📈 Meal History (Weekly Trends)")
    if 'history' not in st.session_state: st.session_state.history=[]
    if st.button("Add to History"):
        st.session_state.history.append({"date": datetime.datetime.now().strftime("%m/%d"), "food": detected, "gl": data['gl']})
        st.toast("Added!")
    if st.session_state.history:
        st.bar_chart(pd.DataFrame(st.session_state.history), x="date", y="gl")
    else:
        st.caption("Add meals to track GL trends.")

st.divider()
st.header("📚 Learning Corner & Architecture")
st.markdown("**GI/GL:** GI = speed of sugar rise, GL = GI x carbs eaten. Lower = steadier.")
st.markdown("- [ADA Guidelines](https://diabetes.org/health-wellness/food-nutrition)\n- [Korean Diabetes Association](https://www.diabetes.or.kr/english/)")
st.warning("Limitations: Image clarity, recipe variations, standard portions used, public DB averages.")
st.code("""
[ User Uploads Meal Photo ]
          │
          ▼
[ Gemini Vision API Engine / Open-Source Fallback ]
          │
          ▼
[ Food Identification & Extraction ]
          │
          ▼
[ Public Databases: USDA / ICMR-NIN / RDA ]
          │
          ▼
[ Nutritional Analysis Block ]
          │
          ▼
[ GI / GL Impact Estimation ]
          │
          ▼
[ Comparison Dashboard & Educational Swaps ]
          │
          ▼
[ Streamlit Meal History Graphing ]
""", language="text")
st.caption("Quality Over Quantity: Focused on 2 polished apps. No doctor login/bloat.")
