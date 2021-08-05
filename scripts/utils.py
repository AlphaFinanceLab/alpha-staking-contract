from brownie import accounts, Contract, chain
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl

try:
    from brownie import interface
except:
    pass

ALPHA = "0xa1faa113cbE53436Df28FF0aEe54275c13B40975"


def almostEqual(a, b, thresh=0.01):
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def mint_tokens(token, to, interface=None, amount=None):
    if interface is None:
        interface = globals()["interface"]

    token = interface.IAny(token)
    if amount is None:
        # default is 1M tokens
        amount = 10 ** 12 * 10 ** token.decimals()

    if token == ALPHA:
        owner = token.owner()
        token.mint(amount, {"from": owner})
        token.transfer(to, amount, {"from": owner})
    else:
        raise Exception("tokens not supported")


def setup():
    deployer = accounts[0]
    alice = accounts[1]
    bob = accounts[2]
    worker = accounts[9]

    alpha = interface.IAny("0xa1faa113cbE53436Df28FF0aEe54275c13B40975")
    proxy_admin = ProxyAdminImpl.deploy({"from": deployer})
    staking_impl = AlphaStaking.deploy({"from": deployer})
    staking = TransparentUpgradeableProxyImpl.deploy(
        staking_impl,
        proxy_admin,
        staking_impl.initialize.encode_input(alpha, deployer),
        {"from": deployer},
    )
    staking = interface.IAny(staking)

    # set deployer as worker
    staking.setWorker(worker, {"from": deployer})

    # mint tokens
    mint_tokens(alpha, alice)
    mint_tokens(alpha, bob)
    mint_tokens(alpha, deployer)
    mint_tokens(alpha, worker)

    # approve
    alpha.approve(staking, 2 ** 256 - 1, {"from": alice})
    alpha.approve(staking, 2 ** 256 - 1, {"from": bob})
    alpha.approve(staking, 2 ** 256 - 1, {"from": deployer})
    alpha.approve(staking, 2 ** 256 - 1, {"from": worker})

    return deployer, alice, bob, worker, alpha, proxy_admin, staking_impl, staking
