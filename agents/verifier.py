import re

class VerifierAgent:
    def verify_text(self, text: str) -> dict:
        t = (text or "").lower()

        # High-risk intents (keep small and precise)
        if re.search(r"(^|\s)(hack|phishing|malware|weapon)\b", t):
            return {"ok": False, "reason": "Blocked: high-risk intent keyword"}

        # Command-like destructive patterns (precise)
        destructive_patterns = [
            r"(^|\s)del\s+[^ \n]+",          # del file
            r"(^|\s)rm\s+(-rf\s+)?[^ \n]+",  # rm / rm -rf
            r"(^|\s)format(\s|$)",           # format
            r"(^|\s)shutdown(\s|$)",         # shutdown
            r"(^|\s)diskpart(\s|$)",         # diskpart
            r"(^|\s)regedit(\s|$)",          # regedit
        ]
        for p in destructive_patterns:
            if re.search(p, t):
                return {"ok": False, "reason": f"Blocked destructive command pattern: {p}"}

        # Tooling words alone should NOT block (e.g., "framework", "crm", etc.)
        return {"ok": True, "reason": "Passed security policy"}

    def verify_goal(self, goal: str) -> dict:
        return self.verify_text(goal)

    def verify_plan(self, goal: str, plan: list[str]) -> dict:
        combined = (goal or "") + " " + " ".join(plan or [])
        return self.verify_text(combined)
