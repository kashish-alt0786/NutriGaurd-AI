import streamlit as st
from PIL import Image
import pandas as pd
import requests
import io
from datetime import datetime

st.set_page_config(page_title="NutriGuard AI - AUTO Vision", page_icon="🛡️", layout="wide")

# --- Custom CSS for polished UI ---
st.markdown("""
<style>
.metric-card {background: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;}
.high-risk {border-left-color: #f44336!important;}
.moderate-risk {border-left-color: #ff9800!important;}
.low-risk {border-left-color: #4CAF50!important;}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ NutriGuard AI - AUTO Vision")
st.markdown("**Indo-Korean Diabetes Meal AI** | Upload → Auto recognises → No typing needed")
st.error("⚠️ EDUCATIONAL ONLY: Does not replace medical advice. Estimates only. No insulin dosing.")

# --- DB ---
nutrition_db = {
    'cake': {'cal': 400, 'carbs': 80, 'protein': 4, 'fiber': 1, 'sugar': 35, 'gi': 85, 'gl': 40, 'impact': 'High', 'reason': 'Refined flour + sugar', 'better': 'brown rice', 'better_carbs': 38},
    'chapati': {'cal': 120, 'carbs': 15, 'protein': 3, 'fiber': 3, 'sugar': 0.5, 'gi': 45, 'gl': 10, 'impact': 'Low', 'reason': 'Whole wheat fiber', 'better': 'chapati', 'better_carbs': 15},
    'chana masala': {'cal': 280, 'carbs': 30, 'protein': 12, 'fiber': 8, 'sugar': 5, 'gi': 38, 'gl': 12, 'impact': 'Low', 'reason': 'Chickpea protein fiber', 'better': 'chana masala', 'better_carbs': 30},
    'chole bhature': {'cal': 450, 'carbs': 55, 'protein': 10, 'fiber': 6, 'sugar': 4, 'gi': 70, 'gl': 32, 'impact': 'High', 'reason': 'Bhatura deep fried', 'better': 'chana masala', 'better_carbs': 30},
    'samosa': {'cal': 250, 'carbs': 30, 'protein': 4, 'fiber': 2, 'sugar': 1, 'gi': 70, 'gl': 22, 'impact': 'High', 'reason': 'Deep fried maida', 'better': 'chana masala', 'better_carbs': 30},
    'dosa': {'cal': 200, 'carbs': 35, 'protein': 4, 'fiber': 1, 'sugar': 1, 'gi': 65, 'gl': 20, 'impact': 'Moderate', 'reason': 'Rice + lentil fermented', 'better': 'idli', 'better_carbs': 25},
    'idli': {'cal': 150, 'carbs': 25, 'protein': 5, 'fiber': 2, 'sugar': 0.5, 'gi': 50, 'gl': 12, 'impact': 'Low', 'reason': 'Steamed fermented', 'better': 'idli', 'better_carbs': 25},
    'biryani': {'cal': 380, 'carbs': 50, 'protein': 10, 'fiber': 3, 'sugar': 2, 'gi': 60, 'gl': 25, 'impact': 'Moderate', 'reason': 'Rice + oil', 'better': 'brown rice', 'better_carbs': 38},
    'kimchi': {'cal': 20, 'carbs': 2, 'protein': 1, 'fiber': 1, 'sugar': 1, 'gi': 15, 'gl': 1, 'impact': 'Low', 'reason': 'Fermented low carb', 'better': 'kimchi', 'better_carbs': 2},
    'bibimbap': {'cal': 350, 'carbs': 50, 'protein': 13, 'fiber': 6, 'sugar': 2, 'gi': 50, 'gl': 18, 'impact': 'Moderate', 'reason': 'Mixed rice veggies', 'better': 'brown rice bibimbap', 'better_carbs': 38},
    'tteokbokki': {'cal': 350, 'carbs': 80, 'protein': 4, 'fiber': 1, 'sugar': 15, 'gi': 85, 'gl': 40, 'impact': 'High', 'reason': 'Rice cake sweet sauce', 'better': 'kimchi', 'better_carbs': 2},
    'kimbap': {'cal': 300, 'carbs': 45, 'protein': 8, 'fiber': 3, 'sugar': 2, 'gi': 60, 'gl': 20, 'impact': 'Moderate', 'reason': 'Rice + seaweed', 'better': 'bibimbap', 'better_carbs': 50},
    'white rice': {'cal': 200, 'carbs': 45, 'protein': 3, 'fiber': 0, 'sugar': 0, 'gi': 80, 'gl': 30, 'impact': 'High', 'reason': 'Refined grain low fiber', 'better': 'brown rice', 'better_carbs': 38},
    'brown rice': {'cal': 180, 'carbs': 38, 'protein': 4, 'fiber': 3, 'sugar': 0, 'gi': 50, 'gl': 16, 'impact': 'Low', 'reason': 'Whole grain fiber', 'better': 'brown rice', 'better_carbs': 38},
}

label_map = {
    'birthday cake': 'cake', 'chocolate cake': 'cake', 'cake': 'cake',
    'chana masala': 'chana masala', 'chole': 'chole bhature',
    'samosa': 'samosa', 'dosa': 'dosa', 'idli': 'idli', 'biryani': 'biryani',
    'kimchi': 'kimchi', 'bibimbap': 'bibimbap', 'tteokbokki': 'tteokbokki', 'rice cake': 'tteokbokki',
    'kimbap': 'kimbap', 'gimbap': 'kimbap', 'white rice': 'white rice', 'brown rice': 'brown rice',
}

def auto_recognize_food(image):
    try:
        API_URL = "https://api-inference.huggingface.co/models/nateraw/food"
        img_byte = io.BytesIO()
        image.save(img_byte, format='JPEG')
        response = requests.post(API_URL, data=img_byte.getvalue(), timeout=25)
        result = response.json()
        if isinstance(result, list) and len(result)>0:
            return result
    except:
        return None
    return None

if 'history' not in st.session_state:
    st.session_state.history = []

# Upload
uploaded = st.file_uploader("Upload meal photo - AUTO will detect", type=['jpg','jpeg','png'])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    col1, col2 = st.columns([1,1.3], gap="large")
    with col1:
        st.image(img, caption="Uploaded meal", use_container_width=True)
        st.caption("**Limitations:** Image quality affects recognition. Nutrition values are estimates. Portion approx. Educational use only.")

    with col2:
        with st.spinner("🤖 Analyzing with open-source Food Recognition Model..."):
            results = auto_recognize_food(img)

        if results:
            # 1. Confidence Score + Possible matches
            st.subheader("🔍 Estimated Food Identification")
            st.caption("Recognition confidence depends on image quality, lighting, and angle.")
            top = results[0]
            st.markdown(f"""
            <div class="metric-card {'high-risk' if nutrition_db.get(label_map.get(top['label'].lower(),''),{}).get('impact')=='High' else 'low-risk'}">
            <b>Detected:</b> {top['label'].title()}<br>
            <b>Confidence:</b> {top['score']*100:.1f}%
            </div>
            """, unsafe_allow_html=True)

            st.write("**Possible matches:**")
            for r in results[:3]:
                st.write(f"• {r['label'].title()} — {r['score']*100:.1f}%")

            # Map
            hf_label = top['label'].lower()
            final_food = None
            for k,v in label_map.items():
                if k in hf_label:
                    final_food = v
                    break

            if final_food in nutrition_db:
                data = nutrition_db[final_food]
                st.session_state.history.append({'food': final_food, 'impact': data['impact'], 'time': datetime.now().strftime("%H:%M")})

                st.divider()
                # Risk
                if data['impact']=='High':
                    st.error(f"### Estimated Glycemic Impact: {data['impact']} 🔴")
                elif data['impact']=='Moderate':
                    st.warning(f"### Estimated Glycemic Impact: {data['impact']} 🟡")
                else:
                    st.success(f"### Estimated Glycemic Impact: {data['impact']} 🟢")

                # 2. Cite nutrition sources
                st.subheader("📊 Nutrition Estimate")
                st.write(f"**Calories:** {data['cal']} | **Carbs:** {data['carbs']}g | **Protein:** {data['protein']}g | **Fiber:** {data['fiber']}g | **GI:** {data['gi']}")
                st.info("Nutritional values are estimated using publicly available food composition databases including USDA FoodData Central, ICMR-NIN (Indian Food Composition Tables), and Korean Food Composition Database (RDA). Values are approximate and depend on portion size.")
                st.write(f"**Reason:** {data['reason']}")

                # 3. Meal comparison
                st.subheader("🔄 Meal Comparison")
                better_food = data['better']
                better_data = nutrition_db.get(better_food, data)
                comp_df = pd.DataFrame({
                    '': ['Current Meal', 'Better Alternative'],
                    'Meal': [final_food.title(), better_food.title()],
                    'Carbs': [f"{data['carbs']}g", f"{better_data['carbs']}g"],
                    'GI': [data['gi'], better_data['gi']],
                    'Impact': [data['impact'], better_data['impact']]
                })
                st.dataframe(comp_df, use_container_width=True, hide_index=True)
            else:
                st.warning(f"Model identified {hf_label.title()} but not in nutrition DB yet.")
        else:
            st.error("Free model busy — wait 15 sec and re-upload. Normal for free Hugging Face API.")

# 4. Weekly history
if st.session_state.history:
    st.divider()
    st.subheader("📈 Weekly Meal History")
    hist_df = pd.DataFrame(st.session_state.history)
    st.bar_chart(hist_df['impact'].value_counts())
    st.dataframe(hist_df.tail(10), use_container_width=True)

st.divider()
st.markdown("**Pipeline:** Upload → Open-source Food Recognition Model (nateraw/food, Food2K) → Predicted Food → GI/GL DB (USDA/ICMR/Korean) → Risk Assessment → Healthy Swap → Weekly History")
st.markdown("""
**Limitations & Ethics:**
- Image quality affects recognition accuracy
- Nutrition values are estimates from public databases
- Portion estimation is approximate
- Educational use only, no medical diagnosis or insulin dosing
""")
