import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from langgraph.prebuilt import create_react_agent

# ==================================================
# LOAD ENV VARIABLES
# ==================================================

load_dotenv()

# ==================================================
# CONNECT TO CEREBRAS (via OpenAI-compatible API)
# ==================================================

llm = ChatOpenAI(
    model="llama3.1-8b",
    base_url="https://api.cerebras.ai/v1",
    api_key=os.environ["CEREBRAS_API_KEY"],
    temperature=0
)

# ==================================================
# CREATE WIKIPEDIA TOOL
# ==================================================

wiki = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper()
)

tools = [wiki]

# ==================================================
# CREATE REACT AGENT (LangGraph — modern approach)
# ==================================================

agent = create_react_agent(
    model=llm,
    tools=tools
)

# ==================================================
# QUESTION
# ==================================================

question = "Who is A.P.J. Abdul Kalam and why is he famous?"
# ==================================================
# RUN AGENT
# ==================================================
print("\n" + "=" * 60)
print("🤖 Running Agent...")
print("=" * 60)
response = agent.invoke({
    "messages": [
        {"role": "user", "content": question}
    ]
})

# ==================================================
# FINAL OUTPUT
# ==================================================

print("\n" + "=" * 60)
print("✅ FINAL ANSWER")
print("=" * 60)

# Get the last message from the agent
final = response["messages"][-1].content
print(final)