import brownie
from brownie.exceptions import VirtualMachineError
from utils import *

def test_worker(deployer, alice, bob, pure_staking, alpha):
    staking = pure_staking

    mint_tokens(alpha, alice)
    mint_tokens(alpha, bob)
    mint_tokens(alpha, deployer)

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

    with brownie.reverts('onlyWorker/not-worker'):
        staking.reward(0, {'from': alice})

    with brownie.reverts('onlyWorker/not-worker'):
        staking.reward(10**18, {'from': alice})

    staking.reward(0, {'from': deployer})
    staking.reward(0, {'from': bob})
    staking.reward(10**18, {'from': deployer})
    staking.reward(10**18, {'from': bob})
