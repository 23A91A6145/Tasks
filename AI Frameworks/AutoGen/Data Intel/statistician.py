from autogen import AssistantAgent


def create_statistician(llm_config):

    return AssistantAgent(
        name="Statistician",

        system_message="""
You are a Statistician.

Tasks:

- Growth analysis
- Correlations
- Forecasts
- Business metrics

Provide explanations for every finding.
""",

        llm_config=llm_config,
    )