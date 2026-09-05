from backend.app.research.planner import ResearchPlanner
from backend.app.models.schemas import ResearchPlan
from backend.app.core.constants import ResearchMode

class PlannerAgent:
    @staticmethod
    def plan(topic: str, mode: ResearchMode) -> ResearchPlan:
        return ResearchPlanner.generate_plan(topic, mode)
