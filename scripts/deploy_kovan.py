from brownie import accounts, interface
from brownie import MockERC20, AlphaStaking, TransparentUpgradeableProxyImpl, ProxyAdminImpl


def main():
    deployer = accounts.at('0xCB8cF8E6f61A3a0E383A3dcd9625d7ACe7436De4', force=True)
    user = accounts.at('0x435Fd10EA3814583eE5fDDfe830330DD4d6Eb4CF', force=True)
    # deployer = accounts.load('staking-kovan')
    # user = accounts.load('kovan-tester')

    token = MockERC20.deploy('mock', 'MOCK', 18, {'from': deployer})
    proxy_admin = ProxyAdminImpl.deploy({'from': deployer})
    staking_impl = AlphaStaking.deploy({'from': deployer})
    staking = TransparentUpgradeableProxyImpl.deploy(
        staking_impl, proxy_admin, staking_impl.initialize.encode_input(token, deployer), {'from': deployer})

    staking = interface.IAny(staking)
    staking.setWorker(deployer, {'from': deployer})

    # mint tokens to deployer
    token.mint(deployer, 10**12 * 10**18, {'from': deployer})
    token.approve(staking, 2**256-1, {'from': deployer})

    staking.stake(1000 * 10**18, {'from': deployer})

    token.mint(user, 10**12 * 10**18, {'from': user})
    token.approve(staking, 2**256-1, {'from': user})

    staking.stake(10 * 10**18, {'from': user})
