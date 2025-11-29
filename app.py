import streamlit as st
import pandas as pd
import requests
import asyncio
import aiohttp
from utils import detect_api_type, get_test_url

st.set_page_config(page_title="Advanced API Key Tester", page_icon="🔑", layout="wide")

st.title("🔑 Advanced API Key Tester (Multi-API, Parallel, Fast)")

# -------------------------
# LOGIN SYSTEM (Optional)
# -------------------------
password = "admin123"  # Change this!
auth = st.sidebar.text_input("Enter Password", type="password")

if auth != password:
    st.warning("🔐 Please enter password to access the tester.")
    st.stop()

# -------------------------
# INPUT
# -------------------------
input_mode = st.radio("Input Mode", ["Paste Keys", "Upload File"])

keys = []

if input_mode == "Paste Keys":
    paste = st.text_area("Paste API keys (one per line)")
    if paste:
        keys = [k.strip() for k in paste.splitlines() if k.strip()]

else:
    file = st.file_uploader("Upload .txt file with keys")
    if file:
        keys = file.read().decode().splitlines()

if not keys:
    st.info("Waiting for keys...")
    st.stop()

# -------------------------
# ASYNC TEST FUNCTION
# -------------------------
async def test_key(session, key):
    api_type = detect_api_type(key)
    url, headers, payload = get_test_url(api_type, key)

    try:
        async with session.post(url, json=payload, headers=headers, timeout=10) as res:
            status = res.status
            if status == 200:
                return key, api_type, "VALID"
            elif status == 401:
                return key, api_type, "INVALID"
            elif status == 429:
                return key, api_type, "RATE LIMITED"
            else:
                return key, api_type, f"ERROR {status}"
    except Exception as e:
        return key, api_type, f"Error: {str(e)}"


# -------------------------
# RUN PARALLEL TESTING
# -------------------------
async def run_tests(keys):
    async with aiohttp.ClientSession() as session:
        tasks = [test_key(session, key) for key in keys]
        return await asyncio.gather(*tasks)


if st.button("🚀 Test All Keys"):
    with st.spinner("Testing keys..."):
        results = asyncio.run(run_tests(keys))

    df = pd.DataFrame(results, columns=["Key", "API Type", "Status"])
    st.success("Completed!")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode()
    st.download_button("Download Results CSV", csv, "results.csv", "text/csv")
