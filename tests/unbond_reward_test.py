from brownie import chain
import brownie


def test_unbond_reward(a, staking, deployer, alice, bob, worker, alpha):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    # setup stake
    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    ####################################################################################
    print("===============================================")
    print("1. unbond -> reward (before 7 days) -> withdraw. still get reward")

    staking.unbond(alice_stake_amt // 4, {"from": alice})

    reward_amt = 4 * 10 ** 18

    staking.reward(reward_amt, {"from": worker})  # reward before 7 days

    chain.sleep(7 * 86400)

    prevAliceBal = alpha.balanceOf(alice)

    staking.withdraw({"from": alice})

    curAliceBal = alpha.balanceOf(alice)

    assert (
        curAliceBal - prevAliceBal == alice_stake_amt // 4 * 2
    ), "incorrect withdraw amount (should get reward)"

    ####################################################################################
    print("===============================================")
    print("2. unbond -> reward (after 7 days) -> withdraw. still get reward")

    staking.unbond(alice_stake_amt // 4, {"from": alice})

    reward_amt = 75 * 10 ** 17

    chain.sleep(7 * 86400 + 10)

    staking.reward(reward_amt, {"from": worker})  # reward after 7 days

    prevAliceBal = alpha.balanceOf(alice)

    staking.withdraw({"from": alice})

    curAliceBal = alpha.balanceOf(alice)

    assert (
        curAliceBal - prevAliceBal == alice_stake_amt // 4 * 4
    ), "incorrect withdraw amount (should get reward)"


def test_unbond_reward_cross_upgrade_period(
    a, staking, staking_v2, proxy_admin, deployer, alice, bob, worker, alpha
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    # setup stake
    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    ####################################################################################
    print("===============================================")
    print("1. unbond -> reward (after 7 days) -> withdraw. still get reward ")

    staking.unbond(alice_stake_amt // 4, {"from": alice})

    reward_amt = 4 * 10 ** 18

    staking.reward(reward_amt, {"from": worker})  # reward before 7 days

    chain.sleep(7 * 86400 + 10)

    prevAliceBal = alpha.balanceOf(alice)

    staking.withdraw({"from": alice})

    curAliceBal = alpha.balanceOf(alice)

    assert (
        curAliceBal - prevAliceBal == alice_stake_amt // 4 * 2
    ), "incorrect withdraw amount (should get reward)"

    ####################################################################################
    print("===============================================")
    print(
        "2. unbond -> reward (after 7 days) -> upgrade -> withdraw fail -> reward (after another 23 days) -> withdraw. get reward"
    )

    staking.unbond(alice_stake_amt // 4, {"from": alice})

    reward_amt = 75 * 10 ** 17

    chain.sleep(7 * 86400 + 10)

    # upgrade to 30days
    proxy_admin.upgrade(staking, staking_v2)

    staking.reward(reward_amt, {"from": worker})  # reward after 7 days

    prevAliceBal = alpha.balanceOf(alice)

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    # wait
    chain.sleep(23 * 86400 + 10)

    staking.withdraw({"from": alice})

    curAliceBal = alpha.balanceOf(alice)

    assert (
        curAliceBal - prevAliceBal == alice_stake_amt // 4 * 4
    ), "incorrect withdraw amount (should get reward)"


# ------------------------------------------- Alpha staking v3 --------------------------------------
def test_unbond_reward_staking_v3(
    a, upgraded_staking_v3, deployer, alice, bob, worker, alpha
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    # setup stake
    upgraded_staking_v3.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob_stake_amt, {"from": bob})

    ####################################################################################
    print("===============================================")
    print("1. unbond -> reward (before 30 days) -> withdraw. still get reward")

    upgraded_staking_v3.unbond(alice_stake_amt // 4, {"from": alice})

    reward_amt = 4 * 10 ** 18

    upgraded_staking_v3.reward(reward_amt, {"from": worker})  # reward before 7 days

    chain.sleep(30 * 86400)

    prevAliceBal = alpha.balanceOf(alice)

    upgraded_staking_v3.withdraw({"from": alice})

    curAliceBal = alpha.balanceOf(alice)

    assert (
        curAliceBal - prevAliceBal == alice_stake_amt // 4 * 2
    ), "incorrect withdraw amount (should get reward)"

    ####################################################################################
    print("===============================================")
    print("2. unbond -> reward (after 30 days) -> withdraw. still get reward")

    upgraded_staking_v3.unbond(alice_stake_amt // 4, {"from": alice})

    reward_amt = 75 * 10 ** 17

    chain.sleep(30 * 86400 + 10)

    upgraded_staking_v3.reward(reward_amt, {"from": worker})  # reward after 30 days

    prevAliceBal = alpha.balanceOf(alice)

    upgraded_staking_v3.withdraw({"from": alice})

    curAliceBal = alpha.balanceOf(alice)

    assert (
        curAliceBal - prevAliceBal == alice_stake_amt // 4 * 4
    ), "incorrect withdraw amount (should get reward)"
