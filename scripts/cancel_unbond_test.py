from brownie import interface, Contract, accounts, chain
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
import brownie
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
    print('1. Unbond -> Stake')

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)
    assert prev_status == 0, 'incorrect alice status before unbond'
    assert prev_unbondtime == 0, 'incorrect unbond time before unbond'
    assert prev_unbondshare == 0, 'incorrect unbond share before unbond'

    tx = staking.unbond(prev_share // 3, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after unbond'
    assert cur_unbondshare == prev_share // 3, 'incorrect unbond share after unbond'

    staking.stake(10**18, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 0, 'incorrect alice status after re-stake'
    assert cur_unbondtime == 0, 'incorrect unbond time after re-stake'
    assert cur_unbondshare == 0, 'incorrect unbond share after re-stake'

    ####################################################################################
    print('===============================================')
    print('2. Unbond -> Unbond')

    tx = staking.unbond(prev_share // 3, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after unbond'
    assert cur_unbondshare == prev_share // 3, 'incorrect unbond share after unbond'

    tx = staking.unbond(prev_share // 4, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after re-unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after re-unbond'
    assert cur_unbondshare == prev_share // 4, 'incorrect unbond share after re-unbond'

    ####################################################################################
    print('===============================================')
    print('3. Unbond (wait 7 days, enter withdraw period) -> Stake')

    tx = staking.unbond(prev_share // 3, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after unbond'
    assert cur_unbondshare == prev_share // 3, 'incorrect unbond share after unbond'

    # wait 7 days
    chain.sleep(7 * 86400)

    # re-stake
    staking.stake(10**18, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 0, 'incorrect alice status after re-stake'
    assert cur_unbondtime == 0, 'incorrect unbond time after re-stake'
    assert cur_unbondshare == 0, 'incorrect unbond share after re-stake'

    ####################################################################################
    print('===============================================')
    print('4. Unbond (wait 7 days, enter withdraw period) -> Unbond')

    tx = staking.unbond(prev_share // 3, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after unbond'
    assert cur_unbondshare == prev_share // 3, 'incorrect unbond share after unbond'

    # wait 7 days
    chain.sleep(7 * 86400)

    # re-stake
    tx = staking.unbond(prev_share // 4, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after re-unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after re-unbond'
    assert cur_unbondshare == prev_share // 4, 'incorrect unbond share after re-unbond'

    ####################################################################################
    print('===============================================')
    print('5. Unbond (wait 10 days, withdraw period expires) -> Stake')

    tx = staking.unbond(prev_share // 3, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after unbond'
    assert cur_unbondshare == prev_share // 3, 'incorrect unbond share after unbond'

    # wait 10 days
    chain.sleep(10 * 86400)

    # re-stake
    staking.stake(10**18, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 0, 'incorrect alice status after re-stake'
    assert cur_unbondtime == 0, 'incorrect unbond time after re-stake'
    assert cur_unbondshare == 0, 'incorrect unbond share after re-stake'

    ####################################################################################
    print('===============================================')
    print('6. Unbond (wait 10 days, withdraw period expires) -> Unbond')

    tx = staking.unbond(prev_share // 3, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after unbond'
    assert cur_unbondshare == prev_share // 3, 'incorrect unbond share after unbond'

    # wait 10 days
    chain.sleep(10 * 86400)

    # re-stake
    tx = staking.unbond(prev_share // 4, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after re-unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after re-unbond'
    assert cur_unbondshare == prev_share // 4, 'incorrect unbond share after re-unbond'
