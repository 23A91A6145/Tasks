import time
from dataclasses import dataclass

from crewai import Crew, Process
from crew.tasks import get_all_tasks
from crew.config import settings
from services.logger import logger
from services.mock_responder import get_mock_response
from services.model_service import ModelService


@dataclass
class CrewMetrics:
    duration: float = 0.0
    tasks_completed: int = 0
    error: str | None = None
    used_fallback: bool = False


class CrewAssistant:
    def __init__(self) -> None:
        self.crew: Crew | None = None
        self.metrics = CrewMetrics()
        self._model_service = ModelService()

    def _build_crew(self, query: str) -> None:
        tasks = get_all_tasks(query)
        agents = list({t.agent for t in tasks})

        self.crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=settings.CREW_VERBOSE,
            max_rpm=settings.CREW_MAX_RPM,
        )

    def _is_llm_available(self) -> bool:
        if settings.provider == "none":
            return False
        if settings.provider == "ollama":
            model = settings.OLLAMA_MODEL_NAME
            return self._model_service.is_model_available(model)
        return True

    def run(self, query: str) -> str:
        if not query or not query.strip():
            self.metrics = CrewMetrics()
            return "Please provide a valid query."

        self.metrics = CrewMetrics()
        start = time.time()

        if not self._is_llm_available():
            logger.warning("LLM not available, using fallback responder")
            self.metrics.used_fallback = True
            self.metrics.duration = time.time() - start
            return get_mock_response(query)

        try:
            self._build_crew(query)
            logger.info(f"Crew built with {len(self.crew.agents)} agents, {len(self.crew.tasks)} tasks")

            result = self.crew.kickoff()

            self.metrics.duration = time.time() - start
            self.metrics.tasks_completed = len(self.crew.tasks)

            logger.info(f"Crew completed in {self.metrics.duration:.2f}s")
            return str(result)

        except Exception as e:
            error_str = str(e)
            logger.warning(f"Crew execution failed ({error_str[:80]}...), using fallback")
            self.metrics.used_fallback = True
            self.metrics.error = error_str
            self.metrics.duration = time.time() - start
            return get_mock_response(query)
