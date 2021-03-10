from brownie import interface, Contract, accounts
import brownie

def test_not_enough_alpha(staking, deployer, alpha):
    assert alpha.balanceOf(staking) == 0, 'invalid initial alpha in staking contract'
    with brownie.reverts('skim/not-enough-balance'):
        staking.skim(1, {'from': deployer})

    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    assert alpha.balanceOf(staking) > 0, 'invalid alpha after stake'

    with brownie.reverts('skim/not-enough-balance'):
        staking.skim(1, {'from': deployer})

def test_not_gov_skim(staking, bob):
    with brownie.reverts('onlyGov/not-governor'):
        staking.skim(0, {'from': bob})

def test_skim(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    alpha.transfer(staking, 1000, {'from': alice})
    prevDeployerBal = alpha.balanceOf(deployer)

    staking.skim(1000, {'from': deployer})
    curDeployerBal = alpha.balanceOf(deployer)

    assert curDeployerBal - prevDeployerBal == 1000, 'incorrect skim amount'

