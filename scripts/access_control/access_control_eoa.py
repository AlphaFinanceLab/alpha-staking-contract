from brownie import interface, accounts, rpc, network

from scripts.utils import *

if not rpc.is_active():
    network.priority_fee("1 gwei")
    network.max_fee("100 gwei")


def main():
    alpha_contracts = get_alpha_contracts()

    exec_safe = alpha_contracts.exec_safe
    exec_account = exec_safe.account
    # FIXME: fix eoa account
    eoa_account = accounts.at("0xB593d82d53e2c187dc49673709a6E9f806cdC835", force=True)

    alpha_staking = interface.IAny("0x2aa297c3208bd98a9a477514d3c80ace570a6dee")
    alpha_staking.setPendingGovernor(exec_account, {"from": eoa_account})

    print("Done!")
