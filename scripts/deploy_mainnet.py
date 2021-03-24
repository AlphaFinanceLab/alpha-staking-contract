from brownie import accounts, interface
from brownie import AlphaStaking, TransparentUpgradeableProxyImpl, ProxyAdminImpl
from brownie.network.gas.strategies import GasNowScalingStrategy

gas_strategy = GasNowScalingStrategy(
    initial_speed="slow", max_speed="fast", increment=1.085, block_duration=20)


def main():
    deployer = accounts.at('0xB593d82d53e2c187dc49673709a6E9f806cdC835', force=True)
    # deployer = accounts.load('gh')

    alpha = interface.IAny('0xa1faa113cbE53436Df28FF0aEe54275c13B40975')

    proxy_admin = ProxyAdminImpl.deploy({'from': deployer, 'gas_price': gas_strategy})
    staking_impl = AlphaStaking.deploy({'from': deployer, 'gas_price': gas_strategy})
    staking = TransparentUpgradeableProxyImpl.deploy(
        staking_impl, proxy_admin, staking_impl.initialize.encode_input(alpha, deployer), {'from': deployer, 'gas_price': gas_strategy})

    staking = interface.IAny(staking)

    # approve staking contract
    alpha.approve(staking, 2**256-1, {'from': deployer, 'gas_price': gas_strategy})

    # stake 10 ALPHA
    staking.stake(10 * 10**18, {'from': deployer, 'gas_price': gas_strategy})
