def detect_api_type(key):
    if key.startswith("gk-") or key.startswith("AIza"):
        return "Google Gemini"
    if key.startswith("anthropic-"):
        return "Anthropic"
    if key.startswith("gsk_"):
        return "Groq"
    if key.startswith("mistral-"):
        return "Mistral"
    if key.startswith("ds-"):
        return "DeepSeek"
    if key.startswith("sk-or-"):
        return "OpenRouter"
    return "Unknown"


def get_test_url(api_type, key):

    # --- GEMINI ---
    if api_type == "Google Gemini":
        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}",
            {},
            {"contents": [{"parts": [{"text": "hi"}]}]},
        )

    # --- ANTHROPIC ---
    if api_type == "Anthropic":
        return (
            "https://api.anthropic.com/v1/messages",
            {
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
            {"model": "claude-3-haiku-20240307", "messages": [{"role": "user", "content": "hi"}]},
        )

    # --- GROQ ---
    if api_type == "Groq":
        return (
            "https://api.groq.com/openai/v1/chat/completions",
            {"Authorization": f"Bearer {key}"},
            {"model": "mixtral-8x7b-32768", "messages": [{"role": "user", "content": "hi"}]},
        )

    # --- MISTRAL ---
    if api_type == "Mistral":
        return (
            "https://api.mistral.ai/v1/chat/completions",
            {"Authorization": f"Bearer {key}"},
            {"model": "mistral-small", "messages": [{"role": "user", "content": "hi"}]},
        )

    # --- DEEPSEEK ---
    if api_type == "DeepSeek":
        return (
            "https://api.deepseek.com/v1/chat/completions",
            {"Authorization": f"Bearer {key}"},
            {"model": "deepseek-chat", "messages": [{"role": "user", "content": "hi"}]},
        )

    # --- OPENROUTER ---
    if api_type == "OpenRouter":
        return (
            "https://openrouter.ai/api/v1/chat/completions",
            {"Authorization": f"Bearer {key}"},
            {"model": "mistralai/mistral-7b-instruct", "messages": [{"role": "user", "content": "hi"}]},
        )

    # UNKNOWN → default endpoint
    return (
        "https://httpbin.org/status/200",
        {},
        {},
    )
