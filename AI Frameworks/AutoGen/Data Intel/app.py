from autogen import (
    UserProxyAgent,
    GroupChat,
    GroupChatManager,
)

from agents.analyst import create_analyst
from agents.statistician import create_statistician
from agents.visualizer import create_visualizer
from agents.reporter import create_reporter

from utils.data_loader import load_sales_data


# ==========================================
# LOAD REAL DATA
# ==========================================

df, summary = load_sales_data()


# ==========================================
# OLLAMA CONFIG
# ==========================================

llm_config = {
    "config_list": [
        {
            "model": "llama3.2:3b",

            "base_url":
                "http://localhost:11434/v1",

            "api_key": "ollama",

            "price": [0, 0]
        }
    ],

    "temperature": 0,
}


# ==========================================
# CREATE AGENTS
# ==========================================

analyst = create_analyst(llm_config)

statistician = create_statistician(llm_config)

visualizer = create_visualizer(llm_config)

reporter = create_reporter(llm_config)


# ==========================================
# USER
# ==========================================

user_proxy = UserProxyAgent(

    name="User",

    human_input_mode="NEVER",

    max_consecutive_auto_reply=8,

    code_execution_config=False,

    is_termination_msg=lambda x:
        "TERMINATE" in x.get("content", "")
)


# ==========================================
# GROUP CHAT
# ==========================================

groupchat = GroupChat(

    agents=[
        user_proxy,
        analyst,
        statistician,
        visualizer,
        reporter,
    ],

    messages=[],

    max_round=8
)


manager = GroupChatManager(

    groupchat=groupchat,

    llm_config=llm_config
)


# ==========================================
# TASK
# ==========================================

TASK = f"""
REAL DATA SUMMARY

Rows:
{summary['rows']}

Columns:
{summary['columns']}

Missing Values:
{summary['missing_values']}

Duplicates:
{summary['duplicates']}

Revenue Growth:
{summary['revenue_growth_percent']}%

Customer Growth:
{summary['customer_growth_percent']}%

TEAM WORKFLOW

Analyst:
Explain data quality.

Statistician:
Explain business trends.

Visualizer:
Suggest charts.

Reporter:
Write executive summary.

End with:

TERMINATE
"""


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    user_proxy.initiate_chat(
        manager,
        message=TASK
    )