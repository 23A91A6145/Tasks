from langchain_core.prompts import ChatPromptTemplate


reply_prompt = ChatPromptTemplate.from_template(
    """
You are an expert business communication assistant.

Analyze the received email.

Generate:

1. Suitable subject
2. Appropriate tone
3. Professional reply

Received Email:

{received_email}

Return structured output.
"""
)