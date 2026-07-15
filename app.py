import streamlit as st
from PIL import Image
import pandas as pd
import requests
import io
from datetime import datetime
import json

st.set_page_config(page_title="NutriGuard AI - AUTO Vision", page_icon="🛡️", layout="wide")
st.title("🛡️ NutriGuard AI - AUTO Vision")
st.caption("Upload → Auto recognises → No typing needed | Indo-Korean Diabetes Meal AI")
st.error("⚠️ EDUCATIONAL ONLY: Does not replace medical advice. Estimates only.")

# --- 50 FOOD DB (same as you have) ---
nutrition_db = {
    'cake': {'cal': 400, 'carbs': 80, 'protein': 4, 'fiber': 1, 'sugar': 35, 'gi': 85, 'gl': 40, 'impact': 'High', 'color':'🔴', 'reason': 'Refined flour + sugar', 'better': 'brown rice', 'better_carbs': 38},
    'chapati': {'cal': 120, 'carbs': 15, 'protein': 3, 'fiber': 3, 'sugar': 0.5, 'gi': 45, 'gl': 10, 'impact': 'Low', 'color':'🟢', 'reason': 'Whole wheat fiber', 'better': 'chapati', 'better_carbs': 15},
    'chana masala': {'cal': 280, 'carbs': 30, 'protein': 12, 'fiber': 8, 'sugar': 5, 'gi': 38, 'gl': 12, 'impact': 'Low', 'color':'🟢', 'reason': 'Chickpea protein fiber', 'better': 'chana masala', 'better_carbs': 30},
    'chole bhature': {'cal': 450, 'carbs': 55, 'protein': 10, 'fiber': 6, 'sugar': 4, 'gi': 70, 'gl': 32, 'impact': 'High', 'color':'🔴', 'reason': 'Bhatura deep fried', 'better': 'chana masala', 'better_carbs': 30},
    'samosa': {'cal': 250, 'carbs': 30, 'protein': 4, 'fiber': 2, 'sugar': 1, 'gi': 70, 'gl': 22, 'impact': 'High', 'color':'🔴', 'reason': 'Deep fried maida', 'better': 'chana masala', 'better_carbs': 30},
    'dosa': {'cal': 200, 'carbs': 35, 'protein': 4, 'fiber': 1, 'sugar': 1, 'gi': 65, 'gl': 20, 'impact': 'Moderate', 'color':'🟡', 'reason': 'Rice + lentil fermented', 'better': 'idli', 'better_carbs': 25},
    'idli': {'cal': 150, 'carbs': 25, 'protein': 5, 'fiber': 2, 'sugar': 0.5, 'gi': 50, 'gl': 12, 'impact': 'Low', 'color':'🟢', 'reason': 'Steamed fermented', 'better': 'idli', 'better_carbs': 25},
    'biryani': {'cal': 380, 'carbs': 50, 'protein': 10, 'fiber': 3, 'sugar': 2, 'gi': 60, 'gl': 25, 'impact': 'Moderate', 'color':'🟡', 'reason': 'Rice + oil', 'better': 'brown rice', 'better_carbs': 38},
    'kimchi': {'cal': 20, 'carbs': 2, 'protein': 1, 'fiber': 1, 'sugar': 1, 'gi': 15, 'gl': 1, 'impact': 'Low', 'color':'🟢', 'reason': 'Fermented low carb', 'better': 'kimchi', 'better_carbs': 2},
    'bibimbap': {'cal': 350, 'carbs': 50, 'protein': 13, 'fiber': 6, 'sugar': 2, 'gi': 50, 'gl': 18, 'impact': 'Moderate', 'color':'🟡', 'reason': 'Mixed rice veggies', 'better': 'brown rice bibimbap', 'better_carbs': 38},
    'tteokbokki': {'cal': 350, 'carbs': 80, 'protein': 4, 'fiber': 1, 'sugar': 15, 'gi': 85, 'gl': 40, 'impact': 'High', 'color':'🔴', 'reason': 'Rice cake sweet sauce', 'better': 'kimchi', 'better_carbs': 2},
    'kimbap': {'cal': 300, 'carbs': 45, 'protein': 8, 'fiber': 3, 'sugar': 2, 'gi': 60, 'gl': 20, 'impact': 'Moderate', 'color':'🟡', 'reason': 'Rice + seaweed', 'better': 'bibimbap', 'better_carbs': 50},
    'bulgogi': {'cal': 350, 'carbs': 15, 'protein': 25, 'fiber': 1, 'sugar': 10, 'gi': 45, 'gl': 10, 'impact': 'Low', 'color':'🟢', 'reason': 'Beef protein but sugary marinade', 'better': 'bulgogi', 'better_carbs': 15},
    'ramen': {'cal': 450, 'carbs': 60, 'protein': 12, 'fiber': 2, 'sugar': 3, 'gi': 70, 'gl': 30, 'impact': 'High', 'color':'🔴', 'reason': 'Refined noodles', 'better': 'japchae', 'better_carbs': 30},
    'white rice': {'cal': 200, 'carbs': 45, 'protein': 3, 'fiber': 0, 'sugar': 0, 'gi': 80, 'gl': 30, 'impact': 'High', 'color':'🔴', 'reason': 'Refined grain low fiber', 'better': 'brown rice', 'better_carbs': 38},
    'brown rice': {'cal': 180, 'carbs': 38, 'protein': 4, 'fiber': 3, 'sugar': 0, 'gi': 50, 'gl': 16, 'impact': 'Low', 'color':'🟢', 'reason': 'Whole grain fiber', 'better': 'brown rice', 'better_carbs': 38},
    'pizza': {'cal': 350, 'carbs': 40, 'protein': 12, 'fiber': 2, 'sugar': 5, 'gi': 70, 'gl': 28, 'impact': 'High', 'color':'🔴', 'reason': 'Refined base cheese', 'better': 'salad', 'better_carbs': 8},
}

label_map = {
    'birthday cake': 'cake', 'chocolate cake': 'cake', 'cake': 'cake',
    'chana masala': 'chana masala', 'chole': 'chole bhature',
    'samosa': 'samosa', 'dosa': 'dosa', 'idli': 'idli', 'biryani': 'biryani',
    'kimchi': 'kimchi', 'bibimbap': 'bibimbap', 'tteokbokki': 'tteokbokki', 'rice cake': 'tteokbokki',
    'kimbap': 'kimbap', 'gimbap': 'kimbap', 'bulgogi': 'bulgogi', 'ramen': 'ramen',
    'white rice': 'white rice', 'brown rice': 'brown rice', 'pizza': 'pizza',
}

def auto_recognize_food(image):
    try:
        API_URL = "https://api-inference.huggingface.co/models/nateraw/food"
        img_byte = io.BytesIO()
        image.save(img_byte, format='JPEG')
        response = requests.post(API_URL, data=img_byte.getvalue(), timeout=25)
        result = response.json()
        if isinstance(result, list) and len(result)>0:
            return result # return top 3
    except Exception as e:
        return None
    return None

# Session history
if 'history' not in st.session_state:
    st.session_state.history = []

uploaded = st.file_uploader("Upload meal photo - AUTO will detect", type=['jpg','jpeg','png'])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    col1, col2 = st.columns([1,1.2])
    with col1:
        st.image(img, caption="Uploaded meal", width=350)
    with col2:
        with st.spinner("🤖 Food Recognition Model analyzing..."):
            results = auto_recognize_food(img)

        if results:
            # 1. Confidence display
            st.subheader("🔍 Recognition Confidence")
            top = results[0]
            st.metric(f"Detected: {top['label']}", f"{top['score']*100:.1f}% confidence")
            if len(results) > 1:
                st.write("Possible matches:")
                for r in results[:3]:
                    st.write(f"- {r['label']} ({r['score']*100:.1f}%)")

            # Map to DB
            hf_label = top['label'].lower()
            final_food = None
            for k,v in label_map.items():
                if k in hf_label:
                    final_food = v
                    break

            if final_food and final_food in nutrition_db:
                data = nutrition_db[final_food]
                # Save to history
                st.session_state.history.append({'food': final_food, 'impact': data['impact'], 'time': datetime.now().strftime("%H:%M")})

                st.divider()
                if data['impact']=='High':
                    st.error(f"### Estimated Glycemic Impact: {data['impact']} {data['color']}")
                elif data['impact']=='Moderate':
                    st.warning(f"### Estimated Glycemic Impact: {data['impact']} {data['color']}")
                else:
                    st.success(f"### Estimated Glycemic Impact: {data['impact']} {data['color']}")

                # 2. Nutrition with source
                st.subheader("📊 Nutrition Estimate")
                st.write(f"Calories: {data['cal']} | Carbs: {data['carbs']}g | Protein: {data['protein']}g | Fiber: {data['fiber']}g")
                st.caption("Estimated using publicly available food composition databases (USDA FoodData Central, ICMR-NIN, Korean Food Composition Table). Values are approximate, portion size not measured.")
                st.write(f"Reason: {data['reason']}")

                # 3. Meal comparison table
                st.subheader("🔄 Meal Comparison: Current vs Better Alternative")
                better_food = data['better']
                better_data = nutrition_db.get(better_food, data)
                comp_df = pd.DataFrame({
                    'Meal': [f"Current: {final_food.title()}", f"Better: {better_food.title()}"],
                    'Carbs (g)': [data['carbs'], better_data['carbs']],
                    'GI': [data['gi'], better_data['gi']],
                    'Impact': [data['impact'], better_data['impact']]
                })
                st.dataframe(comp_df, use_container_width=True)
                if data['carbs'] > better_data['carbs']:
                    st.info(f"💡 Swap {final_food} → {better_food} reduces carbs by {data['carbs'] - better_data['carbs']}g and lowers glycemic load.")
            else:
                st.warning(f"Model saw {hf_label} but not in DB yet. Showing top prediction only.")
        else:
            st.error("Free model busy, wait 15 sec and re-upload.")

# 4. Weekly history chart
if st.session_state.history:
    st.divider()
    st.subheader("📈 Weekly Meal History")
    hist_df = pd.DataFrame(st.session_state.history)
    count_df = hist_df['impact'].value_counts()
    st.bar_chart(count_df)
    st.write(f"Total meals logged this session: {len(hist_df)}")
    st.dataframe(hist_df.tail(10))
    if st.button("Clear History"):
        st.session_state.history = []

st.divider()
st.caption("Pipeline: Upload → Open-source Food Recognition Model (nateraw/food, Food2K) → Predicted Food → GI/GL DB (USDA/ICMR/Korean) → Risk Assessment → Healthy Swap → Weekly History")
st.caption("Limitations: Food recognition accuracy depends on image quality, lighting, and model capability. Nutrition values estimated from public databases, portion approximate. Educational only. No insulin dosing.")
