import pytest
from brownie import interface
import brownie

def test_initial_governor(staking, deployer):
    assert staking.governor() == deployer, 'incorrect deployer governor'

def test_pending_governor(staking):
    assert staking.pendingGovernor() == '0x0000000000000000000000000000000000000000', 'incorrect pending governor'

def test_set_governor(staking, deployer, alice):
    staking.setPendingGovernor(alice, {'from': deployer})
    assert staking.governor() == deployer, 'incorrect deployer governor after set'
    assert staking.pendingGovernor() == alice, 'incorrect pending governor after set'

def test_not_gov_set_pending_governor(deployer, staking, alice, bob):
    with brownie.reverts('onlyGov/not-governor'):
        staking.setPendingGovernor(alice, {'from': bob})

def test_accept_governor(staking, alice, deployer):
    staking.setPendingGovernor(alice, {'from': deployer})
    staking.acceptGovernor({'from': alice})
    assert staking.governor() == alice, 'incorrect deployer governor after accept'
    assert staking.pendingGovernor(
    ) == '0x0000000000000000000000000000000000000000', 'incorrect pending governor after accept'

def test_not_pending_accept_governor(staking, deployer, alice, bob):
    staking.setPendingGovernor(alice, {'from': deployer})
    with brownie.reverts('acceptGovernor/not-pending'):
        staking.acceptGovernor({'from': bob})
    assert staking.pendingGovernor() == alice, 'incorrect pending governor after revert'
    
def test_set_governor_twice(staking, deployer, alice, bob):
    staking.setPendingGovernor(alice, {'from': deployer})
    assert staking.pendingGovernor() == alice, 'incorrect pending governor after set'

    staking.setPendingGovernor(bob, {'from': deployer})
    assert staking.pendingGovernor() == bob, 'incorrect pending governor after set'

    with brownie.reverts('acceptGovernor/not-pending'):
        staking.acceptGovernor({'from': alice})

    staking.acceptGovernor({'from': bob})    
    assert staking.governor() == bob, 'incorrect governor after accept'
    assert staking.pendingGovernor(
    ) == '0x0000000000000000000000000000000000000000', 'incorrect pending governor after accept'

