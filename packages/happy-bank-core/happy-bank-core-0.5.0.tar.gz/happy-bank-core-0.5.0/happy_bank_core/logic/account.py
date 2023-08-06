import json


class Account:
    def __init__(self, customer_id: str, full_name: str, balance: float):
        """Gets customer's data"""
        self.id = customer_id
        self.name = full_name
        self.deposit = balance

    def __repr__(self):
        return json.dumps({"id": self.id, "name": self.name, "deposit": self.deposit})
