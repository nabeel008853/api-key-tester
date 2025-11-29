import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from utils import get_api_tests

st.set_page_config(page_title="Multi-API Key Tester", page_icon="🔑", layout="wide")

st.title("🔑 Multi-API Key Tester (Full Detection, All Providers)")
st.write("Tests: OpenRouter, Groq, Gemini, Anthropic, Mistral, DeepSeek — fully automatic.")

# -------------------------
# INPUT SECTION
# -------------------------
mode = st.radio("Choose Input Method", ["Paste Keys", "Upload File"])

keys = []

if mode == "Paste Keys":
    data = st.text_area("Paste API keys (one per line)", height=200)
    if data:
        keys = [k.strip() for k in data.splitlines() if k.strip()]
else:
    uploaded = st.file_uploader("Upload a .txt file containing keys")
    if uploaded:
        keys = uploaded.read().decode().splitlines()

if not keys:
    st.info("Waiting for API keys...")
    st.stop()

# -------------------------
# TEST ONE KEY
# -------------------------
async def test_key(session, key):
    tests = get_api_tests(key)

    for t in tests:
        try:
            if t["method"] == "GET":
                async with session.get(t["url"], headers=t["headers"], timeout=10) as res:
                    status = res.status
            else:
                async with session.post(t["url"], headers=t["headers"], json=t["payload"], timeout=10) as res:
                    status = res.status

            api_detected = t["api"]

            if status == 200:
                return key, api_detected, "VALID"
            elif status == 429:
                return key, api_detected, "RATE LIMITED"
            elif status == 401:
                return key, api_detected, "INVALID"
            else:
                return key, api_detected, f"ERROR {status}"

        except Exception:
            continue  # try next API

    # Truly unknown if no API responds
    return key, "Unknown", "INVALID"

# -------------------------
# RUN ALL TESTS
# -------------------------
async def run_tests(all_keys):
    async with aiohttp.ClientSession() as session:
        tasks = [test_key(session, key) for key in all_keys]
        return await asyncio.gather(*tasks)

# -------------------------
# START TESTING
# -------------------------
if st.button("🚀 Start Testing All Keys"):
    with st.spinner("Testing keys..."):
        results = asyncio.run(run_tests(keys))

    df = pd.DataFrame(results, columns=["API Key", "Detected API", "Status"])
    st.success("Testing Complete!")

    # Color-code status
    def color_status(val):
        if val == "VALID":
            return 'background-color: #b6fcb6'
        elif val == "INVALID":
            return 'background-color: #ffb6b6'
        elif val == "RATE LIMITED":
            return 'background-color: #fff3b6'
        else:
            return ''

    st.dataframe(df.style.applymap(color_status, subset=["Status"]), height=450)

    csv = df.to_csv(index=False).encode()
    st.download_button("📥 Download Results CSV", csv, "results.csv", "text/csv")
