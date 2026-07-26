from executor.executor import execute_step

def run_plan(plan):

    results = []

    for index, step in enumerate(plan, start=1):

        print(f"\nExecuting Step {index}: {step}")

        output = execute_step(step)

        results.append({
            "step": step,
            "result": output
        })

    return results