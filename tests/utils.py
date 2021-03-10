from brownie import accounts, Contract, chain
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
try:
    from brownie import interface
except:
    pass

ALPHA = '0xa1faa113cbE53436Df28FF0aEe54275c13B40975'


def almostEqual(a, b, thresh=0.01):
    return a <= b + thresh * abs(b) and a >= b - thresh * abs(b)


def mint_tokens(token, to, interface=None, amount=None):
    if interface is None:
        interface = globals()['interface']

    token = interface.IAny(token)
    if amount is None:
        # default is 1M tokens
        amount = 10**12 * 10**token.decimals()

    if token == ALPHA:
        owner = token.owner()
        token.mint(amount, {'from': owner})
        token.transfer(to, amount, {'from': owner})
    else:
        raise Exception('tokens not supported')
