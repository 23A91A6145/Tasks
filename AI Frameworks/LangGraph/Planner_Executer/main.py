from planner.planner import create_plan
from planner.parser import parse_plan
from executor.runner import run_plan

task = input("Enter Task: ")

plan_text = create_plan(task)

plan = parse_plan(plan_text)

results = run_plan(plan)

print("\nExecution Summary\n")

for item in results:

    print("-" * 50)
    print(item["step"])
    print(item["result"])