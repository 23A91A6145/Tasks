class AgentMemory:

    def __init__(self):

        self.state = {
            "task": "",
            "plan": [],
            "current_step": None,
            "completed_steps": [],
            "failed_steps": [],
            "remaining_steps": [],
            "execution_history": [],
            "intermediate_outputs": {},
            "retry_count": 0,
            "status": "idle"
        }

    def set_task(self, task):
        self.state["task"] = task

    def set_plan(self, plan):
        self.state["plan"] = plan
        self.state["remaining_steps"] = plan.copy()

    def start_step(self, step):
        self.state["current_step"] = step

    def complete_step(self, step, output):

        self.state["completed_steps"].append(step)

        self.state["remaining_steps"].remove(step)

        self.state["intermediate_outputs"][step] = output

        self.state["execution_history"].append(
            {
                "step": step,
                "status": "completed"
            }
        )

    def fail_step(self, step, error):

        self.state["failed_steps"].append(step)

        self.state["execution_history"].append(
            {
                "step": step,
                "status": "failed",
                "error": error
            }
        )

    def summary(self):

        return self.state