from langchain_core.prompts import ChatPromptTemplate

email_prompt = ChatPromptTemplate.from_template(
    """
You are an expert email writer.

Generate 3 versions of the same email.

Purpose:
{purpose}

Recipient:
{recipient}

Details:
{details}

Tone:
{tone}

Requirements:

Version A:
Professional and detailed.

Version B:
Friendly and conversational.

Version C:
Short and concise.

Return structured output only.
"""
)