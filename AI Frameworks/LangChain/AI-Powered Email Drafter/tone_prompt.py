from langchain_core.prompts import ChatPromptTemplate


tone_prompt = ChatPromptTemplate.from_template("""
You are an email tone classifier.

Analyze the request.

Choose ONLY one tone:

Professional
Formal
Friendly
Persuasive
Supportive
Apologetic
Urgent
Sales

Request:
{details}

Return only the tone name.
""")