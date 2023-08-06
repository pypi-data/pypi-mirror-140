import logging

from .account import Account

logger = logging.getLogger(__name__)


class TransactionException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Transaction:
    @staticmethod
    def check_balance(customer: Account, amount: float) -> bool:
        """Verifies if customer has enough money to transfer"""
        balance = customer.deposit
        logger.info(f"check_balance function return value: {0 < amount <= balance}")
        return 0 < amount <= balance

    @staticmethod
    def transfer(sender: Account, recipient: Account, amount: float) -> tuple:
        """Ensures transfer between 2 accounts"""
        if sender.id == recipient.id:
            logger.error("Sender and recipient ids should have different values")
            raise TransactionException("Sender and recipient ids should have different values")
        elif not Transaction.check_balance(sender, amount):
            logger.error("Insufficient balance or transfer amount <= 0")
            raise TransactionException("Insufficient balance or transfer amount <= 0")

        sender.deposit = round((sender.deposit - amount), 2)
        recipient.deposit = round((recipient.deposit + amount), 2)
        confirmation_message = (
            f"Following amount {amount} has been transferred "
            f"from account {sender.id} to account {recipient.id}; "
            f"Current {sender.id} balance: {sender.deposit}; "
            f"Current {recipient.id} balance: {recipient.deposit};"
        )
        logger.info(confirmation_message)
        return sender, recipient
