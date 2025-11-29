import streamlit as st
import requests
import re

st.set_page_config(page_title="Universal API Key Checker", layout="centered")

# -------------------------------
# Pattern Detection
# -------------------------------
def detect_key_type(key):
    if key.startswith("sk-") and len(key) > 20:
        return "openai"
    if key.startswith("or-"):
        return "openrouter"
    if key.startswith("AI") or key.startswith("g-"):
        return "gemini"
    return "unknown"

# -------------------------------
# Check OpenAI Key
# -------------------------------
def check_openai(key):
    try:
        r = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {key}"}
        )
        if r.status_code == 200:
            return "VALID"
        if r.status_code in [401, 403]:
            return "INVALID"
        return "UNKNOWN"
    except:
        return "UNKNOWN"

# -------------------------------
# OpenRouter Key Check
# -------------------------------
def check_openrouter(key):
    try:
        r = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {key}"}
        )
        if r.status_code == 200:
            return "VALID"
        if r.status_code in [401, 403]:
            return "INVALID"
        return "UNKNOWN"
    except:
        return "UNKNOWN"

# -------------------------------
# Gemini Key Check
# -------------------------------
def check_gemini(key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models?key={key}"
        r = requests.get(url)
        if r.status_code == 200:
            return "VALID"
        if r.status_code in [400, 401, 403]:
            return "INVALID"
        return "UNKNOWN"
    except:
        return "UNKNOWN"

# -------------------------------
# UNKNOWN type simple check
# -------------------------------
def check_unknown_key(key):
    """
    Always return UNKNOWN because no API type detected.
    """
    return "UNKNOWN"

# -------------------------------
# MAIN CHECK FUNCTION
# -------------------------------
def check_key(key):
    key_type = detect_key_type(key)

    if key_type == "openai":
        return "OpenAI", check_openai(key)
    if key_type == "openrouter":
        return "OpenRouter", check_openrouter(key)
    if key_type == "gemini":
        return "Gemini", check_gemini(key)

    # Fallback
    return "Unknown", check_unknown_key(key)

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.title("🔑 Universal API Key Validator")
st.write("Paste **any** key — OpenAI, OpenRouter, Gemini, or unknown type.")

keys_input = st.text_area(
    "Enter multiple keys (each on new line):",
    height=250,
    placeholder="sk-xxxxxxxxx\nor-xxxxxxxx\nAIxxxxxxxxxxx\nabcd1234..."
)

if st.button("Check Keys"):
    if not keys_input.strip():
        st.warning("Enter at least one API key.")
    else:
        keys = keys_input.strip().split("\n")

        result_table = []

        for k in keys:
            clean = k.strip()
            if clean == "":
                continue

            key_type, status = check_key(clean)
            result_table.append([clean[:10] + "..." if len(clean) > 13 else clean, key_type, status])

        st.subheader("Results")
        st.table(
            {
                "Key": [r[0] for r in result_table],
                "API Type": [r[1] for r in result_table],
                "Status": [r[2] for r in result_table],
            }
        )
