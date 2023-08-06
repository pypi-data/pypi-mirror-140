"""
Runs happy bank core app.

Represents REST Api layer.
"""
import logging
from flask import Flask

from happy_bank_core.logic import account, transaction
from happy_bank_core.config.log import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

api = Flask(__name__)


@api.errorhandler(404)
def page_not_found(e):
    return "Sorry, we can’t find that page", 404


@api.errorhandler(transaction.TransactionException)
def handle_exception(e):
    return f"Message: {e}", 400


@api.route("/")
def welcome_page():
    """Returns welcome message"""
    return "Welcome to Happy Bank", 200


@api.route("/health")
def health():
    """Returns health status"""
    return "Happy Bank Core app is up and running.", 200


@api.route("/transfer/<sender>/<receiver>/<amount>")
def transfer(sender, receiver, amount: float):
    """Ensures transfer between 2 accounts of given money"""
    customer_john = account.Account(sender, "John Doe", 1000)
    customer_johanna = account.Account(receiver, "Johanna Doe", 2000)
    return (
        f"{list(transaction.Transaction.transfer(customer_john, customer_johanna, float(amount)))}",
        200,
    )


def main():
    """Main method to run code as a module"""
    api.run(debug=True, host="0.0.0.0")


if __name__ == "__main__":
    main()
