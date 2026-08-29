import json


class Budget:
    def __init__(self, wallet_file="data/wallet.json"):
        self.wallet_file = wallet_file

    def load(self):
        with open(self.wallet_file, "r") as f:
            return json.load(f)

    def save(self, wallet):
        with open(self.wallet_file, "w") as f:
            json.dump(wallet, f, indent=2)

    def balance(self):
        return self.load()["balance"]

    def spend(self, amount):
        wallet = self.load()

        if amount <= 0:
            return False

        if wallet["balance"] < amount:
            wallet["status"] = "DEAD"
            self.save(wallet)
            return False

        wallet["balance"] -= amount
        wallet["total_spent"] += amount

        if wallet["balance"] <= 0:
            wallet["balance"] = 0
            wallet["status"] = "DEAD"

        self.save(wallet)
        return True

    def earn(self, amount):
        wallet = self.load()

        if amount <= 0:
            return False

        wallet["balance"] += amount
        wallet["total_earned"] += amount
        wallet["status"] = "ALIVE"

        self.save(wallet)
        return True
