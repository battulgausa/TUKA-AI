def require_approval(summary: str) -> bool:
    print("\n[ADMIN APPROVAL REQUIRED]")
    print(summary)
    ans = input("Approve? (y/n): ").strip().lower()
    return ans == "y"
