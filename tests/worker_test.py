import brownie
from brownie.exceptions import VirtualMachineError
from utils import *


def test_reward(a, deployer, alice, bob, staking):
    staking.setWorker(bob, {"from": deployer})

    with brownie.reverts("reward/share-too-small"):
        staking.reward(0, {"from": deployer})

    with brownie.reverts("reward/share-too-small"):
        staking.reward(0, {"from": bob})

    staking.stake(10 ** 18, {"from": alice})

    with brownie.reverts("onlyWorker/not-worker"):
        staking.reward(0, {"from": alice})

    with brownie.reverts("onlyWorker/not-worker"):
        staking.reward(10 ** 18, {"from": alice})

    staking.reward(0, {"from": deployer})
    staking.reward(0, {"from": bob})
    staking.reward(10 ** 18, {"from": deployer})
    staking.reward(10 ** 18, {"from": bob})


def test_reward_after_upgrade(a, deployer, alice, bob, upgraded_staking_v2):
    upgraded_staking_v2.setWorker(bob, {"from": deployer})

    with brownie.reverts("reward/share-too-small"):
        upgraded_staking_v2.reward(0, {"from": deployer})

    with brownie.reverts("reward/share-too-small"):
        upgraded_staking_v2.reward(0, {"from": bob})

    upgraded_staking_v2.stake(10 ** 18, {"from": alice})

    with brownie.reverts("onlyWorker/not-worker"):
        upgraded_staking_v2.reward(0, {"from": alice})

    with brownie.reverts("onlyWorker/not-worker"):
        upgraded_staking_v2.reward(10 ** 18, {"from": alice})

    upgraded_staking_v2.reward(0, {"from": deployer})
    upgraded_staking_v2.reward(0, {"from": bob})
    upgraded_staking_v2.reward(10 ** 18, {"from": deployer})
    upgraded_staking_v2.reward(10 ** 18, {"from": bob})


def test_set_worker(deployer, alice, bob, pure_staking, alpha):
    staking = pure_staking
    assert (
        staking.worker() == "0x0000000000000000000000000000000000000000"
    ), "worker should initially be 0"

    staking.setWorker(alice, {"from": deployer})
    assert staking.worker() == alice, "incorrect worker"

    staking.setWorker(bob, {"from": deployer})
    assert staking.worker() == bob, "incorrect worker"

    with brownie.reverts("onlyGov/not-governor"):
        staking.setWorker(alice, {"from": bob})


def test_set_worker_after_upgraded(
    deployer, alice, bob, pure_staking, alpha, staking_v2, proxy_admin
):
    staking = pure_staking
    proxy_admin.upgrade(staking, staking_v2)
    assert (
        staking.worker() == "0x0000000000000000000000000000000000000000"
    ), "worker should initially be 0"

    staking.setWorker(alice, {"from": deployer})
    assert staking.worker() == alice, "incorrect worker"

    staking.setWorker(bob, {"from": deployer})
    assert staking.worker() == bob, "incorrect worker"

    with brownie.reverts("onlyGov/not-governor"):
        staking.setWorker(alice, {"from": bob})
