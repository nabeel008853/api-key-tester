import streamlit as st
import requests

st.set_page_config(page_title="Universal API Key Tester", layout="centered")

st.title("🔑 Universal API Key Tester + Chat Client")

# -------------------------------
# Detect API Type
# -------------------------------
def detect_api_type(key: str) -> str:
    key = key.strip().lower()

    if key.startswith("sk-"):
        return "openai-like"

    if key.startswith("g-") or key.startswith("ai"):
        return "google-gemini"

    if key.startswith("hf_"):
        return "huggingface"

    if len(key) > 20:
        return "unknown-maybe-valid"

    return "unknown"


# -------------------------------
# Validate API Key
# -------------------------------
def validate_key(api_key: str, api_type: str):
    try:
        if api_type == "openai-like":
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            res = requests.get("https://api.openai.com/v1/models", headers=headers)
            if res.status_code == 200:
                return "valid", res.json()
            elif res.status_code == 401:
                return "invalid", None
            else:
                return "unknown", res.text

        elif api_type == "google-gemini":
            res = requests.get(
                f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
            )
            if res.status_code == 200:
                return "valid", res.json()
            elif res.status_code == 403:
                return "invalid", None
            else:
                return "unknown", res.text

        elif api_type == "huggingface":
            headers = {"Authorization": f"Bearer {api_key}"}
            res = requests.get("https://api.huggingface.co/models", headers=headers)
            if res.status_code == 200:
                return "valid", res.json()
            elif res.status_code == 401:
                return "invalid", None
            else:
                return "unknown", res.text

        elif api_type == "unknown-maybe-valid":
            # Unknown API provider → cannot verify
            return "unknown", None

        else:
            return "unknown", None

    except Exception as e:
        return "unknown", str(e)


# -------------------------------
# Chat Function for Valid Keys
# -------------------------------
def chat_with_api(api_key: str, api_type: str, user_msg: str):
    try:
        if api_type == "openai-like":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}"}
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": user_msg}],
            }
            res = requests.post(url, json=data, headers=headers)
            return res.json()

        elif api_type == "google-gemini":
            url = (
                f"https://generativelanguage.googleapis.com/v1/models/"
                "gemini-pro:generateContent?key=" + api_key
            )
            data = {
                "contents": [{"parts": [{"text": user_msg}]}]
            }
            res = requests.post(url, json=data)
            return res.json()

        elif api_type == "huggingface":
            url = "https://api.huggingface.co/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}"}
            data = {
                "model": "HuggingFaceH4/zephyr-7b-beta",
                "messages": [{"role": "user", "content": user_msg}],
            }
            res = requests.post(url, json=data, headers=headers)
            return res.json()

        return {"error": "Unknown API type, cannot chat"}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# UI
# -------------------------------
api_key = st.text_input("Enter API Key", type="password")

if st.button("🔍 Test Key"):
    if not api_key:
        st.warning("Please enter an API key.")
    else:
        api_type = detect_api_type(api_key)
        status, data = validate_key(api_key, api_type)

        st.subheader("🔎 Detection Result")
        st.write(f"**API Type:** {api_type}")

        if status == "valid":
            st.success("✅ VALID KEY")

        elif status == "invalid":
            st.error("❌ INVALID KEY")

        else:
            st.warning("⚠️ UNKNOWN — API does not match any known provider, might still be valid for other services.")

        if data:
            st.json(data)

        st.session_state["api_key"] = api_key
        st.session_state["api_type"] = api_type


# -------------------------------
# Chat UI (only if valid)
# -------------------------------
if "api_key" in st.session_state:
    st.markdown("---")
    st.subheader("💬 Test Chat (for valid keys)")

    user_message = st.text_input("Send a message:")

    if st.button("Send"):
        response = chat_with_api(
            st.session_state["api_key"],
            st.session_state["api_type"],
            user_message,
        )
        st.write("### Response:")
        st.json(response)
