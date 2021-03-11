from brownie import interface, Contract, accounts
import brownie

def test_not_gov_extract(a, alice, staking):
    with brownie.reverts('onlyGov/not-governor'):
        staking.extract(1000, {'from': alice})

def test_worker_extract(a, alice, worker, staking):
    assert staking.worker() == worker
    with brownie.reverts('onlyGov/not-governor'):
        staking.extract(1000, {'from': worker})

def test_not_enough_alpha(a, alice, bob, deployer, staking):
    alice_stake_amt = 10**18
    staking.stake(alice_stake_amt, {'from': alice})
    with brownie.reverts('extract/too-low-total-alpha'):
        staking.extract(10**18, {'from': deployer})

def test_extract(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    prevDeployerBal = alpha.balanceOf(deployer)

    staking.extract(1000, {'from': deployer})

    curDeployerBal = alpha.balanceOf(deployer)
    assert curDeployerBal - prevDeployerBal == 1000, 'incorrect extract amount'
