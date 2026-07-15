import streamlit as st
import pandas as pd
from PIL import Image
import google.generativeai as genai
import json
import os
from datetime import datetime

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="NutriGuard AI",
    page_icon="🥗",
    layout="wide"
)

# ----------------------------
# CUSTOM CSS
# ----------------------------

st.markdown("""
<style>

.main{
    padding-top:20px;
}

.title{
    text-align:center;
    font-size:42px;
    font-weight:bold;
    color:#2E8B57;
}

.subtitle{
    text-align:center;
    font-size:18px;
    color:gray;
}

.result-box{
    padding:15px;
    border-radius:10px;
    background:#F7F7F7;
    margin-top:10px;
}

.low{
    background:#D4EDDA;
    padding:12px;
    border-radius:8px;
}

.medium{
    background:#FFF3CD;
    padding:12px;
    border-radius:8px;
}

.high{
    background:#F8D7DA;
    padding:12px;
    border-radius:8px;
}

.footer{
    font-size:13px;
    color:gray;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# TITLE
# ----------------------------

st.markdown(
    "<div class='title'>🥗 NutriGuard AI</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Educational Nutrition Analysis for Diabetes Management</div>",
    unsafe_allow_html=True
)

st.divider()

# ----------------------------
# SIDEBAR
# ----------------------------

st.sidebar.title("Settings")

language = st.sidebar.selectbox(
    "Language",
    [
        "English",
        "한국어"
    ]
)

show_history = st.sidebar.checkbox(
    "Show Meal History",
    value=True
)

# ----------------------------
# GEMINI API
# ----------------------------

api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# ----------------------------
# LOAD DATABASE
# ----------------------------

nutrition_df = pd.read_csv("nutrition_db.csv")

# ----------------------------
# SESSION STATE
# ----------------------------

if "history" not in st.session_state:
    st.session_state.history = []

# ----------------------------
# IMAGE UPLOAD
# ----------------------------

uploaded_file = st.file_uploader(
    "📷 Upload Meal Image",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)
# -------------------------------------------------------
# AI FOOD RECOGNITION
# -------------------------------------------------------

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Meal",
        use_container_width=True
    )

    st.divider()

    with st.spinner("🔍 Analyzing your meal..."):

        prompt = """
You are a nutrition analysis assistant.

Analyze this meal image.

Return ONLY valid JSON.

{
  "food_name":"",
  "confidence":0,
  "estimated_portion":"",
  "carbs":0,
  "protein":0,
  "fat":0,
  "fiber":0,
  "calories":0,
  "glycemic_index":0,
  "glycemic_load":0,
  "glycemic_impact":"",
  "reason":"",
  "healthy_swap":"",
  "swap_reason":""
}

Rules:

- Respond ONLY JSON.
- No markdown.
- No explanations.
- Confidence should be 0-100.
- Glycemic Impact must be:
Low
Moderate
High

Food should be recognized even if it is Indian, Korean or international.

Nutrition values are approximate.
"""

        try:

            response = model.generate_content(
                [
                    prompt,
                    image
                ]
            )

            raw_text = response.text.strip()

            if raw_text.startswith("```"):
                raw_text = raw_text.replace("```json", "")
                raw_text = raw_text.replace("```", "")
                raw_text = raw_text.strip()

            result = json.loads(raw_text)

        except Exception as e:

            st.error("❌ Unable to analyze this image.")

            st.exception(e)

            st.stop()
            st.success("✅ Meal recognized successfully")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "🍽 Food",
        result["food_name"]
    )

with col2:

    st.metric(
        "🎯 Confidence",
        f'{result["confidence"]}%'
    )

st.write("Estimated Portion")

st.info(result["estimated_portion"])
if result["confidence"] < 60:

    st.warning(
        """
The AI is not highly confident about this meal.

Nutrition estimates may be inaccurate.
Consider uploading a clearer image.
"""
    )
    # -------------------------------------------------------
# NUTRITION DASHBOARD
# -------------------------------------------------------

st.divider()

st.subheader("📊 Nutrition Analysis")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Calories",
    f"{result['calories']} kcal"
)

c2.metric(
    "Carbs",
    f"{result['carbs']} g"
)

c3.metric(
    "Protein",
    f"{result['protein']} g"
)

c4.metric(
    "Fat",
    f"{result['fat']} g"
)

c5.metric(
    "Fiber",
    f"{result['fiber']} g"
)
st.divider()

st.subheader("🩺 Glycemic Assessment")

g1, g2 = st.columns(2)

with g1:

    st.metric(
        "Estimated Glycemic Index",
        result["glycemic_index"]
    )

    st.metric(
        "Estimated Glycemic Load",
        result["glycemic_load"]
    )

with g2:

    impact = result["glycemic_impact"]

    if impact.lower() == "low":

        st.success("🟢 LOW Glycemic Impact")

    elif impact.lower() == "moderate":

        st.warning("🟡 MODERATE Glycemic Impact")

    else:

        st.error("🔴 HIGH Glycemic Impact")
        st.divider()

st.subheader("💡 Why did the AI give this result?")

st.info(result["reason"])
st.markdown("""
- High carbohydrate content
- Refined grains
- Low dietary fiber
""")
- Rapid glucose absorption expected
st.divider()

st.subheader("🥗 Healthier Alternative")

swap1, swap2 = st.columns(2)

with swap1:

    st.markdown("### Current Meal")

    st.write(result["food_name"])

with swap2:

    st.markdown("### Recommended Swap")

    st.success(result["healthy_swap"])

st.write("### Why is it healthier?")

st.write(result["swap_reason"])
White Rice Bibimbap
Brown Rice Bibimbap
Higher fiber

Lower Glycemic Load

Slower glucose absorption

Better post-meal blood sugar response
st.divider()

st.warning("""
⚠️ Educational Disclaimer

NutriGuard AI is an educational nutrition awareness tool.

Nutrition values, GI and GL are estimates based on publicly
available food composition databases.

This application does NOT diagnose diabetes,
recommend treatment,
or replace professional medical advice.

Always consult a qualified healthcare professional
for diagnosis and medical decisions.
""")
history_item = {

    "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),

    "Meal": result["food_name"],

    "Calories": result["calories"],

    "GI": result["glycemic_index"],

    "GL": result["glycemic_load"],

    "Impact": result["glycemic_impact"]

}

st.session_state.history.append(history_item)
