from brownie import interface, Contract, accounts, chain
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
import brownie
import math


def test_unbond_withdraw(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    # setup stake
    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)
    assert prev_status == 0, "incorrect alice status before unbond"
    assert prev_unbondtime == 0, "incorrect unbond time before unbond"
    assert prev_unbondshare == 0, "incorrect unbond share before unbond"

    tx = staking.unbond(prev_share // 3, {"from": alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 1, "incorrect alice status after unbond"
    assert cur_unbondtime == tx.timestamp, "incorrect unbond time after unbond"
    assert cur_unbondshare == prev_share // 3, "incorrect unbond share after unbond"

    chain.sleep(7 * 86400)

    prevAliceBal = alpha.balanceOf(alice)

    staking.withdraw({"from": alice})

    curAliceBal = alpha.balanceOf(alice)

    assert (
        curAliceBal - prevAliceBal == alice_stake_amt // 3
    ), "incorrect withdraw amount"

    # check status resets
    cur_status, cur_share, cur_unbondtime, cur_unbondshare = staking.users(alice)
    assert cur_status == 0, "incorrect alice status after withdraw"
    assert cur_unbondtime == 0, "incorrect unbond time after withdraw"
    assert cur_unbondshare == 0, "incorrect unbond share after withdraw"


def test_unbond_withdraw_after_uprade(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    # setup stake
    upgraded_staking_v2.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v2.stake(bob_stake_amt, {"from": bob})

    (
        prev_status,
        prev_share,
        prev_unbondtime,
        prev_unbondshare,
    ) = upgraded_staking_v2.users(alice)
    assert prev_status == 0, "incorrect alice status before unbond"
    assert prev_unbondtime == 0, "incorrect unbond time before unbond"
    assert prev_unbondshare == 0, "incorrect unbond share before unbond"

    tx = upgraded_staking_v2.unbond(prev_share // 3, {"from": alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = upgraded_staking_v2.users(
        alice
    )
    assert cur_status == 1, "incorrect alice status after unbond"
    assert cur_unbondtime == tx.timestamp, "incorrect unbond time after unbond"
    assert cur_unbondshare == prev_share // 3, "incorrect unbond share after unbond"

    chain.sleep(30 * 86400)

    prevAliceBal = alpha.balanceOf(alice)

    upgraded_staking_v2.withdraw({"from": alice})

    curAliceBal = alpha.balanceOf(alice)

    assert (
        curAliceBal - prevAliceBal == alice_stake_amt // 3
    ), "incorrect withdraw amount"

    # check status resets
    cur_status, cur_share, cur_unbondtime, cur_unbondshare = upgraded_staking_v2.users(
        alice
    )
    assert cur_status == 0, "incorrect alice status after withdraw"
    assert cur_unbondtime == 0, "incorrect unbond time after withdraw"
    assert cur_unbondshare == 0, "incorrect unbond share after withdraw"


def test_unbond_more_than_share(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    # setup stake
    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)

    with brownie.reverts("unbond/insufficient-share"):
        staking.unbond(math.floor(prev_share * 1.5), {"from": alice})


def test_unbond_more_than_share_after_upgrade(
    a, deployer, alice, bob, worker, alpha, staking, staking_v2, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    # setup stake
    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    proxy_admin.upgrade(staking, staking_v2)

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)

    with brownie.reverts("unbond/insufficient-share"):
        staking.unbond(math.floor(prev_share * 1.5), {"from": alice})


def test_withdraw_before_time(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)

    with brownie.reverts("withdraw/not-unbonding"):
        staking.withdraw({"from": alice})

    staking.unbond(prev_share, {"from": alice})
    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    chain.sleep(1 * 86400)
    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})


def test_withdraw_with_old_unbond_staked_time(
    alice, bob, staking, staking_v2, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)

    with brownie.reverts("withdraw/not-unbonding"):
        staking.withdraw({"from": alice})

    staking.unbond(prev_share, {"from": alice})

    # upgrade to 30 days
    proxy_admin.upgrade(staking, staking_v2)

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    chain.sleep(7 * 86400)
    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})


def test_withdraw_after_expire(alice, bob, worker, alpha, staking):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)
    staking.unbond(prev_share, {"from": alice})

    chain.sleep(33 * 86400 + 1)

    with brownie.reverts("withdraw/already-expired"):
        staking.withdraw({"from": alice})


def test_withdraw_after_new_unbond_period_expire(
    alice, bob, staking, staking_v2, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    proxy_admin.upgrade(staking, staking_v2)

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)
    staking.unbond(prev_share, {"from": alice})

    chain.sleep(33 * 86400 + 1)

    with brownie.reverts("withdraw/already-expired"):
        staking.withdraw({"from": alice})


def test_withdraw_both_before_and_after_upgrade(
    alice, bob, staking, staking_v2, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)

    staking.unbond(prev_share, {"from": alice})

    chain.sleep(7 * 86400 - 10)

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    proxy_admin.upgrade(staking, staking_v2)

    chain.sleep(23 * 86400)

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    chain.sleep(7 * 86400)

    with brownie.reverts("withdraw/already-expired"):
        staking.withdraw({"from": alice})


# ------------------------------------------- Alpha staking v3 --------------------------------------
def test_unbond_withdraw_after_uprade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    # setup stake
    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    (
        prev_status,
        prev_share,
        prev_unbondtime,
        prev_unbondshare,
    ) = upgraded_staking_v3.users(alice)
    assert prev_status == 0, "incorrect alice status before unbond"
    assert prev_unbondtime == 0, "incorrect unbond time before unbond"
    assert prev_unbondshare == 0, "incorrect unbond share before unbond"

    tx = upgraded_staking_v3.unbond(prev_share // 3, {"from": alice})

    cur_status, cur_share, cur_unbondtime, cur_unbondshare = upgraded_staking_v3.users(
        alice
    )
    assert cur_status == 1, "incorrect alice status after unbond"
    assert cur_unbondtime == tx.timestamp, "incorrect unbond time after unbond"
    assert cur_unbondshare == prev_share // 3, "incorrect unbond share after unbond"

    chain.sleep(30 * 86400)

    prevAliceBal = alpha.balanceOf(alice)

    upgraded_staking_v3.withdraw({"from": alice})

    curAliceBal = alpha.balanceOf(alice)

    assert (
        curAliceBal - prevAliceBal == alice_stake_amt // 3
    ), "incorrect withdraw amount"

    # check status resets
    cur_status, cur_share, cur_unbondtime, cur_unbondshare = upgraded_staking_v3.users(
        alice
    )
    assert cur_status == 0, "incorrect alice status after withdraw"
    assert cur_unbondtime == 0, "incorrect unbond time after withdraw"
    assert cur_unbondshare == 0, "incorrect unbond share after withdraw"


def test_unbond_more_than_share_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    # setup stake
    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    (
        prev_status,
        prev_share,
        prev_unbondtime,
        prev_unbondshare,
    ) = upgraded_staking_v3.users(alice)

    with brownie.reverts("unbond/insufficient-share"):
        upgraded_staking_v3.unbond(math.floor(prev_share * 1.5), {"from": alice})


def test_unbond_more_than_share_after_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2, staking_v3, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking = upgraded_staking_v2
    # setup stake
    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    proxy_admin.upgrade(staking, staking_v3)

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)

    with brownie.reverts("unbond/insufficient-share"):
        staking.unbond(math.floor(prev_share * 1.5), {"from": alice})


def test_withdraw_before_time_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    (
        prev_status,
        prev_share,
        prev_unbondtime,
        prev_unbondshare,
    ) = upgraded_staking_v3.users(alice)

    with brownie.reverts("withdraw/not-unbonding"):
        upgraded_staking_v3.withdraw({"from": alice})

    upgraded_staking_v3.unbond(prev_share, {"from": alice})
    with brownie.reverts("withdraw/not-valid"):
        upgraded_staking_v3.withdraw({"from": alice})

    chain.sleep(1 * 86400)
    with brownie.reverts("withdraw/not-valid"):
        upgraded_staking_v3.withdraw({"from": alice})


def test_withdraw_after_expire_staking_v3(
    alice, bob, worker, alpha, upgraded_staking_v3
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    (
        prev_status,
        prev_share,
        prev_unbondtime,
        prev_unbondshare,
    ) = upgraded_staking_v3.users(alice)
    upgraded_staking_v3.unbond(prev_share, {"from": alice})

    chain.sleep(33 * 86400 + 1)

    with brownie.reverts("withdraw/already-expired"):
        upgraded_staking_v3.withdraw({"from": alice})


def test_withdraw_after_new_unbond_period_expire_staking_v3(
    alice, bob, upgraded_staking_v2, staking_v3, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking = upgraded_staking_v2
    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    proxy_admin.upgrade(staking, staking_v3)

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)
    staking.unbond(prev_share, {"from": alice})

    chain.sleep(33 * 86400 + 1)

    with brownie.reverts("withdraw/already-expired"):
        staking.withdraw({"from": alice})


def test_withdraw_both_before_and_after_upgrade_staking_v3(
    alice, bob, upgraded_staking_v2, staking_v3, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking = upgraded_staking_v2

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prev_status, prev_share, prev_unbondtime, prev_unbondshare = staking.users(alice)

    staking.unbond(prev_share, {"from": alice})

    chain.sleep(7 * 86400 - 10)

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    proxy_admin.upgrade(staking, staking_v3)

    chain.sleep(23 * 86400)

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    chain.sleep(7 * 86400)

    with brownie.reverts("withdraw/already-expired"):
        staking.withdraw({"from": alice})
