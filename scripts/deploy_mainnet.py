from brownie import accounts, interface
from brownie import AlphaStaking, TransparentUpgradeableProxyImpl, ProxyAdminImpl
from brownie.network.gas.strategies import GasNowScalingStrategy
from brownie import network


gas_strategy = GasNowScalingStrategy(
    initial_speed="slow", max_speed="fast", increment=1.085, block_duration=20)


def main():
    deployer = accounts.at('0xB593d82d53e2c187dc49673709a6E9f806cdC835', force=True)
    # deployer = accounts.load('gh')

    alpha = '0xa1faa113cbe53436df28ff0aee54275c13b40975'
    worker = deployer

    proxy_admin = ProxyAdminImpl.deploy({'from': deployer, 'gas_price': gas_strategy})
    staking_impl = AlphaStaking.deploy({'from': deployer, 'gas_price': gas_strategy})
    staking = TransparentUpgradeableProxyImpl.deploy(
        staking_impl, proxy_admin, staking_impl.initialize.encode_input(alpha, deployer), {'from': deployer, 'gas_price': gas_strategy})

    staking = interface.IAny(staking)

    # set worker
    staking.setWorker(worker, {'from': deployer, 'gas_price': gas_strategy})

    # stake 10 alpha
    interface.IAny(alpha).approve(staking, 2**256-1, {'from': deployer, 'gas_price': gas_strategy})
    staking.stake(10 * 10**18, {'from': deployer, 'gas_price': gas_strategy})
