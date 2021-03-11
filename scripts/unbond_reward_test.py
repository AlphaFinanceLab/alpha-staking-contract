from brownie import interface, Contract, accounts
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
from brownie.exceptions import VirtualMachineError
from .utils import *


def main():
    deployer, alice, bob, worker, alpha, proxy_admin, staking_impl, staking = setup()

    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    # setup stake
    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    ####################################################################################
    print('===============================================')
    print('1. unbond -> reward (before 7 days) -> withdraw. still get reward')

    staking.unbond(alice_stake_amt // 4, {'from': alice})

    reward_amt = 4 * 10**18

    staking.reward(reward_amt, {'from': worker})  # reward before 7 days

    chain.sleep(7 * 86400)

    prevAliceBal = alpha.balanceOf(alice)

    staking.withdraw({'from': alice})

    curAliceBal = alpha.balanceOf(alice)

    assert curAliceBal - prevAliceBal == alice_stake_amt // 4 * \
        2, 'incorrect withdraw amount (should get reward)'

    ####################################################################################
    print('===============================================')
    print('2. unbond -> reward (after 7 days) -> withdraw. still get reward')

    staking.unbond(alice_stake_amt // 4, {'from': alice})

    reward_amt = 75 * 10**17

    chain.sleep(7 * 86400 + 10)

    staking.reward(reward_amt, {'from': worker})  # reward after 7 days

    prevAliceBal = alpha.balanceOf(alice)

    staking.withdraw({'from': alice})

    curAliceBal = alpha.balanceOf(alice)

    assert curAliceBal - prevAliceBal == alice_stake_amt // 4 * \
        4, 'incorrect withdraw amount (should get reward)'
