from typing import TypedDict


class WorkflowState(TypedDict):
    topic: str

    draft: str

    review_notes: str

    reviewed: bool

    human_feedback: str

    human_approved: bool

    revision_count: int

    published: bool