from brownie import accounts, interface
from brownie import (
    AlphaStaking,
    AlphaStakingV2,
    TransparentUpgradeableProxyImpl,
    ProxyAdminImpl,
)
from brownie.network.gas.strategies import GasNowScalingStrategy
from brownie import network


gas_strategy = GasNowScalingStrategy(
    initial_speed="fast", max_speed="fast", increment=1.085, block_duration=20
)

network.gas_price(gas_strategy)


def main():
    deployer = accounts.at("0xB593d82d53e2c187dc49673709a6E9f806cdC835", force=True)
    # deployer = accounts.load('gh')

    alpha = interface.IAny("0xa1faa113cbE53436Df28FF0aEe54275c13B40975")

    proxy_admin = ProxyAdminImpl.at("0x090eCE252cEc5998Db765073D07fac77b8e60CB2")
    staking_impl_v2 = AlphaStakingV2.deploy({"from": deployer})
    staking_impl_v2.initialize(alpha, deployer)
    staking = TransparentUpgradeableProxyImpl.at(
        "0x2aa297c3208bd98a9a477514d3c80ace570a6dee"
    )

    staking = interface.IAny(staking)

    proxy_admin.upgrade(staking, staking_impl_v2, {"from": deployer})

    # approve staking contract
    stake_amt = 10 * 10 ** 18
    alpha.approve(staking, stake_amt, {"from": deployer})

    # stake 10 ALPHA
    staking.stake(stake_amt, {"from": deployer})
