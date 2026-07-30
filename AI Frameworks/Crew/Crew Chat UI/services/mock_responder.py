import re
import random
from typing import Dict, List, Callable


def _respond_greeting(q: str) -> str | None:
    if re.search(r"\b(hi|hello|hey|greetings|sup|howdy)\b", q, re.IGNORECASE):
        return (
            "Hello! I'm your CrewAI-powered assistant. I can help you with:\n\n"
            "- **Research** — Gather and organize information\n"
            "- **Analysis** — Extract insights from data\n"
            "- **Writing** — Draft content, reports, and code\n"
            "- **Brainstorming** — Generate creative ideas\n\n"
            "What would you like to explore today?"
        )
    return None


def _respond_how_are_you(q: str) -> str | None:
    if re.search(r"\bhow (are|'re) you\b", q, re.IGNORECASE):
        return (
            "I'm functioning optimally, thank you! I'm powered by CrewAI with "
            "three specialized agents working together to assist you:\n\n"
            "1. **🔍 Research Specialist** — Gathers relevant information\n"
            "2. **📊 Analysis Expert** — Extracts insights\n"
            "3. **✍️ Response Writer** — Crafts final responses\n\n"
            "How can I help you today?"
        )
    return None


def _respond_crewai(q: str) -> str | None:
    if re.search(r"\b(crewai|crew.?ai)\b", q, re.IGNORECASE):
        return (
            "## What is CrewAI?\n\n"
            "CrewAI is a framework for orchestrating autonomous AI agents. "
            "It enables multiple AI agents to collaborate on complex tasks.\n\n"
            "### Key Features:\n"
            "- **Role-based agents** — Each agent has a specific role and goal\n"
            "- **Task delegation** — Agents work sequentially or hierarchically\n"
            "- **Tool integration** — Agents can use various tools\n"
            "- **Process control** — Define how agents collaborate\n\n"
            "### Example Use Cases:\n"
            "- Research & report generation\n"
            "- Code review & debugging\n"
            "- Content creation & editing\n"
            "- Data analysis & visualization\n\n"
            "Would you like me to demonstrate any specific capability?"
        )
    return None


def _respond_code(q: str) -> str | None:
    if re.search(r"\b(code|program|function|script|python|javascript)\b", q, re.IGNORECASE):
        return (
            "Here's an example of a well-structured Python function:\n\n"
            "```python\n"
            "from typing import List, Optional\n\n"
            "def calculate_statistics(numbers: List[float]) -> dict:\n"
            "    \"\"\"\n"
            "    Calculate basic statistics for a list of numbers.\n\n"
            "    Args:\n"
            "        numbers: A list of numeric values\n\n"
            "    Returns:\n"
            "        dict: Statistical summary with mean, median, min, max, std\n"
            "    \"\"\"\n"
            "    if not numbers:\n"
            "        return {'error': 'Empty list provided'}\n\n"
            "    n = len(numbers)\n"
            "    mean = sum(numbers) / n\n"
            "    sorted_nums = sorted(numbers)\n"
            "    median = sorted_nums[n // 2] if n % 2 else (\n"
            "        sorted_nums[n // 2 - 1] + sorted_nums[n // 2]\n"
            "    ) / 2\n\n"
            "    variance = sum((x - mean) ** 2 for x in numbers) / n\n"
            "    std_dev = variance ** 0.5\n\n"
            "    return {\n"
            "        'mean': round(mean, 2),\n"
            "        'median': round(median, 2),\n"
            "        'min': min(numbers),\n"
            "        'max': max(numbers),\n"
            "        'std_dev': round(std_dev, 2),\n"
            "        'count': n,\n"
            "    }\n"
            "```\n\n"
            "This function handles edge cases (empty list) and returns "
            "a comprehensive statistical summary. Would you like me to "
            "explain any part in more detail?"
        )
    return None


def _respond_analysis(q: str) -> str | None:
    if re.search(r"\b(analyz|compare|contrast|difference|explain|what is)\b", q, re.IGNORECASE):
        return None

    return None


def _respond_default(q: str) -> str:
    responses = [
        (
            "That's an interesting question! Let me share my perspective.\n\n"
            "Based on my analysis, here are the key points to consider:\n\n"
            "1. **Context matters** — The answer depends on your specific use case\n"
            "2. **Multiple approaches** — There are several valid ways to address this\n"
            "3. **Best practices** — Industry standards suggest starting simple\n\n"
            "Could you provide more context? I'll give you a more tailored response."
        ),
        (
            "Great question! Here's what I found:\n\n"
            "### Key Insights:\n"
            "- This topic involves several interconnected factors\n"
            "- The most effective approach balances trade-offs\n"
            "- Recent developments have opened new possibilities\n\n"
            "### Recommended Next Steps:\n"
            "1. Define your specific requirements\n"
            "2. Evaluate available options\n"
            "3. Start with a prototype\n"
            "4. Iterate based on feedback\n\n"
            "Would you like me to elaborate on any of these points?"
        ),
        (
            "I've analyzed your query thoroughly. Here's a comprehensive response:\n\n"
            "## Overview\n"
            "The subject you're asking about has several important dimensions.\n\n"
            "## Key Considerations\n"
            "- **Efficiency**: Optimize for your specific constraints\n"
            "- **Scalability**: Plan for growth from the start\n"
            "- **Maintainability**: Choose solutions that are easy to update\n"
            "- **Cost**: Balance features with resource requirements\n\n"
            "## Summary\n"
            "The best approach depends on your specific context and goals. "
            "I recommend starting with a clear definition of success criteria."
        ),
    ]
    return random.choice(responses)


_HANDLERS: List[Callable] = [
    _respond_greeting,
    _respond_how_are_you,
    _respond_crewai,
    _respond_code,
    _respond_analysis,
]


def get_mock_response(query: str) -> str:
    for handler in _HANDLERS:
        result = handler(query)
        if result is not None:
            return result
    return _respond_default(query)
