from brownie import interface, Contract, accounts
import brownie


def test_skim(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    # setup stake
    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    ####################################################################################
    print('===============================================')
    print('1. skim excess alpha')

    alpha.transfer(staking, 1000, {'from': alice})

    prevDeployerBal = alpha.balanceOf(deployer)

    staking.skim(1000, {'from': deployer})

    curDeployerBal = alpha.balanceOf(deployer)

    assert curDeployerBal - prevDeployerBal == 1000, 'incorrect skim amount'

    ####################################################################################
    print('===============================================')
    print('2. bad skim (revert expected)')

    with brownie.reverts('skim/not-enough-balance'):
        staking.skim(1, {'from': deployer})

    ####################################################################################
    print('===============================================')
    print('3. unauth skim (revert expected)')

    with brownie.reverts('onlyGov/not-governor'):
        staking.skim(0, {'from': bob})
