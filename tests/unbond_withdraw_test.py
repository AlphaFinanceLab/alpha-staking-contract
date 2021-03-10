from brownie import interface, Contract, accounts, chain
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
import brownie

def test_unbond_withdraw(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    # setup stake
    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    ####################################################################################
    print('===============================================')
    print('1. Unbond states')

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)
    assert prev_status == 0, 'incorrect alice status before unbond'
    assert prev_unbondtime == 0, 'incorrect unbond time before unbond'
    assert prev_unbondshare == 0, 'incorrect unbond share before unbond'

    tx = staking.unbond(prev_share // 3, {'from': alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, 'incorrect alice status after unbond'
    assert cur_unbondtime == tx.timestamp, 'incorrect unbond time after unbond'
    assert cur_unbondshare == prev_share // 3, 'incorrect unbond share after unbond'

    ####################################################################################
    print('===============================================')
    print('2. Try withdraw before time (revert expected)')

    with brownie.reverts('withdraw/not-valid'):
        staking.withdraw({'from': alice})

    ####################################################################################
    print('===============================================')
    print('3. wait -> withdraw')

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

    ####################################################################################
    print('===============================================')
    print('4. Try unbond -> withdraw expires (revert expected)')

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)

    staking.unbond(prev_share, {'from': alice})

    chain.sleep(8 * 86400 + 1)

    with brownie.reverts('withdraw/already-expired'):
        staking.withdraw({'from': alice})
