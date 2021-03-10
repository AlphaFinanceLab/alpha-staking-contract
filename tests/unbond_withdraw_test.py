from brownie import interface, Contract, accounts, chain
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
import brownie
import math

def test_unbond_withdraw(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    # setup stake
    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)
    assert prev_status == 0, 'incorrect alice status before unbond'
    assert prev_unbondtime == 0, 'incorrect unbond time before unbond'
    assert prev_unbondshare == 0, 'incorrect unbond share before unbond'

    tx = staking.unbond(prev_share // 3, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after unbond'
    assert cur_unbondshare == prev_share // 3, 'incorrect unbond share after unbond'

    chain.sleep(7 * 86400)

    prevAliceBal = alpha.balanceOf(alice)

    staking.withdraw({'from': alice})

    curAliceBal = alpha.balanceOf(alice)

    assert curAliceBal - prevAliceBal == alice_stake_amt // 3, 'incorrect withdraw amount'

    # check status resets
    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 0, 'incorrect alice status after withdraw'
    assert cur_unbondtime == 0, 'incorrect unbond time after withdraw'
    assert cur_unbondshare == 0, 'incorrect unbond share after withdraw'

def test_unbond_more_than_share(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    # setup stake
    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)

    with brownie.reverts('unbond/insufficient-share'):
        staking.unbond(math.floor(prev_share * 1.5), {'from': alice})


def test_withdraw_before_time(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    with brownie.reverts('withdraw/not-valid'):
        staking.withdraw({'from': alice})

def test_withdraw_after_expire(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)
    staking.unbond(prev_share, {'from': alice})

    chain.sleep(8 * 86400 + 1)

    with brownie.reverts('withdraw/already-expired'):
        staking.withdraw({'from': alice})
