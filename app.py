import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from utils import detect_api_type, get_test_url

st.set_page_config(page_title="Multi-API Key Tester", page_icon="🔑", layout="wide")

st.title("🔑 Multi-API Key Tester (No OpenAI)")

st.write("Supports OpenRouter, Gemini, Anthropic, Groq, Mistral, DeepSeek, Custom APIs.")

# ---- INPUT ----
mode = st.radio("Input Mode", ["Paste Keys", "Upload File"])
keys = []

if mode == "Paste Keys":
    data = st.text_area("Paste API keys (one per line)")
    if data:
        keys = [k.strip() for k in data.splitlines() if k.strip()]
else:
    file = st.file_uploader("Upload .txt key file")
    if file:
        keys = file.read().decode().splitlines()

if not keys:
    st.info("Waiting for keys...")
    st.stop()

# ---- ASYNC TEST ----
async def test_key(session, key):
    api_type = detect_api_type(key)
    url, headers, payload = get_test_url(api_type, key)

    try:
        async with session.post(url, headers=headers, json=payload, timeout=10) as res:
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
        return key, api_type, f"ERROR: {str(e)}"


async def run(keys):
    async with aiohttp.ClientSession() as session:
        tasks = [test_key(session, key) for key in keys]
        return await asyncio.gather(*tasks)


# ---- RUN ----
if st.button("Test All Keys"):
    with st.spinner("Testing keys..."):
        results = asyncio.run(run(keys))

    df = pd.DataFrame(results, columns=["Key", "API Type", "Status"])
    st.success("DONE")
    st.dataframe(df)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode(),
        "results.csv",
        "text/csv",
    )
