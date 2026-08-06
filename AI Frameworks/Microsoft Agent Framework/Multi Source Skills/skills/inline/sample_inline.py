from providers.inline_provider import register_inline_skill

@register_inline_skill(
    name="math_add",
    description="Adds two numbers together.",
    parameters={
        "a": {"type": "number", "description": "The first number"},
        "b": {"type": "number", "description": "The second number"}
    }
)
def add_numbers(a: float, b: float) -> float:
    return a + b

@register_inline_skill(
    name="translate",
    description="Translates text from English to another language.",
    parameters={
        "text": {"type": "string", "description": "The text to translate"},
        "language": {"type": "string", "description": "The target language (e.g. Spanish, French)"}
    }
)
def translate_text(text: str, language: str) -> str:
    # Dummy implementation for illustration
    translations = {
        "spanish": f"[Spanish] {text} - traducido",
        "french": f"[French] {text} - traduit",
        "german": f"[German] {text} - übersetzt"
    }
    return translations.get(language.lower(), f"[{language}] {text} (mock translation)")

@register_inline_skill(
    name="search_skill",
    description="Search the web (Inline implementation)",
    parameters={
        "query": {"type": "string", "description": "The query to search for"}
    }
)
def inline_search(query: str) -> str:
    return f"Inline Search results for: '{query}'"
