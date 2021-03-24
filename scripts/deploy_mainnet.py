from brownie import accounts, interface
from brownie import AlphaStaking, TransparentUpgradeableProxyImpl, ProxyAdminImpl
from brownie.network.gas.strategies import GasNowScalingStrategy

gas_strategy = GasNowScalingStrategy(
    initial_speed="slow", max_speed="fast", increment=1.085, block_duration=20)


def main():
    deployer = accounts.at('0xB593d82d53e2c187dc49673709a6E9f806cdC835', force=True)
    # deployer = accounts.load('gh')

    alpha = interface.IAny('0xa1faa113cbE53436Df28FF0aEe54275c13B40975')

    proxy_admin = ProxyAdminImpl.at('0x090eCE252cEc5998Db765073D07fac77b8e60CB2')
    staking_impl = AlphaStaking.deploy({'from': deployer, 'gas_price': gas_strategy})
    staking = TransparentUpgradeableProxyImpl.deploy(
        staking_impl, proxy_admin, staking_impl.initialize.encode_input(alpha, deployer), {'from': deployer, 'gas_price': gas_strategy})

    staking = interface.IAny(staking)

    # approve staking contract
    stake_amt = 10 * 10**18
    alpha.approve(staking, stake_amt, {'from': deployer, 'gas_price': gas_strategy})

    # stake 10 ALPHA
    staking.stake(stake_amt, {'from': deployer, 'gas_price': gas_strategy})
