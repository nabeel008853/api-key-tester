API_LIST = [
    {
        "name": "OpenRouter",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "payload": {"model": "mistralai/mistral-7b-instruct", "messages": [{"role": "user", "content": "hi"}]},
    },
    {
        "name": "Groq",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "payload": {"model": "mixtral-8x7b-32768", "messages": [{"role": "user", "content": "hi"}]},
    },
    {
        "name": "Google Gemini",
        "url": None,  # handled separately
        "headers": lambda key: {},
        "payload": None,
    },
    {
        "name": "Anthropic",
        "url": "https://api.anthropic.com/v1/messages",
        "headers": lambda key: {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
        "payload": {"model": "claude-3-haiku-20240307", "messages": [{"role": "user", "content": "hi"}]},
    },
    {
        "name": "Mistral",
        "url": "https://api.mistral.ai/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "payload": {"model": "mistral-small", "messages": [{"role": "user", "content": "hi"}]},
    },
    {
        "name": "DeepSeek",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "payload": {"model": "deepseek-chat", "messages": [{"role": "user", "content": "hi"}]},
    },
]


def get_api_tests(key):
    tests = []

    for api in API_LIST:

        # GEMINI uses GET request
        if api["name"] == "Google Gemini":
            tests.append({
                "api": api["name"],
                "method": "GET",
                "url": f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
                "headers": {},
                "payload": None,
            })
        else:
            tests.append({
                "api": api["name"],
                "method": "POST",
                "url": api["url"],
                "headers": api["headers"](key),
                "payload": api["payload"],
            })

    return tests
