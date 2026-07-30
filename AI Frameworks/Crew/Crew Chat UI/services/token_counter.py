import re
from typing import Dict, List


class TokenCounter:
    _WORD_PATTERN = re.compile(r"\w+|[^\w\s]")

    @classmethod
    def estimate(cls, text: str) -> int:
        if not text:
            return 0
        words = len(cls._WORD_PATTERN.findall(text))
        return max(1, words)

    @classmethod
    def estimate_messages(cls, messages: List[Dict]) -> Dict:
        total_tokens = 0
        per_role = {"user": 0, "assistant": 0, "system": 0}
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            tokens = cls.estimate(content)
            total_tokens += tokens
            if role in per_role:
                per_role[role] += tokens

        return {
            "total": total_tokens,
            "per_role": per_role,
            "estimated_cost": cls.estimate_cost(total_tokens),
        }

    @classmethod
    def estimate_cost(cls, tokens: int, model: str = "llama3.2") -> str:
        return "free"

    @classmethod
    def format_tokens(cls, tokens: int) -> str:
        if tokens < 1000:
            return f"{tokens} tokens"
        return f"{tokens / 1000:.1f}K tokens"

    @classmethod
    def summarize_token_usage(cls, messages: List[Dict]) -> str:
        stats = cls.estimate_messages(messages)
        total = stats["total"]
        per_role = stats["per_role"]
        parts = [f"**{cls.format_tokens(total)}** total"]
        if per_role["user"]:
            parts.append(f"🧑 {cls.format_tokens(per_role['user'])}")
        if per_role["assistant"]:
            parts.append(f"🤖 {cls.format_tokens(per_role['assistant'])}")
        return " · ".join(parts)
