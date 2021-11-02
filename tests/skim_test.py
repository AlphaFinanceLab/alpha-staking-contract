from brownie import interface, Contract, accounts
import brownie


def test_not_enough_alpha(staking, deployer, alpha, alice, bob):
    assert alpha.balanceOf(staking) == 0, "invalid initial alpha in staking contract"

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        staking.skim(1, {"from": deployer})

    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    assert alpha.balanceOf(staking) > 0, "invalid alpha after stake"

    with brownie.reverts("skim/not-enough-balance"):
        staking.skim(1, {"from": deployer})


def test_not_enough_alpha_before_upgrade(
    staking, staking_v2, proxy_admin, deployer, alpha, alice, bob
):
    assert alpha.balanceOf(staking) == 0, "invalid initial alpha in staking contract"

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        staking.skim(1, {"from": deployer})

    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    proxy_admin.upgrade(staking, staking_v2)

    assert alpha.balanceOf(staking) > 0, "invalid alpha after stake"

    with brownie.reverts("skim/not-enough-balance"):
        staking.skim(1, {"from": deployer})


def test_not_enough_alpha_after_upgrade(
    upgraded_staking_v2, deployer, alpha, alice, bob
):
    assert (
        alpha.balanceOf(upgraded_staking_v2) == 0
    ), "invalid initial alpha in upgraded_staking_v2 contract"

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        upgraded_staking_v2.skim(1, {"from": deployer})

    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v2.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v2.stake(bob_stake_amt, {"from": bob})

    assert alpha.balanceOf(upgraded_staking_v2) > 0, "invalid alpha after stake"

    with brownie.reverts("skim/not-enough-balance"):
        upgraded_staking_v2.skim(1, {"from": deployer})


def test_not_gov_skim(staking, bob):
    with brownie.reverts("onlyGov/not-governor"):
        staking.skim(0, {"from": bob})


def test_not_gov_skim_after_upgrade(upgraded_staking_v2, bob):
    with brownie.reverts("onlyGov/not-governor"):
        upgraded_staking_v2.skim(0, {"from": bob})


def test_skim(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    alpha.transfer(staking, 1000, {"from": alice})
    prevDeployerBal = alpha.balanceOf(deployer)

    staking.skim(1000, {"from": deployer})
    curDeployerBal = alpha.balanceOf(deployer)

    assert curDeployerBal - prevDeployerBal == 1000, "incorrect skim amount"


def test_skim_before_upgrade(
    a, deployer, alice, bob, worker, alpha, staking, staking_v2, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    proxy_admin.upgrade(staking, staking_v2)

    alpha.transfer(staking, 1000, {"from": alice})
    prevDeployerBal = alpha.balanceOf(deployer)

    staking.skim(1000, {"from": deployer})
    curDeployerBal = alpha.balanceOf(deployer)

    assert curDeployerBal - prevDeployerBal == 1000, "incorrect skim amount"


def test_skim_after_upgrade(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v2.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v2.stake(bob_stake_amt, {"from": bob})

    alpha.transfer(upgraded_staking_v2, 1000, {"from": alice})
    prevDeployerBal = alpha.balanceOf(deployer)

    upgraded_staking_v2.skim(1000, {"from": deployer})
    curDeployerBal = alpha.balanceOf(deployer)

    assert curDeployerBal - prevDeployerBal == 1000, "incorrect skim amount"


# ------------------------------------------- Alpha staking v3 --------------------------------------
def test_not_enough_alpha_staking_v3(upgraded_staking_v3, deployer, alpha, alice, bob):
    assert (
        alpha.balanceOf(upgraded_staking_v3) == 0
    ), "invalid initial alpha in upgraded_staking_v3 contract"

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        upgraded_staking_v3.skim(1, {"from": deployer})

    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v3.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob_stake_amt, {"from": bob})

    assert alpha.balanceOf(upgraded_staking_v3) > 0, "invalid alpha after stake"

    with brownie.reverts("skim/not-enough-balance"):
        upgraded_staking_v3.skim(1, {"from": deployer})


def test_not_enough_alpha_before_upgrade_staking_v3(
    upgraded_staking_v2, staking_v3, proxy_admin, deployer, alpha, alice, bob
):
    staking = upgraded_staking_v2
    assert alpha.balanceOf(staking) == 0, "invalid initial alpha in staking contract"

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        staking.skim(1, {"from": deployer})

    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    proxy_admin.upgrade(staking, staking_v3)

    assert alpha.balanceOf(staking) > 0, "invalid alpha after stake"

    with brownie.reverts("skim/not-enough-balance"):
        staking.skim(1, {"from": deployer})


def test_not_enough_alpha_after_upgrade_staking_v3(
    upgraded_staking_v3, deployer, alpha, alice, bob
):
    assert (
        alpha.balanceOf(upgraded_staking_v3) == 0
    ), "invalid initial alpha in upgraded_staking_v3 contract"

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        upgraded_staking_v3.skim(1, {"from": deployer})

    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v3.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob_stake_amt, {"from": bob})

    assert alpha.balanceOf(upgraded_staking_v3) > 0, "invalid alpha after stake"

    with brownie.reverts("skim/not-enough-balance"):
        upgraded_staking_v3.skim(1, {"from": deployer})


def test_not_gov_skim_after_upgrade_staking_3(upgraded_staking_v3, bob):
    with brownie.reverts("onlyGov/not-governor"):
        upgraded_staking_v3.skim(0, {"from": bob})


def test_skim_staking_v3(a, deployer, alice, bob, worker, alpha, upgraded_staking_v3):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v3.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob_stake_amt, {"from": bob})

    alpha.transfer(upgraded_staking_v3, 1000, {"from": alice})
    prevDeployerBal = alpha.balanceOf(deployer)

    upgraded_staking_v3.skim(1000, {"from": deployer})
    curDeployerBal = alpha.balanceOf(deployer)

    assert curDeployerBal - prevDeployerBal == 1000, "incorrect skim amount"


def test_skim_before_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2, staking_v3, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v2.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v2.stake(bob_stake_amt, {"from": bob})

    proxy_admin.upgrade(upgraded_staking_v2, staking_v3)

    alpha.transfer(upgraded_staking_v2, 1000, {"from": alice})
    prevDeployerBal = alpha.balanceOf(deployer)

    upgraded_staking_v2.skim(1000, {"from": deployer})
    curDeployerBal = alpha.balanceOf(deployer)

    assert curDeployerBal - prevDeployerBal == 1000, "incorrect skim amount"


def test_skim_after_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v3.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob_stake_amt, {"from": bob})

    alpha.transfer(upgraded_staking_v3, 1000, {"from": alice})
    prevDeployerBal = alpha.balanceOf(deployer)

    upgraded_staking_v3.skim(1000, {"from": deployer})
    curDeployerBal = alpha.balanceOf(deployer)

    assert curDeployerBal - prevDeployerBal == 1000, "incorrect skim amount"