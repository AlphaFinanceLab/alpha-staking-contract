import pytest
from brownie import interface
from utils import *


@pytest.fixture(scope="function")
def deployer(a):
    return a[0]


@pytest.fixture(scope="function")
def alice(a):
    return a[1]


@pytest.fixture(scope="function")
def bob(a):
    return a[2]


@pytest.fixture(scope="function")
def worker(a):
    return a[9]


@pytest.fixture(scope="function")
def alpha(a, MockERC20):
    return MockERC20.deploy("ALPHA", "ALPHA", 18, {"from": a[0]})


@pytest.fixture(scope="function")
def proxy_admin(a, deployer, ProxyAdminImpl):
    return ProxyAdminImpl.deploy({"from": deployer})


@pytest.fixture(scope="function")
def merkle(deployer, alpha, staking, MockMerkleStaking):
    return MockMerkleStaking.deploy(alpha, staking, "", {"from": deployer})


@pytest.fixture(scope="function")
def staking(
    a,
    alpha,
    deployer,
    alice,
    bob,
    worker,
    proxy_admin,
    AlphaStaking,
    TransparentUpgradeableProxyImpl,
):
    staking_impl = AlphaStaking.deploy({"from": deployer})
    contract = TransparentUpgradeableProxyImpl.deploy(
        staking_impl,
        proxy_admin,
        staking_impl.initialize.encode_input(alpha, deployer),
        {"from": deployer},
    )
    contract = interface.IAny(contract)
    contract.setWorker(worker, {"from": deployer})

    alpha.mint(alice, 10 ** 30)
    alpha.mint(bob, 10 ** 30)
    alpha.mint(deployer, 10 ** 30)
    alpha.mint(worker, 10 ** 30)

    alpha.approve(contract, 2 ** 256 - 1, {"from": alice})
    alpha.approve(contract, 2 ** 256 - 1, {"from": bob})
    alpha.approve(contract, 2 ** 256 - 1, {"from": deployer})
    alpha.approve(contract, 2 ** 256 - 1, {"from": worker})

    return contract


@pytest.fixture(scope="function")
def staking_v2(deployer, AlphaStakingV2):
    staking_impl_v2 = AlphaStakingV2.deploy({"from": deployer})
    return staking_impl_v2


@pytest.fixture(scope="function")
def staking_v3(deployer, AlphaStakingV3):
    staking_impl_v3 = AlphaStakingV3.deploy({"from": deployer})
    return staking_impl_v3


@pytest.fixture(scope="function")
def upgraded_staking_v2(deployer, staking, proxy_admin, AlphaStakingV2):
    staking_impl_v2 = AlphaStakingV2.deploy({"from": deployer})
    proxy_admin.upgrade(staking, staking_impl_v2)
    return staking


@pytest.fixture(scope="function")
def upgraded_staking_v3(
    deployer, alpha, merkle, upgraded_staking_v2, proxy_admin, AlphaStakingV3
):
    staking = upgraded_staking_v2
    staking_impl_v3 = AlphaStakingV3.deploy({"from": deployer})
    proxy_admin.upgrade(staking, staking_impl_v3)
    staking.setMerkle(merkle, {"from": deployer})

    # setup merkle
    alpha.mint(merkle, 1000 * 10 ** 18, {"from": deployer})
    alpha.approve(staking, 2 ** 256 - 1, {"from": merkle})
    merkle.updateStaking(staking, {"from": deployer})
    return staking


@pytest.fixture(scope="function")
def pure_staking(
    a,
    alpha,
    deployer,
    alice,
    bob,
    worker,
    proxy_admin,
    AlphaStaking,
    TransparentUpgradeableProxyImpl,
):
    """
    Staking contract without side-effect eg. setWorker, mint_tokens, approve
    """
    staking_impl = AlphaStaking.deploy({"from": deployer})
    contract = TransparentUpgradeableProxyImpl.deploy(
        staking_impl,
        proxy_admin,
        staking_impl.initialize.encode_input(alpha, deployer),
        {"from": deployer},
    )
    contract = interface.IAny(contract)
    return contract
