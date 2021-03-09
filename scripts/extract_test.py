from brownie import interface, Contract, accounts
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
from brownie.exceptions import VirtualMachineError
from .utils import *


def main():
    deployer, alice, bob, worker, alpha, proxy_admin, staking_impl, staking = setup()

    alice_stake_amt = 10**18
    bob_stake_amt = 3 * 10**18

    # setup stake
    staking.stake(alice_stake_amt, {'from': alice})
    staking.stake(bob_stake_amt, {'from': bob})

    ####################################################################################
    print('===============================================')
    print('1. extract alpha')

    prevDeployerBal = alpha.balanceOf(deployer)

    staking.extract(1000, {'from': deployer})

    curDeployerBal = alpha.balanceOf(deployer)

    assert curDeployerBal - prevDeployerBal == 1000, 'incorrect extract amount'

    ####################################################################################
    print('===============================================')
    print('2. unauth extract')

    try:
        staking.extract(1000, {'from': alice})
        assert False
    except VirtualMachineError:
        pass
