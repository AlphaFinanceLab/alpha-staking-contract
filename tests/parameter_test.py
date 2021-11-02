from brownie import interface, Contract, accounts, chain
from brownie import AlphaStaking, ProxyAdminImpl, TransparentUpgradeableProxyImpl
import brownie


def test_unchange_parameter_after_upgrade(staking, staking_v2, proxy_admin, alice):
    prev_STATUS_READY = staking.STATUS_READY()
    prev_STATUS_UNBONDING = staking.STATUS_UNBONDING()
    prev_alpha = staking.alpha()
    prev_governor = staking.governor()
    prev_pendingGovernor = staking.pendingGovernor()
    prev_worker = staking.worker()
    prev_totalAlpha = staking.totalAlpha()
    prev_totalShare = staking.totalShare()
    prev_admin = proxy_admin.getProxyAdmin(staking)

    proxy_admin.upgrade(staking, staking_v2)

    assert prev_STATUS_READY == staking.STATUS_READY(), "STATUS_READY must be the same"
    assert (
        prev_STATUS_UNBONDING == staking.STATUS_UNBONDING()
    ), "STATUS_UNBONDING must be the same"
    assert prev_alpha == staking.alpha(), "alpha must be the same"
    assert prev_governor == staking.governor(), "governor must be the same"
    assert (
        prev_pendingGovernor == staking.pendingGovernor()
    ), "pendingGovernor must be the same"
    assert prev_worker == staking.worker(), "worker must be the same"
    assert prev_totalAlpha == staking.totalAlpha(), "totalAlpha must be the same"
    assert prev_totalShare == staking.totalShare(), "totalShare must be the same"
    assert prev_admin == proxy_admin.getProxyAdmin(
        staking
    ), "proxy admin must be the same"


def test_change_parameter_after_upgrade(staking, staking_v2, proxy_admin, alice):
    prev_UNBONDING_DURATION = staking.UNBONDING_DURATION()
    prev_WITHDRAW_DURATION = staking.WITHDRAW_DURATION()
    prev_impl = proxy_admin.getProxyImplementation(staking)

    proxy_admin.upgrade(staking, staking_v2)

    assert (
        prev_UNBONDING_DURATION != staking.UNBONDING_DURATION()
    ), "UNBONDING_DURATION must change"
    assert (
        prev_WITHDRAW_DURATION != staking.WITHDRAW_DURATION()
    ), "WITHDRAW_DURATION must change"
    assert prev_impl != proxy_admin.getProxyImplementation(staking)


# ------------------------------------------- Alpha staking v3 --------------------------------------
def test_unchange_parameter_after_upgrade_staking_v3(
    upgraded_staking_v2, staking_v3, proxy_admin, alice
):
    staking = upgraded_staking_v2
    prev_STATUS_READY = staking.STATUS_READY()
    prev_STATUS_UNBONDING = staking.STATUS_UNBONDING()
    prev_UNBONDING_DURATION = staking.UNBONDING_DURATION()
    prev_WITHDRAW_DURATION = staking.WITHDRAW_DURATION()
    prev_alpha = staking.alpha()
    prev_governor = staking.governor()
    prev_pendingGovernor = staking.pendingGovernor()
    prev_worker = staking.worker()
    prev_totalAlpha = staking.totalAlpha()
    prev_totalShare = staking.totalShare()
    prev_admin = proxy_admin.getProxyAdmin(staking)

    proxy_admin.upgrade(staking, staking_v3)

    assert prev_STATUS_READY == staking.STATUS_READY(), "STATUS_READY must be the same"
    assert (
        prev_STATUS_UNBONDING == staking.STATUS_UNBONDING()
    ), "STATUS_UNBONDING must be the same"
    assert (
        prev_UNBONDING_DURATION == staking.UNBONDING_DURATION()
    ), "UNBONDING_DURATION must be the same"
    assert (
        prev_WITHDRAW_DURATION == staking.WITHDRAW_DURATION()
    ), "WITHDRAW_DURATION must be the same"
    assert prev_alpha == staking.alpha(), "alpha must be the same"
    assert prev_governor == staking.governor(), "governor must be the same"
    assert (
        prev_pendingGovernor == staking.pendingGovernor()
    ), "pendingGovernor must be the same"
    assert prev_worker == staking.worker(), "worker must be the same"
    assert prev_totalAlpha == staking.totalAlpha(), "totalAlpha must be the same"
    assert prev_totalShare == staking.totalShare(), "totalShare must be the same"
    assert prev_admin == proxy_admin.getProxyAdmin(
        staking
    ), "proxy admin must be the same"
