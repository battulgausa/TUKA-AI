
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.eval_agent import EvalAgent
from agents.verifier import VerifierAgent
from memory.logger import log_run
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

class TukaCore:
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.verifier = VerifierAgent()
        self.evaluator = EvalAgent()

    def run(self, goal: str):
        print("\n[TUKA] Goal:", goal)

        # Verify GOAL first (before planning)
        v_goal = self.verifier.verify_goal(goal)
        print("[VERIFY-GOAL]", v_goal)
        if not v_goal["ok"]:
            print("[TUKA] Blocked before planning:", v_goal["reason"])
            log_run(goal, [], {"status": "blocked"}, {"score": 0.0, "notes": v_goal["reason"]})
            return

        plan = self.planner.plan(goal)
        print("[TUKA] Plan ready.")

        # Verify PLAN
        v_plan = self.verifier.verify_plan(goal, plan)
        print("[VERIFY-PLAN]", v_plan)
        if not v_plan["ok"]:
            print("[TUKA] Blocked after planning:", v_plan["reason"])
            log_run(goal, plan, {"status": "blocked"}, {"score": 0.0, "notes": v_plan["reason"]})
            return

        result = self.executor.execute(plan)
        print("[TUKA] Execution finished.")

        evaluation = self.evaluator.evaluate(result)
        print("[TUKA] Evaluation:", evaluation)

        log_run(goal, plan, result, evaluation)
        print("[TUKA] Logged to runs\\runs.jsonl")

if __name__ == "__main__":
    goal = input("Enter goal: ")
    tuka = TukaCore()
    tuka.run(goal)