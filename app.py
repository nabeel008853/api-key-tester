import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from utils import get_api_tests

st.set_page_config(page_title="Multi-API Key Tester", page_icon="🔑", layout="wide")

st.title("🔑 Multi-API Key Tester (Auto Detection, Correct Status)")
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
    key_worked = False

    for t in tests:
        try:
            if t["method"] == "GET":
                async with session.get(t["url"], headers=t["headers"], timeout=10) as res:
                    status = res.status
            else:
                async with session.post(t["url"], headers=t["headers"], json=t["payload"], timeout=10) as res:
                    status = res.status

            if status == 200:
                return key, t["api"], "VALID"

            if status == 429:
                return key, t["api"], "RATE LIMITED"

            if status == 401:
                continue  # invalid for this provider → try next

        except Exception:
            continue  # skip errors

    # If no provider returned valid or rate limited, mark as INVALID
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
    with st.spinner("Testing in progress..."):
        results = asyncio.run(run_tests(keys))

    df = pd.DataFrame(results, columns=["API Key", "Detected API", "Status"])
    st.success("Testing Complete!")
    st.dataframe(df, height=450)

    # Highlight VALID vs INVALID vs RATE LIMITED
    def color_status(val):
        if val == "VALID":
            return 'background-color: #b6fcb6'
        elif val == "INVALID":
            return 'background-color: #ffb6b6'
        elif val == "RATE LIMITED":
            return 'background-color: #fff3b6'
        else:
            return ''

    st.dataframe(df.style.applymap(color_status, subset=["Status"]))

    csv = df.to_csv(index=False).encode()
    st.download_button("📥 Download Results CSV", csv, "results.csv", "text/csv")
