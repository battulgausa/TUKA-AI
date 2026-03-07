class EvalAgent:
    def evaluate(self, result: dict) -> dict:
        outputs = (result or {}).get("outputs", []) or []

        score = 0.0
        notes = []

        # If admin rejected any step, penalize
        for item in outputs:
            out = (item.get("out") or {})
            if out.get("status") == "rejected":
                score -= 0.2
                notes.append("admin_rejected_step")

        # CRM artifacts
        created_templates = 0
        workflow_created = False

        # Metrics / Simulation
        has_metrics = False
        has_simulation = False

        # Scheduler
        scheduler_seen = False
        scheduler_sent = 0
        scheduler_due = 0
        scheduler_queued = 0

        for item in outputs:
            out = (item.get("out") or {})

            # CRM builder snapshots
            if isinstance(out, dict):
                created = out.get("created") or {}
                if isinstance(created, dict):
                    if created.get("workflow"):
                        workflow_created = True
                    templates = created.get("templates") or []
                    if isinstance(templates, list):
                        created_templates += len(templates)

            # Metrics agent outputs
            if "metrics" in out:
                has_metrics = True
            if "simulation" in out:
                has_simulation = True

            # Scheduler agent outputs
            if "sent" in out or "due" in out or "queued" in out:
                scheduler_seen = True
                scheduler_sent = int(out.get("sent", scheduler_sent) or 0)
                scheduler_due = int(out.get("due", scheduler_due) or 0)
                scheduler_queued = int(out.get("queued", scheduler_queued) or 0)

        # Scoring rules (simple, predictable)
        if workflow_created:
            score += 0.3
            notes.append("workflow_created")

        if created_templates > 0:
            score += 0.2
            notes.append(f"templates_created={created_templates}")

        if has_metrics:
            score += 0.2
            notes.append("metrics_defined")

        if has_simulation:
            score += 0.1
            notes.append("simulation_ran")

        if scheduler_seen:
            score += 0.1
            notes.append(f"scheduler_seen(sent={scheduler_sent},due={scheduler_due},queued={scheduler_queued})")

            # Bonus if something was actually sent
            if scheduler_sent > 0:
                score += 0.2
                notes.append("scheduler_sent_bonus")

        # Clamp
        if score < 0:
            score = 0.0
        if score > 1.0:
            score = 1.0

        return {"score": round(score, 2), "notes": ", ".join(notes) if notes else "basic_eval"}
