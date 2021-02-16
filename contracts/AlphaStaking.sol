pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC20/IERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC20/SafeERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/utils/ReentrancyGuard.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/math/SafeMath.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/proxy/Initializable.sol';

contract AlphaStaking is Initializable, ReentrancyGuard {
  using SafeERC20 for IERC20;
  using SafeMath for uint;

  uint public constant STATUS_READY = 0;
  uint public constant STATUS_UNBONDING = 1;
  uint public constant UNBONDING_DURATION = 7 days;
  uint public constant WITHDRAW_DURATION = 1 days;

  struct Data {
    uint status;
    uint share;
    uint unbondTime;
    uint unbondShare;
  }

  IERC20 public alpha;
  uint public totalAlpha;
  uint public totalShare;
  mapping(address => Data) public users;

  function initialize(IERC20 _alpha) external initializer {
    alpha = _alpha;
  }

  function stake(uint amount) external nonReentrant {
    require(amount >= 1e18, 'stake/amount-too-small');
    Data storage data = users[msg.sender];
    require(data.status == STATUS_READY, 'stake/not-ready');
    alpha.safeTransferFrom(msg.sender, address(this), amount);
    uint share = totalAlpha == 0 ? amount : amount.mul(totalShare).div(totalAlpha);
    totalAlpha = totalAlpha.add(amount);
    totalShare = totalShare.add(share);
    data.share = data.share.add(share);
  }

  function unbond(uint share) external nonReentrant {
    Data storage data = users[msg.sender];
    require(data.status == STATUS_READY, 'unbond/not-ready');
    require(share <= data.share, 'unbond/insufficient-share');
    data.status = STATUS_UNBONDING;
    data.unbondTime = block.timestamp;
    data.unbondShare = share;
  }

  function withdraw() external nonReentrant {
    Data storage data = users[msg.sender];
    require(data.status == STATUS_UNBONDING, 'withdraw/not-unbonding');
    require(block.timestamp >= data.unbondTime + UNBONDING_DURATION, 'withdraw/not-valid');
    require(
      block.timestamp < data.unbondTime + UNBONDING_DURATION + WITHDRAW_DURATION,
      'withdraw/already-expired'
    );
    uint share = data.unbondShare;
    uint amount = totalAlpha.mul(share).div(totalShare);
    totalAlpha = totalAlpha.sub(amount);
    totalShare = totalShare.sub(share);
    data.share = data.share.sub(share);
    data.status = STAUS_READY;
    data.unbondTime = 0;
    data.unbondShare = 0;
    alpha.safeTransfer(msg.sender, amount);
  }

  function reset() external nonReentrant {
    Data storage data = users[msg.sender];
    require(data.status == STATUS_UNBONDING, 'reset/not-unbonding');
    data.status = STATUS_READY;
    data.unbondTime = 0;
    data.unbondShare = 0;
  }
}
