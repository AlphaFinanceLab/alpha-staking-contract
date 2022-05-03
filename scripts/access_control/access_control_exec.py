import time

from brownie import interface, accounts, ZERO_ADDRESS, rpc
from brownie.exceptions import VirtualMachineError

from scripts.utils import *


def main():
    assert rpc.is_active(), "only fork rpc"

    alpha_contracts = get_alpha_contracts()

    exec_safe = alpha_contracts.exec_safe
    exec_account = exec_safe.account
    eoa_account = accounts.at("0xB593d82d53e2c187dc49673709a6E9f806cdC835", force=True)

    final_receipts = []
    alpha_staking = interface.IAny("0x2aa297c3208bd98a9a477514d3c80ace570a6dee")

    receipt = alpha_staking.acceptGovernor({"from": exec_account})
    final_receipts.append(receipt)

    # if submit safe transaction, skip running tests
    is_submit = yes_no_question("do we submit tx to safe wallet?", default=False)
    if is_submit:
        for i in range(0, len(final_receipts), 10):
            safe_tx = exec_safe.multisend_from_receipts(
                receipts=final_receipts[i : i + 10]
            )
            exec_safe.post_transaction(safe_tx)

        time.sleep(1)
        exit()

    # testing
    alpha_staking.setWorker(ZERO_ADDRESS, {"from": exec_account})
    try:
        alpha_staking.setWorker(ZERO_ADDRESS, {"from": eoa_account})
        assert False, "should revert"
    except VirtualMachineError as e:
        assert e.revert_msg == "onlyGov/not-governor"
        print("expect revert")

    alpha_staking.setPendingGovernor(eoa_account, {"from": exec_account})
    try:
        alpha_staking.setPendingGovernor(eoa_account, {"from": eoa_account})
        assert False, "should revert"
    except VirtualMachineError as e:
        assert e.revert_msg == "onlyGov/not-governor"
        print("expect revert")

    alpha_staking.setMerkle(ZERO_ADDRESS, {"from": exec_account})
    try:
        alpha_staking.setMerkle(ZERO_ADDRESS, {"from": eoa_account})
        assert False, "should revert"
    except VirtualMachineError as e:
        assert e.revert_msg == "onlyGov/not-governor"
        print("expect revert")

    print("Done!")
