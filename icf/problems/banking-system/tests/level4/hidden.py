"""Level 4 — merging accounts (hidden cases)."""
from icf_testkit import case, expect

DAY = 86_400_000


@case("an id re-created after a merge is a brand new, empty account")
def recreated_id_is_new(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "bob", 900)
    bank.merge_accounts(4, "alice", "bob")
    expect(bank.create_account(5, "bob"), True, "the id is free again")
    expect(bank.get_balance(6, "bob", 6), 0, "it starts empty")
    expect(bank.get_balance(7, "bob", 3), None,
           "the balances of the old bob are not this account's history")
    expect(bank.top_spenders(8, 3), ["alice(0)", "bob(0)"])


@case("a re-created account's own history starts at its creation")
def recreated_history_is_its_own(Bank):
    bank = Bank()
    bank.create_account(1, "a")
    bank.create_account(2, "b")
    bank.deposit(3, "b", 500)
    bank.merge_accounts(4, "a", "b")
    bank.create_account(5, "b")
    bank.deposit(6, "b", 7)
    expect(bank.get_balance(7, "b", 4), None)
    expect(bank.get_balance(7, "b", 5), 0)
    expect(bank.get_balance(7, "b", 6), 7)
    expect(bank.get_balance(7, "a", 6), 500, "the merged money stayed with a")


@case("a pending cashback follows the money into the absorbing account")
def pending_cashback_follows_the_merge(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.create_account(2, "bob")
    bank.deposit(3, "bob", 1000)
    bank.pay(4, "bob", 1000)                 # 20 back at 4 + DAY
    bank.merge_accounts(5, "alice", "bob")
    expect(bank.get_balance(6, "alice", 6), 0)
    expect(bank.get_balance(4 + DAY, "alice", 4 + DAY), 20,
           "the cashback landed on alice")


@case("a cashback shows in the history at the moment it landed")
def cashback_is_dated_when_it_lands(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 1000)
    bank.pay(3, "alice", 500)                # 10 back at 3 + DAY
    later = 3 + DAY + 1000
    expect(bank.get_balance(later, "alice", 3 + DAY - 1), 500, "before it landed")
    expect(bank.get_balance(later, "alice", 3 + DAY), 510, "the moment it landed")


@case("merges chain: money moved twice still ends in the right place")
def chained_merges(Bank):
    bank = Bank()
    for index, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(index, name)
    bank.deposit(4, "b", 40)
    bank.deposit(5, "c", 300)
    bank.merge_accounts(6, "b", "c")
    bank.merge_accounts(7, "a", "b")
    expect(bank.get_balance(8, "a", 8), 340)
    expect(bank.get_balance(9, "b", 6), None)
    expect(bank.get_balance(10, "c", 5), None)


@case("a payment made before a chain of merges is still found at the end")
def payment_status_through_chained_merges(Bank):
    bank = Bank()
    for index, name in enumerate(("a", "b", "c"), start=1):
        bank.create_account(index, name)
    bank.deposit(4, "c", 500)
    payment = bank.pay(5, "c", 100)
    bank.merge_accounts(6, "b", "c")
    bank.merge_accounts(7, "a", "b")
    expect(bank.get_payment_status(8, "a", payment), "IN_PROGRESS")
    expect(bank.get_payment_status(5 + DAY, "a", payment), "CASHBACK_RECEIVED")
    expect(bank.get_payment_status(5 + DAY, "b", payment), None, "b is gone")


@case("the balance of an account queried at the present moment is its balance")
def balance_now(Bank):
    bank = Bank()
    bank.create_account(1, "alice")
    bank.deposit(2, "alice", 100)
    bank.create_account(3, "bob")
    bank.deposit(4, "bob", 10)
    bank.transfer(5, "alice", "bob", 60)
    expect(bank.get_balance(6, "alice", 6), 40)
    expect(bank.get_balance(6, "bob", 6), 70)
    expect(bank.get_balance(6, "bob", 4), 10, "before the transfer")


@case("a long mixed sequence keeps balances, spending and history consistent")
def long_mixed_scenario(Bank):
    bank = Bank()
    for index, name in enumerate(("ann", "bo", "cy"), start=1):
        bank.create_account(index, name)
    bank.deposit(4, "ann", 5_000)
    bank.deposit(5, "bo", 3_000)
    bank.deposit(6, "cy", 1_000)

    bank.transfer(7, "ann", "bo", 1_000)          # ann out 1000
    payment = bank.pay(8, "bo", 2_000)            # bo out 2000, 40 back at 8+DAY
    bank.transfer(9, "cy", "ann", 500)            # cy out 500

    expect(bank.top_spenders(10, 3), ["bo(2000)", "ann(1000)", "cy(500)"])
    expect(bank.get_balance(11, "bo", 11), 2_000)

    bank.merge_accounts(12, "ann", "cy")
    expect(bank.top_spenders(13, 3), ["bo(2000)", "ann(1500)"],
           "ann absorbed cy's 500 of outgoing")
    expect(bank.get_balance(14, "ann", 14), 5_000,
           "4500 of her own plus cy's remaining 500")

    settled = 8 + DAY
    expect(bank.get_payment_status(settled, "bo", payment), "CASHBACK_RECEIVED")
    expect(bank.get_balance(settled, "bo", settled), 2_040)
    expect(bank.create_account(settled + 1, "cy"), True)
    expect(bank.get_balance(settled + 2, "cy", 6), None)
