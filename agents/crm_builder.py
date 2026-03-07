from tools.crm_store import create_workflow, add_template, read_db

class CRMBuilderAgent:
    def handle(self, step: str) -> dict:
        created = {"workflow": None, "templates": []}

        s = step.lower()

        if "define follow-up stages" in s:
            stages = ["Day 0", "Day 2", "Day 7"]
            created["workflow"] = create_workflow("CRM Follow-up", stages)

        if "draft message templates" in s:
            created["templates"].append(
                add_template("sms", "Hi {name}, just checking in—do you have 5 minutes to chat about your project?")
            )
            created["templates"].append(
                add_template(
                    "email",
                    "Subject: Quick follow-up\n\nHi {name},\nJust following up on our last message. What’s a good time to connect?\n\nThanks,\n{sender}"
                )
            )

        if "create crm fields" in s:
            # дараагийн алхамд fields хэсгийг DB-д нэмнэ (одоохондоо mock)
            pass

        return {"status": "ok", "created": created, "db_snapshot": read_db()}
def run(self, step: str):
    return self.execute(step)  