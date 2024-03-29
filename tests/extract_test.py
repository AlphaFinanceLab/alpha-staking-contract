from brownie import interface, Contract, accounts, chain
import brownie


def test_not_gov_extract(a, alice, staking):
    with brownie.reverts("onlyGov/not-governor"):
        staking.extract(1000, {"from": alice})


def test_not_gov_extract_after_upgrade(a, alice, upgraded_staking_v2):
    with brownie.reverts("onlyGov/not-governor"):
        upgraded_staking_v2.extract(1000, {"from": alice})


def test_worker_extract(a, alice, worker, staking):
    assert staking.worker() == worker
    with brownie.reverts("onlyGov/not-governor"):
        staking.extract(1000, {"from": worker})


def test_worker_extract_after_upgrade(a, alice, worker, upgraded_staking_v2):
    assert upgraded_staking_v2.worker() == worker
    with brownie.reverts("onlyGov/not-governor"):
        upgraded_staking_v2.extract(1000, {"from": worker})


def test_not_enough_alpha(a, alice, bob, deployer, staking):
    alice_stake_amt = 10 ** 18
    staking.stake(alice_stake_amt, {"from": alice})
    with brownie.reverts("extract/too-low-total-alpha"):
        staking.extract(10 ** 18, {"from": deployer})


def test_not_enough_alpha_before_upgrade(
    a, alice, bob, deployer, staking, staking_v2, proxy_admin
):
    alice_stake_amt = 10 ** 18
    staking.stake(alice_stake_amt, {"from": alice})
    proxy_admin.upgrade(staking, staking_v2)
    with brownie.reverts("extract/too-low-total-alpha"):
        staking.extract(10 ** 18, {"from": deployer})


def test_not_enough_alpha_after_upgrade(a, alice, bob, deployer, upgraded_staking_v2):
    alice_stake_amt = 10 ** 18
    upgraded_staking_v2.stake(alice_stake_amt, {"from": alice})
    with brownie.reverts("extract/too-low-total-alpha"):
        upgraded_staking_v2.extract(10 ** 18, {"from": deployer})


def test_extract(a, deployer, alice, bob, worker, alpha, staking):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prevDeployerBal = alpha.balanceOf(deployer)

    staking.extract(1000, {"from": deployer})

    curDeployerBal = alpha.balanceOf(deployer)
    assert curDeployerBal - prevDeployerBal == 1000, "incorrect extract amount"


def test_extract_before_upgrade(
    a, deployer, alice, bob, worker, alpha, staking, staking_v2, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prevDeployerBal = alpha.balanceOf(deployer)

    staking.extract(1000, {"from": deployer})

    proxy_admin.upgrade(staking, staking_v2)

    curDeployerBal = alpha.balanceOf(deployer)
    assert curDeployerBal - prevDeployerBal == 1000, "incorrect extract amount"


def test_extract_after_upgrade(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v2.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v2.stake(bob_stake_amt, {"from": bob})

    prevDeployerBal = alpha.balanceOf(deployer)

    upgraded_staking_v2.extract(1000, {"from": deployer})

    curDeployerBal = alpha.balanceOf(deployer)
    assert curDeployerBal - prevDeployerBal == 1000, "incorrect extract amount"


def test_extract_during_unbond(a, deployer, alice, bob, worker, alpha, staking):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    staking.unbond(alice_stake_amt / 2, {"from": alice})

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    staking.extract(100 * 10 ** 18, {"from": deployer})

    chain.sleep(7 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    staking.withdraw({"from": alice})
    cur_alice_balance = alpha.balanceOf(alice)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 75 * 10 ** 18, "incorrect withdraw amount"

    staking.unbond(alice_stake_amt / 2, {"from": alice})
    staking.unbond(bob_stake_amt / 2, {"from": bob})

    staking.extract(150 * 10 ** 18, {"from": deployer})

    chain.sleep(7 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    staking.withdraw({"from": alice})
    staking.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"


def test_extract_during_unbond_before_upgrade(
    a, deployer, alice, bob, worker, alpha, staking, staking_v2, proxy_admin
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    staking.unbond(alice_stake_amt / 2, {"from": alice})

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    staking.extract(100 * 10 ** 18, {"from": deployer})

    chain.sleep(7 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    staking.withdraw({"from": alice})
    cur_alice_balance = alpha.balanceOf(alice)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 75 * 10 ** 18, "incorrect withdraw amount"

    # upgrade

    proxy_admin.upgrade(staking, staking_v2)

    staking.unbond(alice_stake_amt / 2, {"from": alice})
    staking.unbond(bob_stake_amt / 2, {"from": bob})

    staking.extract(150 * 10 ** 18, {"from": deployer})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    staking.withdraw({"from": alice})
    staking.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"


def test_extract_during_unbond_after_upgrade(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    upgraded_staking_v2.stake(alice_stake_amt, {"from": alice})
    upgraded_staking_v2.stake(bob_stake_amt, {"from": bob})

    upgraded_staking_v2.unbond(alice_stake_amt / 2, {"from": alice})

    with brownie.reverts("withdraw/not-valid"):
        upgraded_staking_v2.withdraw({"from": alice})

    upgraded_staking_v2.extract(100 * 10 ** 18, {"from": deployer})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    upgraded_staking_v2.withdraw({"from": alice})
    cur_alice_balance = alpha.balanceOf(alice)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 75 * 10 ** 18, "incorrect withdraw amount"

    upgraded_staking_v2.unbond(alice_stake_amt / 2, {"from": alice})
    upgraded_staking_v2.unbond(bob_stake_amt / 2, {"from": bob})

    upgraded_staking_v2.extract(150 * 10 ** 18, {"from": deployer})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    upgraded_staking_v2.withdraw({"from": alice})
    upgraded_staking_v2.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"


def test_staking_after_extract(a, deployer, alice, bob, worker, alpha, staking):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})

    staking.extract(100 * 10 ** 18, {"from": deployer})
    staking.stake(bob_stake_amt, {"from": bob})

    staking.unbond(alice_stake_amt, {"from": alice})
    staking.unbond(bob_stake_amt * 2 * 99 // 100, {"from": bob})

    chain.sleep(7 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    staking.withdraw({"from": alice})
    staking.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 100 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 198 * 10 ** 18, "incorrect withdraw amount"


def test_staking_after_extract_before_upgrade(
    a, deployer, alice, bob, worker, alpha, staking, staking_v2, proxy_admin
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})

    staking.extract(100 * 10 ** 18, {"from": deployer})
    staking.stake(bob_stake_amt, {"from": bob})

    staking.unbond(alice_stake_amt, {"from": alice})
    staking.unbond(bob_stake_amt * 2 * 99 // 100, {"from": bob})

    chain.sleep(7 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    # upgrade
    proxy_admin.upgrade(staking, staking_v2)

    # wait for next 23 d
    chain.sleep(23 * 86400)

    staking.withdraw({"from": alice})
    staking.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 100 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 198 * 10 ** 18, "incorrect withdraw amount"


def test_staking_after_extract_and_upgrade(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    upgraded_staking_v2.stake(alice_stake_amt, {"from": alice})

    upgraded_staking_v2.extract(100 * 10 ** 18, {"from": deployer})
    upgraded_staking_v2.stake(bob_stake_amt, {"from": bob})

    upgraded_staking_v2.unbond(alice_stake_amt, {"from": alice})
    upgraded_staking_v2.unbond(bob_stake_amt * 2 * 99 // 100, {"from": bob})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    upgraded_staking_v2.withdraw({"from": alice})
    upgraded_staking_v2.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 100 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 198 * 10 ** 18, "incorrect withdraw amount"


def test_withdraw_all(a, deployer, alice, bob, worker, alpha, staking):

    alice_stake_amt = 200 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})

    staking.unbond(alice_stake_amt, {"from": alice})

    chain.sleep(7 * 86400)

    with brownie.reverts("withdraw/too-low-total-alpha"):
        staking.withdraw({"from": alice})


def test_withdraw_all_before_upgrade(
    a, deployer, alice, bob, worker, alpha, staking, staking_v2, proxy_admin
):

    alice_stake_amt = 200 * 10 ** 18

    staking.stake(alice_stake_amt, {"from": alice})

    staking.unbond(alice_stake_amt, {"from": alice})

    chain.sleep(7 * 86400)

    proxy_admin.upgrade(staking, staking_v2)

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    chain.sleep(23 * 86400)

    with brownie.reverts("withdraw/too-low-total-alpha"):
        staking.withdraw({"from": alice})


def test_withdraw_all_after_upgrade(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2
):

    alice_stake_amt = 200 * 10 ** 18

    upgraded_staking_v2.stake(alice_stake_amt, {"from": alice})

    upgraded_staking_v2.unbond(alice_stake_amt, {"from": alice})

    chain.sleep(7 * 86400)

    with brownie.reverts("withdraw/not-valid"):
        upgraded_staking_v2.withdraw({"from": alice})

    chain.sleep(23 * 86400)

    with brownie.reverts("withdraw/too-low-total-alpha"):
        upgraded_staking_v2.withdraw({"from": alice})


# ------------------------------------------- Alpha staking v3 --------------------------------------
def test_not_gov_extract_after_upgrade_staking_v3(a, alice, upgraded_staking_v3):
    with brownie.reverts("onlyGov/not-governor"):
        upgraded_staking_v3.extract(1000, {"from": alice})


def test_worker_extract_after_upgrade_staking_v3(a, alice, worker, upgraded_staking_v3):
    assert upgraded_staking_v3.worker() == worker
    with brownie.reverts("onlyGov/not-governor"):
        upgraded_staking_v3.extract(1000, {"from": worker})


def test_not_enough_alpha_staking_v3(a, alice, bob, deployer, upgraded_staking_v3):
    alice_stake_amt = 10 ** 18
    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    with brownie.reverts("extract/too-low-total-alpha"):
        upgraded_staking_v3.extract(10 ** 18, {"from": deployer})


def test_not_enough_alpha_before_upgrade_staking_v3(
    a, alice, bob, deployer, upgraded_staking_v2, staking_v3, proxy_admin
):
    staking = upgraded_staking_v2
    alice_stake_amt = 10 ** 18
    staking.stake(alice_stake_amt, {"from": alice})
    proxy_admin.upgrade(staking, staking_v3)
    with brownie.reverts("extract/too-low-total-alpha"):
        staking.extract(10 ** 18, {"from": deployer})


def test_not_enough_alpha_after_upgrade_staking_v3(
    a, alice, bob, deployer, upgraded_staking_v3
):
    alice_stake_amt = 10 ** 18
    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    with brownie.reverts("extract/too-low-total-alpha"):
        upgraded_staking_v3.extract(10 ** 18, {"from": deployer})


def test_extract_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    prevDeployerBal = alpha.balanceOf(deployer)

    upgraded_staking_v3.extract(1000, {"from": deployer})

    curDeployerBal = alpha.balanceOf(deployer)
    assert curDeployerBal - prevDeployerBal == 1000, "incorrect extract amount"


def test_extract_before_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2, staking_v3, proxy_admin
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    staking = upgraded_staking_v2

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    prevDeployerBal = alpha.balanceOf(deployer)

    staking.extract(1000, {"from": deployer})

    proxy_admin.upgrade(staking, staking_v3)

    curDeployerBal = alpha.balanceOf(deployer)
    assert curDeployerBal - prevDeployerBal == 1000, "incorrect extract amount"


def test_extract_after_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):
    alice_stake_amt = 10 ** 18
    bob_stake_amt = 3 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    prevDeployerBal = alpha.balanceOf(deployer)

    upgraded_staking_v3.extract(1000, {"from": deployer})

    curDeployerBal = alpha.balanceOf(deployer)
    assert curDeployerBal - prevDeployerBal == 1000, "incorrect extract amount"


def test_extract_during_unbond_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    upgraded_staking_v3.unbond(alice_stake_amt / 2, {"from": alice})

    with brownie.reverts("withdraw/not-valid"):
        upgraded_staking_v3.withdraw({"from": alice})

    upgraded_staking_v3.extract(100 * 10 ** 18, {"from": deployer})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    upgraded_staking_v3.withdraw({"from": alice})
    cur_alice_balance = alpha.balanceOf(alice)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 75 * 10 ** 18, "incorrect withdraw amount"

    upgraded_staking_v3.unbond(alice_stake_amt / 2, {"from": alice})
    upgraded_staking_v3.unbond(bob_stake_amt / 2, {"from": bob})

    upgraded_staking_v3.extract(150 * 10 ** 18, {"from": deployer})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    upgraded_staking_v3.withdraw({"from": alice})
    upgraded_staking_v3.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"


def test_extract_during_unbond_before_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2, staking_v3, proxy_admin
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    staking = upgraded_staking_v2

    staking.stake(alice_stake_amt, {"from": alice})
    staking.stake(bob_stake_amt, {"from": bob})

    staking.unbond(alice_stake_amt / 2, {"from": alice})

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    staking.extract(100 * 10 ** 18, {"from": deployer})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    staking.withdraw({"from": alice})
    cur_alice_balance = alpha.balanceOf(alice)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 75 * 10 ** 18, "incorrect withdraw amount"

    # upgrade

    proxy_admin.upgrade(staking, staking_v3)

    staking.unbond(alice_stake_amt / 2, {"from": alice})
    staking.unbond(bob_stake_amt / 2, {"from": bob})

    staking.extract(150 * 10 ** 18, {"from": deployer})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    staking.withdraw({"from": alice})
    staking.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"


def test_extract_during_unbond_after_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    upgraded_staking_v3.unbond(alice_stake_amt / 2, {"from": alice})

    with brownie.reverts("withdraw/not-valid"):
        upgraded_staking_v3.withdraw({"from": alice})

    upgraded_staking_v3.extract(100 * 10 ** 18, {"from": deployer})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    upgraded_staking_v3.withdraw({"from": alice})
    cur_alice_balance = alpha.balanceOf(alice)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 75 * 10 ** 18, "incorrect withdraw amount"

    upgraded_staking_v3.unbond(alice_stake_amt / 2, {"from": alice})
    upgraded_staking_v3.unbond(bob_stake_amt / 2, {"from": bob})

    upgraded_staking_v3.extract(150 * 10 ** 18, {"from": deployer})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    upgraded_staking_v3.withdraw({"from": alice})
    upgraded_staking_v3.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 25 * 10 ** 18, "incorrect withdraw amount"


def test_staking_after_extract_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})

    upgraded_staking_v3.extract(100 * 10 ** 18, {"from": deployer})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    upgraded_staking_v3.unbond(alice_stake_amt, {"from": alice})
    upgraded_staking_v3.unbond(bob_stake_amt * 2 * 99 // 100, {"from": bob})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    upgraded_staking_v3.withdraw({"from": alice})
    upgraded_staking_v3.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 100 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 198 * 10 ** 18, "incorrect withdraw amount"


def test_staking_after_extract_before_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2, staking_v3, proxy_admin
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    staking = upgraded_staking_v2

    staking.stake(alice_stake_amt, {"from": alice})

    staking.extract(100 * 10 ** 18, {"from": deployer})
    staking.stake(bob_stake_amt, {"from": bob})

    staking.unbond(alice_stake_amt, {"from": alice})
    staking.unbond(bob_stake_amt * 2 * 99 // 100, {"from": bob})

    chain.sleep(7 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    # upgrade
    proxy_admin.upgrade(staking, staking_v3)

    # wait for next 23 d
    chain.sleep(23 * 86400)

    staking.withdraw({"from": alice})
    staking.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 100 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 198 * 10 ** 18, "incorrect withdraw amount"


def test_staking_after_extract_and_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):

    alice_stake_amt = 200 * 10 ** 18
    bob_stake_amt = 200 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})

    upgraded_staking_v3.extract(100 * 10 ** 18, {"from": deployer})
    upgraded_staking_v3.stake(bob, bob_stake_amt, {"from": bob})

    upgraded_staking_v3.unbond(alice_stake_amt, {"from": alice})
    upgraded_staking_v3.unbond(bob_stake_amt * 2 * 99 // 100, {"from": bob})

    chain.sleep(30 * 86400)

    prv_alice_balance = alpha.balanceOf(alice)
    prv_bob_balance = alpha.balanceOf(bob)

    upgraded_staking_v3.withdraw({"from": alice})
    upgraded_staking_v3.withdraw({"from": bob})

    cur_alice_balance = alpha.balanceOf(alice)
    cur_bob_balance = alpha.balanceOf(bob)

    assert (
        cur_alice_balance - prv_alice_balance
    ) == 100 * 10 ** 18, "incorrect withdraw amount"
    assert (
        cur_bob_balance - prv_bob_balance
    ) == 198 * 10 ** 18, "incorrect withdraw amount"


def test_withdraw_all_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):

    alice_stake_amt = 200 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})

    upgraded_staking_v3.unbond(alice_stake_amt, {"from": alice})

    chain.sleep(30 * 86400)

    with brownie.reverts("withdraw/too-low-total-alpha"):
        upgraded_staking_v3.withdraw({"from": alice})


def test_withdraw_all_before_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v2, staking_v3, proxy_admin
):

    alice_stake_amt = 200 * 10 ** 18
    staking = upgraded_staking_v2

    staking.stake(alice_stake_amt, {"from": alice})

    staking.unbond(alice_stake_amt, {"from": alice})

    chain.sleep(7 * 86400)

    proxy_admin.upgrade(staking, staking_v3)

    with brownie.reverts("withdraw/not-valid"):
        staking.withdraw({"from": alice})

    chain.sleep(23 * 86400)

    with brownie.reverts("withdraw/too-low-total-alpha"):
        staking.withdraw({"from": alice})


def test_withdraw_all_after_upgrade_staking_v3(
    a, deployer, alice, bob, worker, alpha, upgraded_staking_v3
):

    alice_stake_amt = 200 * 10 ** 18

    upgraded_staking_v3.stake(alice, alice_stake_amt, {"from": alice})

    upgraded_staking_v3.unbond(alice_stake_amt, {"from": alice})

    chain.sleep(7 * 86400)

    with brownie.reverts("withdraw/not-valid"):
        upgraded_staking_v3.withdraw({"from": alice})

    chain.sleep(23 * 86400)

    with brownie.reverts("withdraw/too-low-total-alpha"):
        upgraded_staking_v3.withdraw({"from": alice})
