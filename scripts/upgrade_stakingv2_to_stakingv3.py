from typing import ChainMap
from brownie import accounts, interface, chain
from brownie import (
    AlphaStakingV3,
    MockMerkleStaking,
    TransparentUpgradeableProxyImpl,
    ProxyAdminImpl,
)
from brownie.network.gas.strategies import GasNowScalingStrategy
from brownie import network
from .utils import generate_merkle

from brownie.exceptions import VirtualMachineError

network.priority_fee("1 gwei")
network.max_fee("100 gwei")


def test_upgrade(alpha, staking, staking_impl_v3, proxy_admin, deployer):
    network.gas_price(0)

    alice = accounts.at("0x2fff23939db97a2dc94c9d49d6b07fb720a4ad95", force=True)
    _, alice_staking_v2_share, _, _ = staking.users(alice)
    unbonding_duration_v2 = staking.UNBONDING_DURATION()
    withdraw_duration_v2 = staking.WITHDRAW_DURATION()
    total_share_v2 = staking.totalShare()
    total_alpha_v2 = staking.totalAlpha()

    duration_30_days = 30 * 86400
    duration_3_day = 3 * 86400
    assert (
        unbonding_duration_v2 == duration_30_days
    ), "incorrect unbonding duration of staking v3"
    assert (
        withdraw_duration_v2 == duration_3_day
    ), "incorrect withdraw duration of staking v3"

    bob = accounts.at("0x6dfe87acaa482dea05713ad559ccce862ee873b7", force=True)
    (
        bob_staking_v2_status,
        bob_staking_v2_share,
        bob_staking_v2_unbond_time,
        bob_staking_v2_unbond_share,
    ) = staking.users(bob)

    assert bob_staking_v2_status == staking.STATUS_UNBONDING(), "bob isn't unbonding"

    proxy_admin.upgrade(staking, staking_impl_v3, {"from": deployer})

    unbonding_duration_v3 = staking.UNBONDING_DURATION()
    withdraw_duration_v3 = staking.WITHDRAW_DURATION()
    total_share_v3 = staking.totalShare()
    total_alpha_v3 = staking.totalAlpha()

    duration_3_days = 3 * 86400
    duration_30_days = 30 * 86400
    assert (
        unbonding_duration_v3 == duration_30_days
    ), "incorrect unbonding duration of staking v3"
    assert (
        withdraw_duration_v3 == duration_3_days
    ), "incorrect withdraw duration of staking v3"
    assert total_alpha_v3 == total_alpha_v2, "total alpha after update isn't equal"
    assert total_share_v3 == total_share_v2, "total share after update isn't equal"

    # check alice
    _, alice_staking_v3_share, _, _ = staking.users(alice)
    assert (
        alice_staking_v3_share == alice_staking_v2_share
    ), "stake share isn't equal staking v2"

    # check bob
    (
        bob_staking_v3_status,
        bob_staking_v3_share,
        bob_staking_v3_unbond_time,
        bob_staking_v3_unbond_share,
    ) = staking.users(bob)

    assert (
        bob_staking_v3_status == bob_staking_v2_status
    ), "bob status before and after isn't equal"
    assert (
        bob_staking_v3_share == bob_staking_v2_share
    ), "bob share before and after isn't equal"
    assert (
        bob_staking_v3_unbond_time == bob_staking_v2_unbond_time
    ), "bob unbond time before and after isn't equal"
    assert (
        bob_staking_v3_unbond_share == bob_staking_v2_unbond_share
    ), "bob unbond share before and after isn't equal"

    # charlie stake after updrade contract
    charlie = accounts.at("0x326d9f47ba49bbaac279172634827483af70a601", force=True)
    charlie_stake_amount = 100 * 10 ** 18
    alpha.approve(staking, charlie_stake_amount, {"from": charlie, "gas_price": 0})
    staking.stake(charlie, charlie_stake_amount, {"from": charlie, "gas_price": 0})

    (
        charlie_after_status,
        charlie_after_share,
        charlie_after_unbond_time,
        charlie_after_unbond_share,
    ) = staking.users(charlie)
    assert (
        charlie_after_status == staking.STATUS_READY()
    ), "incorrect charlie status after stake"
    assert (
        charlie_after_share == charlie_stake_amount * total_share_v3 // total_alpha_v3
    ), "incorrect charlie share after stake"
    assert charlie_after_unbond_time == 0, "incorrect charlie unbond time after stake"
    assert charlie_after_unbond_share == 0, "incorrect charlie unbond share after stake"

    # alice unbond
    staking.unbond(alice_staking_v3_share, {"from": alice, "gas_price": 0})
    (
        alice_after_unbond_status,
        alice_after_unbond_share,
        alice_after_unbond_unbond_time,
        alice_after_unbond_unbond_share,
    ) = staking.users(alice)
    assert (
        alice_after_unbond_status == staking.STATUS_UNBONDING()
    ), "incorrect alice unbond status"
    assert (
        alice_after_unbond_share == alice_staking_v3_share
    ), "incorrect alice share after unbond"
    assert (
        alice_after_unbond_unbond_share == alice_staking_v3_share
    ), "incorrect alice unbond share"

    # bob withdraw
    start_time = chain.time()
    bob_withdraw_time = bob_staking_v3_unbond_time + unbonding_duration_v3 - start_time

    chain.sleep(bob_withdraw_time - 100)
    try:
        staking.withdraw({"from": bob, "gas_price": 0})
        assert False
    except VirtualMachineError:
        pass

    chain.sleep(100)

    bob_before = alpha.balanceOf(bob)
    total_alpha_v3 = staking.totalAlpha()
    total_share_v3 = staking.totalShare()
    staking.withdraw({"from": bob, "gas_price": 0})
    bob_after = alpha.balanceOf(bob)
    (
        bob_data_status,
        bob_data_share,
        bob_data_unbond_time,
        bob_data_unbond_share,
    ) = staking.users(bob)
    assert bob_after - bob_before, (
        bob_staking_v3_unbond_share * total_alpha_v3 // total_share_v3
    )
    assert (
        bob_data_status == staking.STATUS_READY()
    ), "incorrect bob status after withdraw"
    assert bob_data_share == 0, "incorrect bob share after withdraw"
    assert bob_data_unbond_time == 0, "incorrect bob unbond time after withdraw"
    assert bob_data_unbond_share == 0, "incorrect bob unbond share after withdraw"

    try:
        staking.withdraw({"from": alice, "gas_price": 0})
        assert False
    except VirtualMachineError:
        pass
    chain.sleep(
        alice_after_unbond_unbond_time + (30 * 86400) - bob_withdraw_time - start_time
    )

    # alice withdraw
    total_alpha_v3 = staking.totalAlpha()
    total_share_v3 = staking.totalShare()
    alice_before = alpha.balanceOf(alice)
    staking.withdraw({"from": alice, "gas_price": 0})
    alice_after = alpha.balanceOf(alice)
    (
        alice_data_status,
        alice_data_share,
        alice_data_unbond_time,
        alice_data_unbond_share,
    ) = staking.users(alice)

    assert (
        alice_after - alice_before
        == alice_staking_v3_share * total_alpha_v3 // total_share_v3
    )
    assert (
        alice_data_status == staking.STATUS_READY()
    ), "incorrect alice status after withdraw"
    assert alice_data_share == 0, "incorrect alice share after withdraw"
    assert alice_data_unbond_time == 0, "incorrect alice unbond time after withdraw"
    assert alice_data_unbond_share == 0, "incorrect alice unbond share after withdraw"

    # set merkle
    eve = accounts.at("0xb597B202294Dd5a4A616FCc2F178588BFc6D2c16", force=True)

    merkle = MockMerkleStaking.deploy(alpha, staking, "", {"from": deployer})
    alpha.approve(staking, 2 ** 256 - 1, {"from": merkle, "gas_price": 0})
    merkle.updateStaking(staking, {"from": deployer})

    # set merkle to staking
    staking.setMerkle(merkle, {"from": deployer})

    rewards = {
        alice.address: 10 * 10 ** 18,
        eve.address: 90 * 10 ** 18,
    }
    root, proof = generate_merkle(list(rewards.keys()), list(rewards.values()))
    merkle.updateMerkleRoot(root, {"from": deployer})
    alpha.transfer(merkle, sum(rewards.values()), {"from": deployer})

    # try to claim eve reward by bob, this should be revert
    alpha.approve(staking, rewards[eve.address], {"from": bob, "gas_price": 0})
    try:
        merkle.claimAndStake(
            rewards[eve.address], proof[1], {"from": bob, "gas_price": 0}
        )
        assert False
    except VirtualMachineError:
        pass

    alpha.approve(staking, rewards[eve.address], {"from": eve, "gas_price": 0})
    merkle.claimAndStake(rewards[eve.address], proof[1], {"from": eve, "gas_price": 0})

    total_alpha_v3 = staking.totalAlpha()
    total_share_v3 = staking.totalShare()

    (
        eve_staking_v3_status,
        eve_staking_v3_share,
        eve_staking_v3_unbond_time,
        eve_staking_v3_unbond_share,
    ) = staking.users(eve)

    assert (
        eve_staking_v3_status == staking.STATUS_READY()
    ), "incorrect eve status after stake"
    assert (
        eve_staking_v3_share == rewards[eve.address] * total_share_v3 // total_alpha_v3
    ), "incorrect eve share after stake"
    assert eve_staking_v3_unbond_time == 0, "incorrect eve unbond time after stake"
    assert eve_staking_v3_unbond_share == 0, "incorrect eve unbond share after stake"

    print("Test pass!!!")


def main():
    deployer = accounts.at("0xB593d82d53e2c187dc49673709a6E9f806cdC835", force=True)
    # deployer = accounts.load('gh')

    alpha = interface.IAny("0xa1faa113cbE53436Df28FF0aEe54275c13B40975")
    # TODO: Update merkle address before deploy
    merkle = ""

    proxy_admin = ProxyAdminImpl.at("0x090eCE252cEc5998Db765073D07fac77b8e60CB2")
    staking_impl_v3 = AlphaStakingV3.deploy({"from": deployer})
    staking_impl_v3.initialize(alpha, deployer, {"from": deployer})
    staking = interface.IAny("0x2aa297c3208bd98a9a477514d3c80ace570a6dee")

    # comment this function when upgrade contract
    # test_upgrade(alpha, staking, staking_impl_v3, proxy_admin, deployer)

    # upgrade
    proxy_admin.upgrade(staking, staking_impl_v3, {"from": deployer})

    staking.setMerkle(merkle, {"from": deployer})
