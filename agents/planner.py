class PlannerAgent:
    def plan(self, goal: str) -> list[str]:
        print("[Planner] Creating a plan...")

        g = (goal or "").lower().strip()

        #  Shortcut goals
        if "run due" in g:
            return ["Run due followups"]

        if "schedule automation" in g:
            return ["Schedule automation triggers"]

        # Default CRM workflow plan
        return [
            f"Confirm customer segment & channel for: {goal}",
            "Define follow-up stages (Day 0, Day 2, Day 7)",
            "Draft message templates (SMS/email)",
            "Create CRM fields + statuses",
            "Schedule automation triggers",
            "Add metrics: reply rate, conversion rate",
            "Run a test with 5 sample leads, then evaluate",
        ]
