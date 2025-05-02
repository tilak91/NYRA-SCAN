import streamlit as st
import pandas as pd
import requests
import tempfile
import urllib.request

# CONFIG
st.set_page_config(page_title="🎉 QR Verifier", page_icon="🔍")
st.title("🎉 Freshers Fest QR Verifier")

# URL of Excel on GitHub
EXCEL_URL = "https://raw.githubusercontent.com/tilak91/NYRA-SCAN/main/freshers_data.xlsx"

@st.cache_data
def load_excel_data():
    try:
        with urllib.request.urlopen(EXCEL_URL) as response:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                tmp_file.write(response.read())
                df = pd.read_excel(tmp_file.name)
        return df
    except Exception as e:
        st.error(f"Error loading Excel: {e}")
        return pd.DataFrame()

df = load_excel_data()

st.subheader("📸 Scan QR Code using Webcam")
qr_image = st.camera_input("Use your phone camera or webcam")

if qr_image is not None:
    st.image(qr_image, caption="Scanned QR", width=250)

    files = {'file': qr_image.getvalue()}
    api_url = "https://api.qrserver.com/v1/read-qr-code/"
    response = requests.post(api_url, files=files)

    try:
        qr_data = response.json()[0]['symbol'][0]['data']
        if qr_data:
            st.success(f"✅ QR Code Data: {qr_data}")
            match = df[df['Virtual Pass ID'] == qr_data]
            if not match.empty:
                st.success("🎟 Valid Entry Pass!")
                st.write(f"👤 Name: **{match.iloc[0]['Name']}**")
                st.write(f"🎓 Roll No: **{match.iloc[0]['Roll No']}**")
                st.write(f"🏫 Branch: **{match.iloc[0]['Branch']}**")
                st.write(f"📅 Year: **{match.iloc[0]['Year']}**")
                
            else:
                st.error("❌ Invalid Pass! Entry Denied.")
        else:
            st.error("⚠️ No data found in QR Code.")
    except Exception as e:
        st.error(f"Error decoding QR: {e}")
