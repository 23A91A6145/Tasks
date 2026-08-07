from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

# Import agents
from agents.classifier import IntentClassifierAgent
from agents.loan_agent import LoanAgent
from agents.support_agent import SupportAgent

# 1. State Definition
class AgentState(TypedDict):
    session_id: str
    user_id: int
    user_role: str
    query: str
    classified_intent: Optional[str]
    target_agent: Optional[str]
    response_content: Optional[str]
    shared_context: Dict[str, Any]

# 2. Node Implementations
def classify_intent_node(state: AgentState) -> Dict[str, Any]:
    classifier = IntentClassifierAgent()
    result = classifier.process(state["query"])
    return {
        "classified_intent": result["classified_intent"],
        "target_agent": result["target_agent"]
    }

def loan_agent_node(state: AgentState, config: Any) -> Dict[str, Any]:
    agent = LoanAgent()
    db_session = config["configurable"]["db_session"]
    result = agent.process(state["query"], state["user_id"], db_session)
    context = state.get("shared_context", {})
    if "shared_context" in result:
        context.update(result["shared_context"])
    return {
        "response_content": result["response_content"],
        "shared_context": context
    }

def support_agent_node(state: AgentState, config: Any) -> Dict[str, Any]:
    agent = SupportAgent()
    db_session = config["configurable"]["db_session"]
    result = agent.process(state["query"], state["user_id"], db_session)
    context = state.get("shared_context", {})
    if "shared_context" in result:
        context.update(result["shared_context"])
    return {
        "response_content": result["response_content"],
        "shared_context": context
    }

# 3. Routing Edge Logic
def route_to_agent(state: AgentState) -> str:
    target = state.get("target_agent")
    if target == "loan_agent":
        return "loan_agent_node"
    elif target == "support_agent":
        return "support_agent_node"
    return "support_agent_node"

# 4. Graph Construction
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("loan_agent_node", loan_agent_node)
workflow.add_node("support_agent_node", support_agent_node)

# Add Edges
workflow.add_edge(START, "classify_intent")

# Add Conditional Edges
workflow.add_conditional_edges(
    "classify_intent",
    route_to_agent,
    {
        "loan_agent_node": "loan_agent_node",
        "support_agent_node": "support_agent_node"
    }
)

workflow.add_edge("loan_agent_node", END)
workflow.add_edge("support_agent_node", END)

# Compile Graph
compiled_graph = workflow.compile()


# 5. Execution Wrapper Helper
def run_agent_workflow(session_id: str, user_id: int, user_role: str, query: str, db_session: Any, existing_context: Optional[dict] = None) -> dict:
    initial_state = {
        "session_id": session_id,
        "user_id": user_id,
        "user_role": user_role,
        "query": query,
        "classified_intent": None,
        "target_agent": None,
        "response_content": None,
        "shared_context": existing_context or {}
    }
    
    config = {"configurable": {"db_session": db_session}}
    final_state = compiled_graph.invoke(initial_state, config=config)
    
    return {
        "classified_intent": final_state.get("classified_intent"),
        "target_agent": final_state.get("target_agent"),
        "response_content": final_state.get("response_content"),
        "shared_context": final_state.get("shared_context", {})
    }
