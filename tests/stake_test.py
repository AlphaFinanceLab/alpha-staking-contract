from brownie import interface, Contract, accounts
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
from brownie.exceptions import VirtualMachineError


def test_stake(a, deployer, alice, bob, worker, alpha, staking):
    ####################################################################################
    print('===============================================')
    print('1. Single staker gets all reward')

    stake_amt = 10**18
    reward_amt = 10**16

    staking.stake(stake_amt, {'from': alice})  # stake 1 ALPHA
    staking.reward(reward_amt, {'from': worker})  # reward 0.01 ALPHA

    assert staking.totalShare() == stake_amt, 'incorrect share'
    assert staking.totalAlpha() == stake_amt + reward_amt, 'incorrect total alpha'
    assert staking.getStakeValue(alice) == stake_amt + reward_amt, 'incorrect reward to alice'
    assert alpha.balanceOf(staking) == stake_amt + reward_amt, 'incorrect alpha in staking'

    ####################################################################################
    print('===============================================')
    print('2. Reward split')

    bob_stake_amt = 2 * 10**18

    staking.stake(bob_stake_amt, {'from': bob})  # stake 2 ALPHA

    assert staking.totalAlpha() == 301 * 10**16, 'incorrect total alpha'
    assert staking.totalShare() == bob_stake_amt * stake_amt // (stake_amt +
                                                                 reward_amt) + stake_amt, 'incorrect total share'

    reward_amt_2 = 100 * 10**18

    staking.reward(reward_amt_2, {'from': worker})

    assert staking.totalShare() == bob_stake_amt * stake_amt // (stake_amt +
                                                                 reward_amt) + stake_amt, 'incorrect total share'
    assert staking.totalAlpha() == stake_amt + reward_amt + bob_stake_amt + \
        reward_amt_2, 'incorrect total alpha'

    assert staking.getStakeValue(alice) == stake_amt + reward_amt + reward_amt_2 * \
        stake_amt // (staking.totalShare()), 'incorrect alpha alice'

    assert staking.getStakeValue(bob) == bob_stake_amt + reward_amt_2 * \
        (staking.totalShare() - stake_amt) // staking.totalShare(), 'incorrect bob alice'
