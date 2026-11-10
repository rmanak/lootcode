class Bank:
    """An in-memory ledger with scheduled payments.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: accounts and transfers ----------------------------------

    def create_account(self, timestamp: int, account_id: str) -> bool:
        pass

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        pass

    def transfer(self, timestamp: int, source_id: str, target_id: str,
                 amount: int) -> int | None:
        pass

    # --- Level 2: who spends the most -------------------------------------

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        pass

    # --- Level 3: scheduled payments --------------------------------------

    def schedule_payment(self, timestamp: int, account_id: str, amount: int,
                         delay: int) -> str | None:
        pass

    def cancel_payment(self, timestamp: int, account_id: str,
                       payment_id: str) -> bool:
        pass

    def get_payment_status(self, timestamp: int, account_id: str,
                           payment_id: str) -> str | None:
        pass

    # --- Level 4: merging accounts and past balances ----------------------

    def merge_accounts(self, timestamp: int, account_id_1: str,
                       account_id_2: str) -> bool:
        pass

    def get_balance(self, timestamp: int, account_id: str,
                    time_at: int) -> int | None:
        pass
