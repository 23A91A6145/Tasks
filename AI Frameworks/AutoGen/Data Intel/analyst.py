from autogen import AssistantAgent


def create_analyst(llm_config):

    return AssistantAgent(
        name="Analyst",

        system_message="""
You are a Senior Data Analyst.

Responsibilities:

- Inspect datasets
- Detect missing values
- Detect duplicates
- Identify outliers
- Produce business insights

Keep responses concise.
Finish your work clearly.
""",

        llm_config=llm_config,
    )