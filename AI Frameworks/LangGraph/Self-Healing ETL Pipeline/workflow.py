from datetime import datetime
from typing import Any, TypedDict

from langgraph.graph import StateGraph, END

from agents.extractor import ExtractorAgent
from agents.cleaner import CleanerAgent
from agents.transformer import TransformerAgent
from agents.validator import ValidatorAgent
from agents.loader import LoaderAgent
from agents.recovery import RecoveryAgent
from agents.monitor import MonitorAgent
from agents.reporter import ReporterAgent
from agents.analyst import AnalystAgent
from agents.quality import QualityAgent


extractor = ExtractorAgent()
cleaner = CleanerAgent()
transformer = TransformerAgent()
validator = ValidatorAgent()
loader = LoaderAgent()
recovery = RecoveryAgent()
monitor = MonitorAgent()
reporter = ReporterAgent()
analyst = AnalystAgent()
quality = QualityAgent()


class ETLState(TypedDict):

    data: Any

    validation_report: dict

    status: str

    start_time: Any

    end_time: Any

    metrics: dict

    analysis: str

    quality_score: int


# =====================================================
# NODES
# =====================================================

def extract_node(state):

    result = extractor.extract(
        "data/raw/iris.csv"
    )

    state["data"] = result["data"]

    return state


def clean_node(state):

    state["data"] = cleaner.clean(
        state["data"]
    )

    return state


def transform_node(state):

    state["data"] = transformer.transform(
        state["data"]
    )

    return state


def validate_node(state):

    report = validator.validate(
        state["data"]
    )

    state["validation_report"] = report

    state["status"] = report["status"]

    return state


def recovery_node(state):

    state["data"] = recovery.recover(
        state["data"]
    )

    return state


def load_node(state):

    loader.load(
        state["data"]
    )

    return state


def monitor_node(state):

    state["end_time"] = datetime.now()

    metrics = monitor.build_metrics(
        state["data"],
        state["validation_report"],
        state["start_time"],
        state["end_time"]
    )

    monitor.save_metrics(
        metrics
    )

    state["metrics"] = metrics

    return state


def quality_node(state):

    score = quality.calculate_score(
        state["validation_report"]
    )

    quality.save_history(
        state["metrics"],
        score
    )

    state["quality_score"] = score

    return state


def analyst_node(state):

    analysis = analyst.analyze(
        state["data"]
    )

    state["analysis"] = analysis

    return state


# =====================================================
# ROUTER
# =====================================================

def validation_router(state):

    if state["status"] == "PASS":
        return "load"

    return "recovery"


# =====================================================
# GRAPH
# =====================================================

builder = StateGraph(
    ETLState
)

builder.add_node(
    "extract",
    extract_node
)

builder.add_node(
    "clean",
    clean_node
)

builder.add_node(
    "transform",
    transform_node
)

builder.add_node(
    "validate",
    validate_node
)

builder.add_node(
    "recovery",
    recovery_node
)

builder.add_node(
    "load",
    load_node
)

builder.add_node(
    "monitor",
    monitor_node
)

builder.add_node(
    "quality",
    quality_node
)

builder.add_node(
    "analyst",
    analyst_node
)

builder.set_entry_point(
    "extract"
)

builder.add_edge(
    "extract",
    "clean"
)

builder.add_edge(
    "clean",
    "transform"
)

builder.add_edge(
    "transform",
    "validate"
)

builder.add_conditional_edges(
    "validate",
    validation_router,
    {
        "load": "load",
        "recovery": "recovery"
    }
)

builder.add_edge(
    "recovery",
    "validate"
)

builder.add_edge(
    "load",
    "monitor"
)

builder.add_edge(
    "monitor",
    "quality"
)

builder.add_edge(
    "quality",
    "analyst"
)

builder.add_edge(
    "analyst",
    END
)

workflow = builder.compile()