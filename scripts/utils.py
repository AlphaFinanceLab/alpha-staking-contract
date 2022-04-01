from web3 import Web3
from brownie import accounts, Contract, chain
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
from ape_safe import ApeSafe

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
        amount = 10**12 * 10 ** token.decimals()

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
    alpha.approve(staking, 2**256 - 1, {"from": alice})
    alpha.approve(staking, 2**256 - 1, {"from": bob})
    alpha.approve(staking, 2**256 - 1, {"from": deployer})
    alpha.approve(staking, 2**256 - 1, {"from": worker})

    return deployer, alice, bob, worker, alpha, proxy_admin, staking_impl, staking


def generate_merkle(accounts, rewards):
    if len(accounts) != len(rewards):
        raise Exception("length is not equal")
    leaves = [
        Web3.solidityKeccak(["address", "uint256"], [account, reward])
        for account, reward in zip(accounts, rewards)
    ]
    hashes = leaves
    proofs = []
    for _ in accounts:
        proofs.append([])

    _round = 0
    while len(hashes) > 1:
        _res = []
        for i in range(0, len(hashes), 2):
            if i == len(hashes) - 1:
                _res.append(hashes[i])
                continue

            node1 = hashes[i]
            node2 = hashes[i + 1]
            if node1 > node2:
                node1, node2 = node2, node1
            _res.append(Web3.solidityKeccak(["bytes32", "bytes32"], [node1, node2]))

            for j in range(1 << _round):
                proofs[i * (1 << _round) + j].append(hashes[i + 1])
                if (i + 1) * (1 << _round) + j < len(leaves):
                    proofs[(i + 1) * (1 << _round) + j].append(hashes[i])

        hashes = _res
        _round += 1

    root = hashes[0]
    return root, proofs


def yes_no_question(message="?", default=False) -> bool:
    """Ask user about yes/no question.

    Argument
    ---------
        message: promt message for showing a question to user.
        default: default answer if user just enter, default is True.

    Return
    ---------
        user's answer: boolean
    """

    answer = "invalid_answer"
    valid_answer = {"yes": True, "y": True, "n": False, "no": False, "": default}
    default_flag_msg = " [Y/n]" if default else " [y/N]"

    while answer not in valid_answer:
        answer = input(message + default_flag_msg).lower()
    return valid_answer[answer]


class AlphaMainnetContracts:
    def __init__(self):
        self.dev_safe = ApeSafe("0x6be987c6d72e25F02f6f061F94417d83a6Aa13fC")  # FIXME:
        self.exec_safe = ApeSafe("0x914C687FFdAB6E1B47a327E7E4C10e4a058e009d")  # FIXME:

    def add(self, name, address):
        setattr(self, name, address)


def get_alpha_contracts():
    return AlphaMainnetContracts()
