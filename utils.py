def detect_api_type(key):
    if key.startswith("sk-"):
        return "OpenAI / Compatible"
    if key.startswith("gk-"):
        return "Google Gemini"
    if key.startswith("anthropic-"):
        return "Anthropic"
    if key.startswith("gsk_"):
        return "Groq"
    return "Unknown"


def get_test_url(api_type, key):
    if api_type == "OpenAI / Compatible":
        return (
            "https://api.openai.com/v1/chat/completions",
            {"Authorization": f"Bearer {key}"},
            {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}]}
        )

    if api_type == "Google Gemini":
        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}",
            {},
            {"contents": [{"parts": [{"text": "hi"}]}]}
        )

    if api_type == "Anthropic":
        return (
            "https://api.anthropic.com/v1/messages",
            {
                "x-api-key": key,
                "anthropic-version": "2023-06-01"
            },
            {"model": "claude-3-haiku-20240307", "messages": [{"role": "user", "content": "hi"}]}
        )

    if api_type == "Groq":
        return (
            "https://api.groq.com/openai/v1/chat/completions",
            {"Authorization": f"Bearer {key}"},
            {"model": "mixtral-8x7b-32768", "messages": [{"role": "user", "content": "hi"}]}
        )

    return (
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {key}"},
        {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}]}
    )
