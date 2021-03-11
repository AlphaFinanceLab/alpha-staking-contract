import pytest
from brownie import interface
from utils import *

@pytest.fixture(scope='function')
def deployer(a):
    return a[0]

@pytest.fixture(scope='function')
def alice(a):
    return a[1]

@pytest.fixture(scope='function')
def bob(a):
    return a[2]

@pytest.fixture(scope='function')
def worker(a):
    return a[9]

@pytest.fixture(scope='function')
def alpha(a, MockERC20):
    return MockERC20.deploy('ALPHA', 'ALPHA', 18, {'from': a[0]})

@pytest.fixture(scope='function')
def proxy_admin(a, deployer, ProxyAdminImpl):
    return ProxyAdminImpl.deploy({'from': deployer})

@pytest.fixture(scope='function')
def staking(a, alpha, deployer, alice, bob, worker, proxy_admin, AlphaStaking, TransparentUpgradeableProxyImpl):
    staking_impl = AlphaStaking.deploy({'from': deployer})
    contract = TransparentUpgradeableProxyImpl.deploy(
        staking_impl, proxy_admin, staking_impl.initialize.encode_input(alpha, deployer), {'from': deployer})
    contract = interface.IAny(contract)
    contract.setWorker(worker, {'from': deployer})

    alpha.mint(alice, 10**30)
    alpha.mint(bob, 10**30)
    alpha.mint(deployer, 10**30)
    alpha.mint(worker, 10**30)

    alpha.approve(contract, 2**256-1, {'from': alice})
    alpha.approve(contract, 2**256-1, {'from': bob})
    alpha.approve(contract, 2**256-1, {'from': deployer})
    alpha.approve(contract, 2**256-1, {'from': worker})

    return contract

@pytest.fixture(scope='function')
def pure_staking(a, alpha, deployer, alice, bob, worker, proxy_admin, AlphaStaking, TransparentUpgradeableProxyImpl):
    '''
    Staking contract without side-effect eg. setWorker, mint_tokens, approve
    '''
    staking_impl = AlphaStaking.deploy({'from': deployer})
    contract = TransparentUpgradeableProxyImpl.deploy(
        staking_impl, proxy_admin, staking_impl.initialize.encode_input(alpha, deployer), {'from': deployer})
    contract = interface.IAny(contract)
    return contract

