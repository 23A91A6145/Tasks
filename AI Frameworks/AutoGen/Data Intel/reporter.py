from autogen import AssistantAgent


def create_reporter(llm_config):

    return AssistantAgent(
        name="Reporter",

        system_message="""
You are an Executive Business Consultant.

Write:

- Executive summaries
- Risks
- Opportunities
- Recommendations
- Future actions

Always end your final response with:

TERMINATE
""",

        llm_config=llm_config,
    )