from typing import ChainMap
from brownie import accounts, interface, chain
from brownie import (
    AlphaStaking,
    AlphaStakingV2,
    TransparentUpgradeableProxyImpl,
    ProxyAdminImpl,
)
from brownie.network.gas.strategies import GasNowScalingStrategy
from brownie import network

from brownie.exceptions import VirtualMachineError


gas_strategy = GasNowScalingStrategy(
    initial_speed="fast", max_speed="fast", increment=1.085, block_duration=20
)

network.gas_price(gas_strategy)


def test_upgrade(alpha, staking, staking_impl_v2, proxy_admin, deployer):
    network.gas_price(0)

    alice = accounts.at("0x41355e7c162aC92f364acfDaA3A630B3ae87A556", force=True)
    _, alice_staking_v1_share, _, _ = staking.users(alice)
    unbonding_duration_v1 = staking.UNBONDING_DURATION()
    withdraw_duration_v1 = staking.WITHDRAW_DURATION()
    total_share_v1 = staking.totalShare()
    total_alpha_v1 = staking.totalAlpha()

    duration_7_days = 7 * 86400
    duration_1_day = 86400
    assert (
        unbonding_duration_v1 == duration_7_days
    ), "incorrect unbonding duration of staking v1"
    assert (
        withdraw_duration_v1 == duration_1_day
    ), "incorrect withdraw duration of staking v1"

    bob = accounts.at("0x2D4D60ea43784B5287Bce6BddEb23a93722E3C41", force=True)
    (
        bob_staking_v1_status,
        bob_staking_v1_share,
        bob_staking_v1_unbond_time,
        bob_staking_v1_unbond_share,
    ) = staking.users(bob)

    assert bob_staking_v1_status == staking.STATUS_UNBONDING(), "bob isn't unbonding"

    proxy_admin.upgrade(staking, staking_impl_v2, {"from": deployer})

    unbonding_duration_v2 = staking.UNBONDING_DURATION()
    withdraw_duration_v2 = staking.WITHDRAW_DURATION()
    total_share_v2 = staking.totalShare()
    total_alpha_v2 = staking.totalAlpha()

    duration_3_days = 3 * 86400
    duration_30_days = 30 * 86400
    assert (
        unbonding_duration_v2 == duration_30_days
    ), "incorrect unbonding duration of staking v2"
    assert (
        withdraw_duration_v2 == duration_3_days
    ), "incorrect withdraw duration of staking v2"
    assert total_alpha_v2 == total_alpha_v1, "total alpha after update isn't equal"
    assert total_share_v2 == total_share_v1, "total share after update isn't equal"

    # check alice
    _, alice_staking_v2_share, _, _ = staking.users(alice)
    assert (
        alice_staking_v2_share == alice_staking_v1_share
    ), "stake share isn't equal staking v1"

    # check bob
    (
        bob_staking_v2_status,
        bob_staking_v2_share,
        bob_staking_v2_unbond_time,
        bob_staking_v2_unbond_share,
    ) = staking.users(bob)

    assert (
        bob_staking_v2_status == bob_staking_v1_status
    ), "bob status before and after isn't equal"
    assert (
        bob_staking_v2_share == bob_staking_v1_share
    ), "bob share before and after isn't equal"
    assert (
        bob_staking_v2_unbond_time == bob_staking_v1_unbond_time
    ), "bob unbond time before and after isn't equal"
    assert (
        bob_staking_v2_unbond_share == bob_staking_v1_unbond_share
    ), "bob unbond share before and after isn't equal"

    # charlie stake after updrade contract
    charlie = accounts.at("0x326d9f47ba49bbaac279172634827483af70a601", force=True)
    charlie_stake_amount = 100 * 10 ** 18
    alpha.approve(staking, charlie_stake_amount, {"from": charlie, "gas_price": 0})
    staking.stake(charlie_stake_amount, {"from": charlie, "gas_price": 0})

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
        charlie_after_share == charlie_stake_amount * total_share_v2 // total_alpha_v2
    ), "incorrect charlie share after stake"
    assert charlie_after_unbond_time == 0, "incorrect charlie unbond time after stake"
    assert charlie_after_unbond_share == 0, "incorrect charlie unbond share after stake"

    # alice unbond
    staking.unbond(alice_staking_v2_share, {"from": alice, "gas_price": 0})
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
        alice_after_unbond_share == alice_staking_v2_share
    ), "incorrect alice share after unbond"
    assert (
        alice_after_unbond_unbond_share == alice_staking_v2_share
    ), "incorrect alice unbond share"

    # bob withdraw
    start_time = chain.time()
    bob_withdraw_time = bob_staking_v2_unbond_time + unbonding_duration_v2 - start_time

    chain.sleep(bob_withdraw_time - 100)
    try:
        staking.withdraw({"from": bob, "gas_price": 0})
        assert False
    except VirtualMachineError:
        pass

    chain.sleep(100)

    bob_before = alpha.balanceOf(bob)
    total_alpha_v2 = staking.totalAlpha()
    total_share_v2 = staking.totalShare()
    staking.withdraw({"from": bob, "gas_price": 0})
    bob_after = alpha.balanceOf(bob)
    (
        bob_data_status,
        bob_data_share,
        bob_data_unbond_time,
        bob_data_unbond_share,
    ) = staking.users(bob)
    assert bob_after - bob_before, (
        bob_staking_v2_unbond_share * total_alpha_v2 // total_share_v2
    )
    assert (
        bob_data_status == staking.STATUS_READY()
    ), "incorrect bob status after withdraw"
    assert bob_data_share == 0, "incorrect bob share after withdraw"
    assert bob_data_unbond_time == 0, "incorrect bob unbond time after withdraw"
    assert bob_data_unbond_share == 0, "incorrect bob unbond share after withdraw"

    try:
        staking.withdraw({"from": alice})
        assert False
    except VirtualMachineError:
        pass
    chain.sleep(
        alice_after_unbond_unbond_time + (30 * 86400) - bob_withdraw_time - start_time
    )

    # alice withdraw
    total_alpha_v2 = staking.totalAlpha()
    total_share_v2 = staking.totalShare()
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
        == alice_staking_v2_share * total_alpha_v2 // total_share_v2
    )
    assert (
        alice_data_status == staking.STATUS_READY()
    ), "incorrect alice status after withdraw"
    assert alice_data_share == 0, "incorrect alice share after withdraw"
    assert alice_data_unbond_time == 0, "incorrect alice unbond time after withdraw"
    assert alice_data_unbond_share == 0, "incorrect alice unbond share after withdraw"


def main():
    deployer = accounts.at("0xB593d82d53e2c187dc49673709a6E9f806cdC835", force=True)
    # deployer = accounts.load('gh')

    alpha = interface.IAny("0xa1faa113cbE53436Df28FF0aEe54275c13B40975")

    proxy_admin = ProxyAdminImpl.at("0x090eCE252cEc5998Db765073D07fac77b8e60CB2")
    staking_impl_v2 = AlphaStakingV2.deploy({"from": deployer})
    staking_impl_v2.initialize(alpha, deployer, {"from": deployer})
    staking = interface.IAny("0x2aa297c3208bd98a9a477514d3c80ace570a6dee")

    # comment this function when upgrade contract
    # test_upgrade(alpha, staking, staking_impl_v2, proxy_admin, deployer)

    # upgrade
    proxy_admin.upgrade(staking, staking_impl_v2, {"from": deployer})
