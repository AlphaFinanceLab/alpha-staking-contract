from brownie import interface, Contract, accounts
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
from brownie.exceptions import VirtualMachineError
from .utils import *


def main():
    deployer, alice, bob, worker, alpha, proxy_admin, staking_impl, staking = setup()

    ####################################################################################
    print('===============================================')
    print('1. set & accept governor')

    assert staking.governor() == deployer, 'incorrect deployer governor'
    assert staking.pendingGovernor() == '0x0000000000000000000000000000000000000000', 'incorrect pending governor'

    staking.setPendingGovernor(alice, {'from': deployer})

    assert staking.governor() == deployer, 'incorrect deployer governor after set'
    assert staking.pendingGovernor() == alice, 'incorrect pending governor after set'

    staking.acceptGovernor({'from': alice})

    assert staking.governor() == alice, 'incorrect deployer governor after accept'
    assert staking.pendingGovernor(
    ) == '0x0000000000000000000000000000000000000000', 'incorrect pending governor after accept'

    ####################################################################################
    print('===============================================')
    print('2. unauth set governor (revert expected)')

    try:
        staking.setPendingGovernor(alice, {'from': bob})
        assert False
    except VirtualMachineError:
        pass

    ####################################################################################
    print('===============================================')
    print('3. unauth accept governor (revert expected) ')

    staking.setPendingGovernor(deployer, {'from': alice})

    try:
        staking.acceptGovernor({'from': bob})
        assert False
    except VirtualMachineError:
        pass
