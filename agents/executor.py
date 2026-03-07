from agents.crm_builder import CRMBuilderAgent
from agents.metrics import MetricsAgent
from agents.scheduler_agent import SchedulerAgent
from tools.approval import require_approval


class ExecutorAgent:
    def __init__(self):
        self.crm = CRMBuilderAgent()
        self.metrics = MetricsAgent()
        self.scheduler = SchedulerAgent()

    def execute(self, plan: list[str]) -> dict:
        outputs = []

        for step in (plan or []):
            print(" ", step)
            s = (step or "").lower()

            # --- ADMIN approval ---
            if any(k in s for k in ["draft", "create", "schedule", "run", "metrics", "test"]):
                if not require_approval(f"Step: {step}"):
                    outputs.append({"step": step, "agent": "approval", "out": {"status": "skipped"}})
                    continue

            # --- ROUTING ---
            if "run due" in s:
                out = self.scheduler.run_due()
                agent_name = "SchedulerAgent"

            elif "schedule automation" in s:
                out = self.scheduler.enqueue()
                agent_name = "SchedulerAgent"

            elif ("metrics" in s) or ("test" in s):
                out = self.metrics.run(step)
                agent_name = "MetricsAgent"

            else:
                # ✅ CRMBuilderAgent дээр handle() байгаа
                out = self.crm.handle(step)
                agent_name = "CRMBuilderAgent"

            outputs.append({
                "step": step,
                "agent": agent_name,
                "out": out
            })

        return {"status": "ok", "outputs": outputs}