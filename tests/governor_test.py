import pytest
from brownie import interface
import brownie


def test_initial_governor(staking, deployer):
    assert staking.governor() == deployer, "incorrect deployer governor"


def test_initial_governor_after_upgrade(upgraded_staking_v2, deployer):
    assert upgraded_staking_v2.governor() == deployer, "incorrect deployer governor"


def test_pending_governor(staking):
    assert (
        staking.pendingGovernor() == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor"


def test_pending_governor_after_upgrade(upgraded_staking_v2):
    assert (
        upgraded_staking_v2.pendingGovernor()
        == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor"


def test_set_governor(staking, deployer, alice):
    staking.setPendingGovernor(alice, {"from": deployer})
    assert staking.governor() == deployer, "incorrect deployer governor after set"
    assert staking.pendingGovernor() == alice, "incorrect pending governor after set"


def test_set_governor_before_upgraded(
    staking, staking_v2, proxy_admin, deployer, alice
):
    staking.setPendingGovernor(alice, {"from": deployer})
    proxy_admin.upgrade(staking, staking_v2)
    assert staking.governor() == deployer, "incorrect deployer governor after set"
    assert staking.pendingGovernor() == alice, "incorrect pending governor after set"


def test_set_governor_after_upgrade(upgraded_staking_v2, deployer, alice):
    upgraded_staking_v2.setPendingGovernor(alice, {"from": deployer})
    assert (
        upgraded_staking_v2.governor() == deployer
    ), "incorrect deployer governor after set"
    assert (
        upgraded_staking_v2.pendingGovernor() == alice
    ), "incorrect pending governor after set"


def test_not_gov_set_pending_governor(deployer, staking, alice, bob):
    with brownie.reverts("onlyGov/not-governor"):
        staking.setPendingGovernor(alice, {"from": bob})


def test_not_gov_set_after_upgrade(deployer, upgraded_staking_v2, alice, bob):
    with brownie.reverts("onlyGov/not-governor"):
        upgraded_staking_v2.setPendingGovernor(alice, {"from": bob})


def test_accept_governor(staking, alice, deployer):
    staking.setPendingGovernor(alice, {"from": deployer})
    staking.acceptGovernor({"from": alice})
    assert staking.governor() == alice, "incorrect deployer governor after accept"
    assert (
        staking.pendingGovernor() == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


def test_accept_governor_before_upgrade(
    staking, staking_v2, proxy_admin, alice, deployer
):
    staking.setPendingGovernor(alice, {"from": deployer})
    staking.acceptGovernor({"from": alice})
    proxy_admin.upgrade(staking, staking_v2)
    assert staking.governor() == alice, "incorrect deployer governor after accept"
    assert (
        staking.pendingGovernor() == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


def test_accept_governor_after_upgrade(upgraded_staking_v2, alice, deployer):
    upgraded_staking_v2.setPendingGovernor(alice, {"from": deployer})
    upgraded_staking_v2.acceptGovernor({"from": alice})
    assert (
        upgraded_staking_v2.governor() == alice
    ), "incorrect deployer governor after accept"
    assert (
        upgraded_staking_v2.pendingGovernor()
        == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


def test_not_pending_accept_governor(staking, deployer, alice, bob):
    staking.setPendingGovernor(alice, {"from": deployer})
    with brownie.reverts("acceptGovernor/not-pending"):
        staking.acceptGovernor({"from": bob})
    assert staking.pendingGovernor() == alice, "incorrect pending governor after revert"


def test_not_pending_accept_governor_before_upgrade(
    staking, staking_v2, proxy_admin, deployer, alice, bob
):
    staking.setPendingGovernor(alice, {"from": deployer})
    proxy_admin.upgrade(staking, staking_v2)
    with brownie.reverts("acceptGovernor/not-pending"):
        staking.acceptGovernor({"from": bob})
    assert staking.pendingGovernor() == alice, "incorrect pending governor after revert"


def test_not_pending_accept_governor_after_upgrade(
    upgraded_staking_v2, deployer, alice, bob
):
    upgraded_staking_v2.setPendingGovernor(alice, {"from": deployer})
    with brownie.reverts("acceptGovernor/not-pending"):
        upgraded_staking_v2.acceptGovernor({"from": bob})
    assert (
        upgraded_staking_v2.pendingGovernor() == alice
    ), "incorrect pending governor after revert"


def test_set_governor_twice(staking, deployer, alice, bob):
    staking.setPendingGovernor(alice, {"from": deployer})
    assert staking.pendingGovernor() == alice, "incorrect pending governor after set"

    staking.setPendingGovernor(bob, {"from": deployer})
    assert staking.pendingGovernor() == bob, "incorrect pending governor after set"

    with brownie.reverts("acceptGovernor/not-pending"):
        staking.acceptGovernor({"from": alice})

    staking.acceptGovernor({"from": bob})
    assert staking.governor() == bob, "incorrect governor after accept"
    assert (
        staking.pendingGovernor() == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


def test_set_governor_twice_before_upgrade(
    staking, staking_v2, proxy_admin, deployer, alice, bob
):
    staking.setPendingGovernor(alice, {"from": deployer})
    assert staking.pendingGovernor() == alice, "incorrect pending governor after set"

    staking.setPendingGovernor(bob, {"from": deployer})
    assert staking.pendingGovernor() == bob, "incorrect pending governor after set"

    proxy_admin.upgrade(staking, staking_v2)

    with brownie.reverts("acceptGovernor/not-pending"):
        staking.acceptGovernor({"from": alice})

    staking.acceptGovernor({"from": bob})
    assert staking.governor() == bob, "incorrect governor after accept"
    assert (
        staking.pendingGovernor() == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


def test_set_governor_twice_after_upgrade(upgraded_staking_v2, deployer, alice, bob):
    upgraded_staking_v2.setPendingGovernor(alice, {"from": deployer})
    assert (
        upgraded_staking_v2.pendingGovernor() == alice
    ), "incorrect pending governor after set"

    upgraded_staking_v2.setPendingGovernor(bob, {"from": deployer})
    assert (
        upgraded_staking_v2.pendingGovernor() == bob
    ), "incorrect pending governor after set"

    with brownie.reverts("acceptGovernor/not-pending"):
        upgraded_staking_v2.acceptGovernor({"from": alice})

    upgraded_staking_v2.acceptGovernor({"from": bob})
    assert upgraded_staking_v2.governor() == bob, "incorrect governor after accept"
    assert (
        upgraded_staking_v2.pendingGovernor()
        == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


# ------------------------------------------- Alpha staking v3 --------------------------------------
def test_initial_governor_after_upgrade_staking_v3(upgraded_staking_v3, deployer):
    assert upgraded_staking_v3.governor() == deployer, "incorrect deployer governor"


def test_pending_governor_after_upgrade_staking_v3(upgraded_staking_v3):
    assert (
        upgraded_staking_v3.pendingGovernor()
        == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor"


def test_set_governor_before_upgraded_staking_v3(
    upgraded_staking_v2, staking_v3, proxy_admin, deployer, alice
):
    staking = upgraded_staking_v2
    staking.setPendingGovernor(alice, {"from": deployer})
    proxy_admin.upgrade(staking, staking_v3)
    assert staking.governor() == deployer, "incorrect deployer governor after set"
    assert staking.pendingGovernor() == alice, "incorrect pending governor after set"


def test_set_governor_after_upgrade_staking_v3(upgraded_staking_v3, deployer, alice):
    upgraded_staking_v3.setPendingGovernor(alice, {"from": deployer})
    assert (
        upgraded_staking_v3.governor() == deployer
    ), "incorrect deployer governor after set"
    assert (
        upgraded_staking_v3.pendingGovernor() == alice
    ), "incorrect pending governor after set"


def test_not_gov_set_after_upgrade_staking_v3(
    deployer, upgraded_staking_v3, alice, bob
):
    with brownie.reverts("onlyGov/not-governor"):
        upgraded_staking_v3.setPendingGovernor(alice, {"from": bob})


def test_accept_governor_before_upgrade_staking_v3(
    upgraded_staking_v2, staking_v3, proxy_admin, alice, deployer
):
    staking = upgraded_staking_v2
    staking.setPendingGovernor(alice, {"from": deployer})
    staking.acceptGovernor({"from": alice})
    proxy_admin.upgrade(staking, staking_v3)
    assert staking.governor() == alice, "incorrect deployer governor after accept"
    assert (
        staking.pendingGovernor() == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


def test_accept_governor_after_upgrade_staking_v3(upgraded_staking_v3, alice, deployer):
    upgraded_staking_v3.setPendingGovernor(alice, {"from": deployer})
    upgraded_staking_v3.acceptGovernor({"from": alice})
    assert (
        upgraded_staking_v3.governor() == alice
    ), "incorrect deployer governor after accept"
    assert (
        upgraded_staking_v3.pendingGovernor()
        == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


def test_not_pending_accept_governor_staking_v3(
    upgraded_staking_v3, deployer, alice, bob
):
    upgraded_staking_v3.setPendingGovernor(alice, {"from": deployer})
    with brownie.reverts("acceptGovernor/not-pending"):
        upgraded_staking_v3.acceptGovernor({"from": bob})
    assert (
        upgraded_staking_v3.pendingGovernor() == alice
    ), "incorrect pending governor after revert"


def test_not_pending_accept_governor_before_upgrade_staking_v3(
    upgraded_staking_v2, staking_v3, proxy_admin, deployer, alice, bob
):
    staking = upgraded_staking_v2
    staking.setPendingGovernor(alice, {"from": deployer})
    proxy_admin.upgrade(staking, staking_v3)
    with brownie.reverts("acceptGovernor/not-pending"):
        staking.acceptGovernor({"from": bob})
    assert staking.pendingGovernor() == alice, "incorrect pending governor after revert"


def test_not_pending_accept_governor_after_upgrade_staking_v3(
    upgraded_staking_v3, deployer, alice, bob
):
    upgraded_staking_v3.setPendingGovernor(alice, {"from": deployer})
    with brownie.reverts("acceptGovernor/not-pending"):
        upgraded_staking_v3.acceptGovernor({"from": bob})
    assert (
        upgraded_staking_v3.pendingGovernor() == alice
    ), "incorrect pending governor after revert"


def test_set_governor_twice_staking_v3(upgraded_staking_v3, deployer, alice, bob):
    upgraded_staking_v3.setPendingGovernor(alice, {"from": deployer})
    assert (
        upgraded_staking_v3.pendingGovernor() == alice
    ), "incorrect pending governor after set"

    upgraded_staking_v3.setPendingGovernor(bob, {"from": deployer})
    assert (
        upgraded_staking_v3.pendingGovernor() == bob
    ), "incorrect pending governor after set"

    with brownie.reverts("acceptGovernor/not-pending"):
        upgraded_staking_v3.acceptGovernor({"from": alice})

    upgraded_staking_v3.acceptGovernor({"from": bob})
    assert upgraded_staking_v3.governor() == bob, "incorrect governor after accept"
    assert (
        upgraded_staking_v3.pendingGovernor()
        == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


def test_set_governor_twice_before_upgrade_staking_v3(
    upgraded_staking_v2, staking_v3, proxy_admin, deployer, alice, bob
):
    staking = upgraded_staking_v2
    staking.setPendingGovernor(alice, {"from": deployer})
    assert staking.pendingGovernor() == alice, "incorrect pending governor after set"

    staking.setPendingGovernor(bob, {"from": deployer})
    assert staking.pendingGovernor() == bob, "incorrect pending governor after set"

    proxy_admin.upgrade(staking, staking_v3)

    with brownie.reverts("acceptGovernor/not-pending"):
        staking.acceptGovernor({"from": alice})

    staking.acceptGovernor({"from": bob})
    assert staking.governor() == bob, "incorrect governor after accept"
    assert (
        staking.pendingGovernor() == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"


def test_set_governor_twice_after_upgrade_staking_v3(
    upgraded_staking_v3, deployer, alice, bob
):
    upgraded_staking_v3.setPendingGovernor(alice, {"from": deployer})
    assert (
        upgraded_staking_v3.pendingGovernor() == alice
    ), "incorrect pending governor after set"

    upgraded_staking_v3.setPendingGovernor(bob, {"from": deployer})
    assert (
        upgraded_staking_v3.pendingGovernor() == bob
    ), "incorrect pending governor after set"

    with brownie.reverts("acceptGovernor/not-pending"):
        upgraded_staking_v3.acceptGovernor({"from": alice})

    upgraded_staking_v3.acceptGovernor({"from": bob})
    assert upgraded_staking_v3.governor() == bob, "incorrect governor after accept"
    assert (
        upgraded_staking_v3.pendingGovernor()
        == "0x0000000000000000000000000000000000000000"
    ), "incorrect pending governor after accept"