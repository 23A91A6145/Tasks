import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
from agents.manager import SkillManager
from agents.assistant import AssistantAgent

# Set up logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def run_demo():
    print("=" * 80)
    print("      MULTI-SOURCE SKILLS PROVIDER & AGENT ORCHESTRATION PIPELINE DEMO      ")
    print("=" * 80)
    
    # Initialize Manager
    manager = SkillManager()
    registry = manager.get_registry()
    
    # Display Active Skills
    print("\n--- ACTIVE SKILLS IN UNIFIED REGISTRY ---")
    active_skills = registry.list_skills()
    print(f"Total Active Skills: {len(active_skills)}")
    for idx, skill in enumerate(active_skills, 1):
        print(f" {idx}. [{skill.name.upper()}] (v{skill.version})")
        print(f"    Source:   {skill.source_type} -> {skill.source_path}")
        print(f"    Priority: {skill.priority}")
        print(f"    Desc:     {skill.description}")
        print(f"    Params:   {list(skill.parameters.get('properties', {}).keys())}")
        print("-" * 50)
        
    # Display Conflict Resolution Report
    print("\n--- CONFLICT DETECTION & RESOLUTION REPORT ---")
    summary = registry.summary
    print(f"Total Source Skills Loaded: {summary.total_loaded_skills}")
    print(f"Conflicts Detected:         {summary.conflicts_detected}")
    
    for conflict in summary.conflicts:
        print(f"\nConflict on skill: '{conflict.skill_name}'")
        print("  Found in sources:")
        for src in conflict.sources:
            print(f"    - Type: {src['source_type']:8} | Priority: {src['priority']:3} | Path: {src['source_path']}")
        print(f"  Winner:  [{conflict.winning_source_type.upper()}] -> {conflict.winning_source_path}")
        print(f"  Reason:  {conflict.resolution_reason}")
    print("-" * 50)

    # Initialize Assistant Agent
    agent = AssistantAgent(manager)
    
    # Test cases representing different skill sources and logic
    test_prompts = [
        "Can you add 12.5 and 37.5?",
        "Please subtract 15 from 100",
        "Search for the best machine learning frameworks",
        "Explain host system details (uname / os info)",
        "Translate the phrase Hello and Welcome to Spanish",
        "Send email to manager@office.com about Task Status saying all features are fully implemented",
        "Calculate the factorial of 6",
        "Please greet Doctor Bruce Banner"
    ]
    
    print("\n--- RUNNING AGENT NATURAL LANGUAGE INTERFACES ---")
    for idx, prompt in enumerate(test_prompts, 1):
        print(f"\n[Prompt {idx}]: \"{prompt}\"")
        result = agent.execute_query(prompt)
        print(f"Thought:     {result['thought']}")
        print(f"Action:      {result['action']}({result['arguments']})")
        print(f"Observation: {result['observation']}")
        print(f"Response:    {result['answer']}")
        print("-" * 80)

if __name__ == "__main__":
    run_demo()
