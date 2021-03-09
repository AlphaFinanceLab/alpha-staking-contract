from brownie import interface, Contract, accounts
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
import brownie
from brownie.exceptions import VirtualMachineError
from .utils import *


def main():
    deployer = accounts[0]
    alice = accounts[1]
    bob = accounts[2]

    alpha = interface.IAny('0xa1faa113cbE53436Df28FF0aEe54275c13B40975')
    proxy_admin = ProxyAdminImpl.deploy({'from': deployer})
    staking_impl = AlphaStaking.deploy({'from': deployer})
    staking = TransparentUpgradeableProxyImpl.deploy(
        staking_impl, proxy_admin, staking_impl.initialize.encode_input(alpha, deployer), {'from': deployer})
    staking = interface.IAny(staking)

    # mint tokens
    mint_tokens(alpha, alice)
    mint_tokens(alpha, bob)
    mint_tokens(alpha, deployer)

    # approve
    alpha.approve(staking, 2**256-1, {'from': alice})
    alpha.approve(staking, 2**256-1, {'from': bob})
    alpha.approve(staking, 2**256-1, {'from': deployer})

    ####################################################################################
    print('===============================================')
    print('1. set worker & reward')

    assert staking.worker() == '0x0000000000000000000000000000000000000000', 'worker should initially be 0'

    staking.setWorker(alice, {'from': deployer})

    assert staking.worker() == alice, 'incorrect worker'

    staking.setWorker(bob, {'from': deployer})

    assert staking.worker() == bob, 'incorrect worker'

    staking.stake(10**18, {'from': alice})

    try:
        staking.reward(0, {'from': alice})
        assert False
    except VirtualMachineError:
        pass

    try:
        staking.reward(10**18, {'from': alice})
        assert False
    except VirtualMachineError:
        pass

    staking.reward(0, {'from': deployer})
    staking.reward(0, {'from': bob})
    staking.reward(10**18, {'from': deployer})
    staking.reward(10**18, {'from': bob})
