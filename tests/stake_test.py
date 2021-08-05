from brownie import interface, Contract, accounts
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
from brownie.exceptions import VirtualMachineError


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


def test_single_stake_after_upgrade(a, alice, worker, alpha, upgraded_staking):
    stake_amt = 10 ** 18
    reward_amt = 10 ** 16

    upgraded_staking.stake(stake_amt, {"from": alice})  # stake 1 ALPHA
    upgraded_staking.reward(reward_amt, {"from": worker})  # reward 0.01 ALPHA

    assert upgraded_staking.totalShare() == stake_amt, "incorrect share"
    assert (
        upgraded_staking.totalAlpha() == stake_amt + reward_amt
    ), "incorrect total alpha"
    assert (
        upgraded_staking.getStakeValue(alice) == stake_amt + reward_amt
    ), "incorrect reward to alice"
    assert (
        alpha.balanceOf(staking) == stake_amt + reward_amt
    ), "incorrect alpha in staking"


def test_many_stake_after_upgrade(a, alice, bob, worker, alpha, upgraded_staking):
    stake_amt = 10 ** 18
    reward_amt = 10 ** 16

    upgraded_staking.stake(stake_amt, {"from": alice})  # stake 1 ALPHA
    upgraded_staking.reward(reward_amt, {"from": worker})  # reward 0.01 ALPHA

    bob_stake_amt = 2 * 10 ** 18
    upgraded_staking.stake(bob_stake_amt, {"from": bob})  # stake 2 ALPHA

    assert upgraded_staking.totalAlpha() == 301 * 10 ** 16, "incorrect total alpha"
    assert (
        upgraded_staking.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"

    reward_amt_2 = 100 * 10 ** 18
    upgraded_staking.reward(reward_amt_2, {"from": worker})

    assert (
        upgraded_staking.totalShare()
        == bob_stake_amt * stake_amt // (stake_amt + reward_amt) + stake_amt
    ), "incorrect total share"
    assert (
        upgraded_staking.totalAlpha()
        == stake_amt + reward_amt + bob_stake_amt + reward_amt_2
    ), "incorrect total alpha"
    assert upgraded_staking.getStakeValue(
        alice
    ) == stake_amt + reward_amt + reward_amt_2 * stake_amt // (
        upgraded_staking.totalShare()
    ), "incorrect alpha alice"
    assert (
        upgraded_staking.getStakeValue(bob)
        == bob_stake_amt
        + reward_amt_2
        * (upgraded_staking.totalShare() - stake_amt)
        // upgraded_staking.totalShare()
    ), "incorrect bob alice"
