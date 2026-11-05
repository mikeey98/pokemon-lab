import requests

OLLAMA_URL = "http://localhost:11434"


def ollama_is_running() -> bool:
    """Ollama only exists on the user's own computer, not in the online version."""
    try:
        return requests.get(f"{OLLAMA_URL}/api/tags", timeout=2).ok
    except requests.RequestException:
        return False


def ask_qwen(
    facts: str,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> str:
    instructions = (
        "You are a friendly Pokémon fan. Answer in English.\n"
        "Use the Pokémon facts below for factual questions. "
        "Never invent facts or claim that a guess is official Pokémon lore.\n"
        "If the user asks what you think, imagine, or guess, give a short, "
        "playful answer inspired by the Pokémon's types and stats. "
        "Make clear that it is just your imagination.\n"
        "If the user asks for an unknown fact, say you don't know.\n\n"
        f"Pokémon facts:\n{facts}"
    )

    messages = [
        {"role": "system", "content": instructions},
        *(history or []),
        {"role": "user", "content": question},
    ]

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": "qwen3:1.7b",
            "messages": messages,
            "stream": False,
            "think": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]
