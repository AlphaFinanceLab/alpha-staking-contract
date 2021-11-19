from brownie import interface, Contract, accounts
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
from brownie.exceptions import VirtualMachineError
import brownie


def test_single_stake(a, alice, worker, alpha, staking):
    stake_amt = 10 ** 18
    reward_amt = 10 ** 16

    staking.stake(stake_amt, {"from": alice})  # stake 1 ALPHA
    staking.reward(reward_amt, {"from": worker})  # reward 0.01 ALPHA

    assert staking.totalShare() == stake_amt, "incorrect share"
    assert staking.totalAlpha() == stake_amt + reward_amt, "incorrect total alpha"
    assert (
        staking.getStakeValue(alice) == stake_amt + reward_amt
    ), "incorrect reward to alice"
    assert (
        alpha.balanceOf(staking) == stake_amt + reward_amt
    ), "incorrect alpha in staking"


def test_single_stake_after_upgrade(a, alice, worker, alpha, upgraded_staking_v2):
    stake_amt = 10 ** 18
    reward_amt = 10 ** 16

    upgraded_staking_v2.stake(stake_amt, {"from": alice})  # stake 1 ALPHA
    upgraded_staking_v2.reward(reward_amt, {"from": worker})  # reward 0.01 ALPHA

    assert upgraded_staking_v2.totalShare() == stake_amt, "incorrect share"
    assert (
        upgraded_staking_v2.totalAlpha() == stake_amt + reward_amt
    ), "incorrect total alpha"
    assert (
        upgraded_staking_v2.getStakeValue(alice) == stake_amt + reward_amt
    ), "incorrect reward to alice"
    assert (
        alpha.balanceOf(upgraded_staking_v2) == stake_amt + reward_amt
    ), "incorrect alpha in staking"


def test_many_stake_after_upgrade(a, alice, bob, worker, alpha, upgraded_staking_v2):
    stake_amt = 10 ** 18
    reward_amt = 10 ** 16

    upgraded_staking_v2.stake(stake_amt, {"from": alice})  # stake 1 ALPHA
    upgraded_staking_v2.reward(reward_amt, {"from": worker})  # reward 0.01 ALPHA

    bob_stake_amt = 2 * 10 ** 18
    upgraded_staking_v2.stake(bob_stake_amt, {"from": bob})  # stake 2 ALPHA

    assert upgraded_staking_v2.totalAlpha() == 301 * 10 ** 16, "incorrect total alpha"
    assert (
        upgraded_staking_v2.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"

    reward_amt_2 = 100 * 10 ** 18
    upgraded_staking_v2.reward(reward_amt_2, {"from": worker})

    assert (
        upgraded_staking_v2.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"
    assert (
        upgraded_staking_v2.totalAlpha()
        == stake_amt + reward_amt + bob_stake_amt + reward_amt_2
    ), "incorrect total alpha"
    assert upgraded_staking_v2.getStakeValue(
        alice
    ) == stake_amt + reward_amt + reward_amt_2 * stake_amt // (
        upgraded_staking_v2.totalShare()
    ), "incorrect alpha alice"
    assert (
        upgraded_staking_v2.getStakeValue(bob)
        == bob_stake_amt
        + reward_amt_2
        * (upgraded_staking_v2.totalShare() - stake_amt)
        // upgraded_staking_v2.totalShare()
    ), "incorrect bob alice"


# ------------------------------------------- Alpha staking v3 --------------------------------------
def test_single_stake_after_upgrade_staking_v3(
    a, alice, worker, alpha, upgraded_staking_v3
):
    stake_amt = 10 ** 18
    reward_amt = 10 ** 16

    upgraded_staking_v3.stake(alice, stake_amt, {"from": alice})  # stake 1 ALPHA
    upgraded_staking_v3.reward(reward_amt, {"from": worker})  # reward 0.01 ALPHA

    assert upgraded_staking_v3.totalShare() == stake_amt, "incorrect share"
    assert (
        upgraded_staking_v3.totalAlpha() == stake_amt + reward_amt
    ), "incorrect total alpha"
    assert (
        upgraded_staking_v3.getStakeValue(alice) == stake_amt + reward_amt
    ), "incorrect reward to alice"
    assert (
        alpha.balanceOf(upgraded_staking_v3) == stake_amt + reward_amt
    ), "incorrect alpha in upgraded_staking_v3"


def test_many_stake_after_upgrade_staking_v3(
    a, alice, bob, worker, alpha, upgraded_staking_v3
):
    stake_amt = 10 ** 18
    reward_amt = 10 ** 16

    upgraded_staking_v3.stake(alice, stake_amt, {"from": alice})  # stake 1 ALPHA
    upgraded_staking_v3.reward(reward_amt, {"from": worker})  # reward 0.01 ALPHA

    bob_stake_amt = 2 * 10 ** 18
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})  # stake 2 ALPHA

    assert upgraded_staking_v3.totalAlpha() == 301 * 10 ** 16, "incorrect total alpha"
    assert (
        upgraded_staking_v3.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"

    reward_amt_2 = 100 * 10 ** 18
    upgraded_staking_v3.reward(reward_amt_2, {"from": worker})

    assert (
        upgraded_staking_v3.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"
    assert (
        upgraded_staking_v3.totalAlpha()
        == stake_amt + reward_amt + bob_stake_amt + reward_amt_2
    ), "incorrect total alpha"
    assert upgraded_staking_v3.getStakeValue(
        alice
    ) == stake_amt + reward_amt + reward_amt_2 * stake_amt // (
        upgraded_staking_v3.totalShare()
    ), "incorrect alpha alice"
    assert (
        upgraded_staking_v3.getStakeValue(bob)
        == bob_stake_amt
        + reward_amt_2
        * (upgraded_staking_v3.totalShare() - stake_amt)
        // upgraded_staking_v3.totalShare()
    ), "incorrect bob alice"


def test_stake_for_staking_v3(
    a, alice, bob, worker, alpha, upgraded_staking_v3, merkle
):
    stake_amt = 10 ** 18
    reward_amt = 10 ** 16

    upgraded_staking_v3.stake(
        alice, stake_amt, {"from": merkle}
    )  # merkle stakes 1 ALPHA for alice
    upgraded_staking_v3.reward(reward_amt, {"from": worker})  # reward 0.01 ALPHA

    bob_stake_amt = 2 * 10 ** 18
    upgraded_staking_v3.stake(
        bob, bob_stake_amt, {"from": merkle}
    )  # merkle stakes 2 ALPHA for alice

    assert upgraded_staking_v3.totalAlpha() == 301 * 10 ** 16, "incorrect total alpha"
    assert (
        upgraded_staking_v3.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"

    reward_amt_2 = 100 * 10 ** 18
    upgraded_staking_v3.reward(reward_amt_2, {"from": worker})

    assert (
        upgraded_staking_v3.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"
    assert (
        upgraded_staking_v3.totalAlpha()
        == stake_amt + reward_amt + bob_stake_amt + reward_amt_2
    ), "incorrect total alpha"
    assert upgraded_staking_v3.getStakeValue(
        alice
    ) == stake_amt + reward_amt + reward_amt_2 * stake_amt // (
        upgraded_staking_v3.totalShare()
    ), "incorrect alpha alice"
    assert (
        upgraded_staking_v3.getStakeValue(bob)
        == bob_stake_amt
        + reward_amt_2
        * (upgraded_staking_v3.totalShare() - stake_amt)
        // upgraded_staking_v3.totalShare()
    ), "incorrect bob alice"


def test_stake_for_with_normal_stake_staking_v3(
    a, alice, bob, worker, alpha, upgraded_staking_v3, merkle
):
    stake_amt = 10 ** 18
    reward_amt = 10 ** 16

    upgraded_staking_v3.stake(
        alice, stake_amt, {"from": merkle}
    )  # merkle stakes 1 ALPHA for alice
    upgraded_staking_v3.reward(reward_amt, {"from": worker})  # reward 0.01 ALPHA

    bob_stake_amt = 2 * 10 ** 18
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})  # bob stakes 2 ALPHA

    assert upgraded_staking_v3.totalAlpha() == 301 * 10 ** 16, "incorrect total alpha"
    assert (
        upgraded_staking_v3.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"

    reward_amt_2 = 100 * 10 ** 18
    upgraded_staking_v3.reward(reward_amt_2, {"from": worker})

    assert (
        upgraded_staking_v3.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"
    assert (
        upgraded_staking_v3.totalAlpha()
        == stake_amt + reward_amt + bob_stake_amt + reward_amt_2
    ), "incorrect total alpha"
    assert upgraded_staking_v3.getStakeValue(
        alice
    ) == stake_amt + reward_amt + reward_amt_2 * stake_amt // (
        upgraded_staking_v3.totalShare()
    ), "incorrect alpha alice"
    assert (
        upgraded_staking_v3.getStakeValue(bob)
        == bob_stake_amt
        + reward_amt_2
        * (upgraded_staking_v3.totalShare() - stake_amt)
        // upgraded_staking_v3.totalShare()
    ), "incorrect bob alice"


def test_stake_for_by_other_user_staking_v3(alice, bob, upgraded_staking_v3):
    stake_amt = 10 ** 18
    with brownie.reverts("stake/caller-not-owner-or-merkle"):
        upgraded_staking_v3.stake(alice, stake_amt, {"from": bob})
