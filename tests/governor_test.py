import pytest
from brownie import interface
import brownie

def test_governor(deployer, staking, alice, bob):
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

    with brownie.reverts('onlyGov/not-governor'):
        staking.setPendingGovernor(alice, {'from': bob})

    ####################################################################################
    print('===============================================')
    print('3. unauth accept governor (revert expected) ')

    staking.setPendingGovernor(deployer, {'from': alice})

    with brownie.reverts('acceptGovernor/not-pending'):
        staking.acceptGovernor({'from': bob})
