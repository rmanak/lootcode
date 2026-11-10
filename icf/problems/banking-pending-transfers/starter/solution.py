class Bank:
    """An in-memory ledger with transfers that wait to be accepted.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: accounts ------------------------------------------------

    def create_account(self, timestamp: int, account_id: str) -> bool:
        pass

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        pass

    def withdraw(self, timestamp: int, account_id: str, amount: int) -> int | None:
        pass

    def get_balance(self, timestamp: int, account_id: str) -> int | None:
        pass

    # --- Level 2: transfers and activity ----------------------------------

    def transfer(self, timestamp: int, source_id: str, target_id: str,
                 amount: int) -> int | None:
        pass

    def top_activity(self, timestamp: int, n: int) -> list[str]:
        pass

    # --- Level 3: pending transfers ---------------------------------------

    def initiate_transfer(self, timestamp: int, source_id: str, target_id: str,
                          amount: int) -> str | None:
        pass

    def accept_transfer(self, timestamp: int, account_id: str,
                        transfer_id: str) -> bool:
        pass

    # --- Level 4: merging accounts and history ----------------------------

    def merge_accounts(self, timestamp: int, account_id_1: str,
                       account_id_2: str) -> bool:
        pass

    def get_history(self, timestamp: int, account_id: str) -> list[str] | None:
        pass
