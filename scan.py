import streamlit as st
import pandas as pd
from PIL import Image
import urllib.request
import tempfile
import requests

st.set_page_config(page_title="QR Pass Verifier", page_icon="🔍")
st.title("🔍 Freshers Fest QR Code Verifier")

EXCEL_URL = "https://raw.githubusercontent.com/tilak91/NYRA-SCAN/main/freshers_data.xlsx"


@st.cache_data
def load_data_from_github():
    try:
        with urllib.request.urlopen(EXCEL_URL) as response:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                tmp_file.write(response.read())
                df = pd.read_excel(tmp_file.name)
        return df
    except Exception as e:
        st.error(f"Error loading Excel from GitHub: {e}")
        return pd.DataFrame()

df = load_data_from_github()

st.subheader("📁 Upload QR Code Image")
qr_file = st.file_uploader("Upload QR Code Image (JPG, PNG, JPEG)", type=['jpg', 'jpeg', 'png'])

if qr_file is not None:
    img = Image.open(qr_file)
    st.image(img, caption="Uploaded QR", width=250)

    # Send to QR decoding API
    files = {'file': qr_file.getvalue()}
    api_url = "https://api.qrserver.com/v1/read-qr-code/"
    response = requests.post(api_url, files=files)

    try:
        qr_data = response.json()[0]['symbol'][0]['data']
        if qr_data:
            st.success(f"✅ QR Code Scanned: {qr_data}")
            match = df[df['Virtual Pass ID'] == qr_data]
            if not match.empty:
                st.success("🎉 Valid Pass! Entry Allowed.")
                st.write(f"**Name:** {match.iloc[0]['Name']}")
                st.write(f"**Roll No:** {match.iloc[0]['Roll No']}")
                st.write(f"**Branch:** {match.iloc[0]['Branch']}")
                st.write(f"**Year:** {match.iloc[0]['Year']}")
            else:
                st.error("❌ Invalid Pass! Entry Denied.")
        else:
            st.error("⚠️ Could not decode QR code. Try again.")
    except Exception as e:
        st.error(f"Error decoding QR code: {e}")
