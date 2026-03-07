import bcrypt

pw = input("Password (visible): ").encode("utf-8")
hashed = bcrypt.hashpw(pw, bcrypt.gensalt(rounds=12)).decode("utf-8")
print("\nHASH:\n", hashed)
