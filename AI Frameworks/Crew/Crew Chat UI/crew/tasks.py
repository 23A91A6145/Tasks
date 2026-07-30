from crewai import Task
from crew.agents import create_researcher, create_analyst, create_writer


_researcher = create_researcher()
_analyst = create_analyst()
_writer = create_writer()


def create_research_task(query: str) -> Task:
    return Task(
        description=(
            f"Research the following query thoroughly:\n\n"
            f"---\n{query}\n---\n\n"
            "Gather relevant information, key facts, context, and any data "
            "needed to answer this question comprehensively. "
            "Organize your findings clearly for the next agent."
        ),
        expected_output=(
            "A structured summary of findings with key points, relevant data, "
            "and organized information ready for analysis."
        ),
        agent=_researcher,
    )


def create_analysis_task(query: str) -> Task:
    return Task(
        description=(
            f"Based on the research provided, analyze the information "
            f"to answer this question:\n\n---\n{query}\n---\n\n"
            "Identify key insights, connections, and implications. "
            "Evaluate the quality and relevance of the information. "
            "Prepare a clear analytical summary for the response writer."
        ),
        expected_output=(
            "A concise analysis with key insights, logical connections, "
            "and a recommended structure for the final response."
        ),
        agent=_analyst,
    )


def create_writing_task(query: str) -> Task:
    return Task(
        description=(
            f"Using the research and analysis provided, write a comprehensive, "
            f"clear, and helpful response to this question:\n\n---\n{query}\n---\n\n"
            "The response should be well-structured, accurate, and directly "
            "address the user's needs. Use markdown formatting where appropriate "
            "(headings, lists, code blocks). Be conversational but professional."
        ),
        expected_output=(
            "A polished, complete response in markdown format that directly "
            "answers the user's question with clarity and depth."
        ),
        agent=_writer,
    )


def get_all_tasks(query: str) -> list[Task]:
    return [
        create_research_task(query),
        create_analysis_task(query),
        create_writing_task(query),
    ]
