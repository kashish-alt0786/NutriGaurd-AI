import streamlit as st
import pandas as pd
import plotly.express as px
from translations import TEXT

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="NutriGuard AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------

foods = pd.read_csv("foods.csv")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.image(
        "https://img.icons8.com/color/96/salad.png",
        width=70
    )

    language = st.selectbox(
        "🌐 Language",
        ["English", "한국어"]
    )

    t = TEXT[language]

    st.divider()

    st.markdown("## 📂 Categories")

    category = st.selectbox(

        "",

        [

            "All",

            "Indian Home",

            "Indian Street",

            "Korean Home",

            "Korean Street",

            "International"

        ]

    )

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------

if category != "All":

    foods = foods[foods["Category"] == category]

# ---------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------

st.title(t["title"])

st.caption(t["subtitle"])

st.divider()
# ---------------------------------------------------
# FOOD SEARCH
# ---------------------------------------------------

st.header(f"🍽 {t['select_food']}")

search = st.text_input(
    "🔍 Search by food name",
    placeholder="Example: Rajma, Bibimbap, Dosa..."
)

# ---------------------------------------------------
# FILTER SEARCH
# ---------------------------------------------------

if search:

    filtered_foods = foods[
        foods["English"].str.contains(search, case=False, na=False)
    ]

else:

    filtered_foods = foods

# ---------------------------------------------------
# FOOD SELECTION
# ---------------------------------------------------

food_names = filtered_foods["English"].tolist()

if len(food_names) == 0:

    st.warning("No matching food found.")

    st.stop()

selected_food = st.selectbox(

    "🍛 Select Food",

    food_names

)

# ---------------------------------------------------
# GET FOOD DATA
# ---------------------------------------------------

result = filtered_foods[
    filtered_foods["English"] == selected_food
].iloc[0]

# ---------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------

analyze = st.button(
    "📊 Analyze Meal",
    use_container_width=True
)
# ---------------------------------------------------
# NUTRITION ANALYSIS
# ---------------------------------------------------

if analyze:

    st.divider()

    st.header(f"📊 {t['nutrition']}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🔥 Calories",
            f"{result['Calories']} kcal"
        )

    with col2:
        st.metric(
            "🍞 Carbohydrates",
            f"{result['Carbs']} g"
        )

    with col3:
        st.metric(
            "🥩 Protein",
            f"{result['Protein']} g"
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "🥑 Fat",
            f"{result['Fat']} g"
        )

    with col5:
        st.metric(
            "🥦 Fiber",
            f"{result['Fiber']} g"
        )

    with col6:
        st.metric(
            "📈 Glycemic Index (GI)",
            result["GI"]
        )

    st.metric(
        "📉 Glycemic Load (GL)",
        result["GL"]
    )

    st.divider()
    # ---------------------------------------------------
# GLYCEMIC ASSESSMENT
# ---------------------------------------------------

    st.header(f"🩺 {t['glycemic']}")

    gi = result["GI"]
    gl = result["GL"]

    # Determine Glycemic Impact

    if gl <= 10:

        impact = "🟢 LOW"

        color = "green"

        message = """
This meal has a relatively low estimated glycemic impact.
"""

    elif gl <= 19:

        impact = "🟡 MODERATE"

        color = "orange"

        message = """
This meal has a moderate estimated glycemic impact.
"""

    else:

        impact = "🔴 HIGH"

        color = "red"

        message = """
This meal has a high estimated glycemic impact.
"""

    st.markdown(
        f"""
<div style="
background-color:{color};
padding:18px;
border-radius:12px;
color:white;
">

<h2>{impact} GLYCEMIC IMPACT</h2>

<p>{message}</p>

<b>Estimated GI:</b> {gi}<br>

<b>Estimated GL:</b> {gl}

</div>
""",
        unsafe_allow_html=True
    )

    st.divider()
    # ---------------------------------------------------
# HEALTHIER ALTERNATIVE
# ---------------------------------------------------

    st.header("🥗 Healthier Alternative")

    current_col, swap_col = st.columns(2)

    with current_col:

        st.subheader("🍽 Current Meal")

        st.error(result["English"])

        st.write(f"🔥 Calories: {result['Calories']} kcal")
        st.write(f"🍞 Carbs: {result['Carbs']} g")
        st.write(f"🥦 Fiber: {result['Fiber']} g")
        st.write(f"📈 GI: {result['GI']}")
        st.write(f"📉 GL: {result['GL']}")

    with swap_col:

        st.subheader("✅ Recommended Swap")

        st.success(result["HealthySwap"])

        st.info(result["Why"])

    st.markdown("---")

    st.subheader("📈 Expected Benefits")

    benefit1, benefit2 = st.columns(2)

    with benefit1:

        st.success("Higher dietary fiber")

        st.success("Lower estimated Glycemic Load")

        st.success("Slower glucose absorption")

    with benefit2:

        st.success("Better post-meal blood sugar response")

        st.success("Supports balanced nutrition")

        st.success("Educational recommendation only")

    st.markdown("---")

    st.subheader("💡 Why is this healthier?")

    st.info(result["Why"])
    # ---------------------------------------------------
# MEAL HISTORY DASHBOARD
# ---------------------------------------------------

    st.header("📈 Meal History Dashboard")

    history = pd.DataFrame({

        "Day": [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun"
        ],

        "Glycemic Impact": [
            "Low",
            "Moderate",
            "High",
            "Low",
            "Moderate",
            "High",
            "Low"
        ]
    })

    impact_count = (
        history["Glycemic Impact"]
        .value_counts()
        .reset_index()
    )

    impact_count.columns = [
        "Impact",
        "Days"
    ]

    fig = px.bar(

        impact_count,

        x="Impact",

        y="Days",

        text="Days",

        title="Weekly Glycemic Impact Summary"

    )

    fig.update_layout(

        xaxis_title="Impact Level",

        yaxis_title="Number of Days"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info(
        "Meal history is currently a demonstration feature. "
        "Future versions will securely save user meals and trends."
    )

    st.divider()
    # ---------------------------------------------------
# EDUCATIONAL RESOURCES
# ---------------------------------------------------

st.header("📚 Educational Resources")

st.write(
    """
NutriGuard AI is designed for educational nutrition awareness.
The following trusted organizations provide evidence-based
information about nutrition, diabetes, and healthy eating.
"""
)

col1, col2 = st.columns(2)

with col1:
    st.link_button(
        "🇺🇸 American Diabetes Association",
        "https://diabetes.org"
    )

    st.link_button(
        "🇺🇸 USDA FoodData Central",
        "https://fdc.nal.usda.gov"
    )

    st.link_button(
        "🌍 World Health Organization",
        "https://www.who.int"
    )

with col2:
    st.link_button(
        "🇮🇳 ICMR – National Institute of Nutrition",
        "https://www.nin.res.in"
    )

    st.link_button(
        "🇰🇷 Korean Nutrition Society",
        "https://www.kns.or.kr"
    )
    # ---------------------------------------------------
# EDUCATIONAL DISCLAIMER
# ---------------------------------------------------

st.header("⚠️ Educational Disclaimer")

st.error("""
**NutriGuard AI is an educational nutrition awareness application.**

The nutrition values, Glycemic Index (GI), Glycemic Load (GL),
and healthier meal suggestions provided by this application are
estimated using publicly available food composition databases and
are intended solely for educational purposes.

This application:

✅ Does NOT diagnose diabetes.

✅ Does NOT predict diabetes risk.

✅ Does NOT replace healthcare professionals.

✅ Does NOT provide medical treatment or personalized medical advice.

Food recognition, portion estimation, and nutritional values are
approximate and may vary depending on ingredients, preparation
methods, serving size, and image quality.

If you have diabetes or another medical condition, consult a
qualified healthcare professional or registered dietitian before
making healthcare decisions.
""")

st.info("""
📖 Data Sources

• USDA FoodData Central

• ICMR–National Institute of Nutrition (India)

• Korean Food Composition Database

• Scientific literature on Glycemic Index and Glycemic Load

• Open-source nutrition datasets
""")

st.success("""
Thank you for using NutriGuard AI!

Our goal is to improve nutrition literacy through explainable,
evidence-informed educational tools—not to replace professional
medical care.
""")

st.divider()
# =====================================================
# PART 9: PROFESSIONAL PRODUCT FOOTER & BRANDING
# NutriGuard AI v1.0.0
# =====================================================

import streamlit as st
from datetime import datetime


# Footer Divider
st.markdown("---")


# Developer Information Section
st.markdown(
    """
    <div style="text-align:center;">

    <h2>💙 NutriGuard AI</h2>

    <p>
    AI-powered nutrition intelligence for
    diabetes-aware eating
    </p>

    <br>

    <h4>👩‍💻 Developed By</h4>

    <p>
    <b>Kashish</b><br>
    AI & Healthcare Technology Enthusiast<br>
    Biomedical Informatics | Machine Learning | Digital Healthcare
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


# Version Information
col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        """
        🏷️ Version

        v1.0.0
        """
    )

with col2:
    st.info(
        """
        📅 Last Updated

        July 2026
        """
    )

with col3:
    st.info(
        """
        🤖 Technology

        AI + ML + Healthcare
        """
    )


st.markdown("---")


# GitHub + Demo Buttons

st.markdown(
    """
    <div style="text-align:center;">

    <h4>Explore NutriGuard AI</h4>

    </div>
    """,
    unsafe_allow_html=True
)


button1, button2 = st.columns(2)


with button1:
    st.link_button(
        "💻 GitHub Repository",
        "https://github.com/"
    )


with button2:
    st.link_button(
        "🌐 Live Demo",
        "https://indo-korean-diabetes-meal-ai-ekdguqlhsxsjnhsmeszucr.streamlit.app/
    )


st.markdown("---")


# Medical Disclaimer

st.warning(
    """
    ⚕️ Medical Disclaimer

    NutriGuard AI provides nutritional insights
    for educational and wellness purposes only.

    This application does not replace professional
    medical diagnosis, treatment, or advice.
    """
)


# Final Branding Message

st.markdown(
    """
    <div style="text-align:center;">

    <h3>💙 NutriGuard AI</h3>

    <p>
    Making nutrition smarter through
    Artificial Intelligence and Healthcare Innovation.
    </p>

    <p>
    © 2026 NutriGuard AI
    </p>

    </div>
    """,
    unsafe_allow_html=True
)
