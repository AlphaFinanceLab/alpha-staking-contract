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
  address public governor;
  address public pendingGovernor;
  uint public totalAlpha;
  uint public totalShare;
  mapping(address => Data) public users;

  modifier onlyGov() {
    require(msg.sender == governor, 'onlyGov/not-governor');
    _;
  }

  function initialize(IERC20 _alpha, address _governor) external initializer {
    alpha = _alpha;
    governor = _governor;
  }

  function setPendingGovernor(address _pendingGovernor) external onlyGov {
    pendingGovernor = _pendingGovernor;
  }

  function acceptGovernor() external {
    require(msg.sender == pendingGovernor, 'acceptGovernor/not-pending');
    pendingGovernor = address(0);
    governor = msg.sender;
  }

  function getStakeValue(address user) external view returns (uint) {
    uint share = users[user].share;
    return share == 0 ? 0 : share.mul(totalAlpha).div(totalShare);
  }

  function stake(uint amount) external nonReentrant {
    require(amount >= 1e18, 'stake/amount-too-small');
    Data storage data = users[msg.sender];
    if (data.status != STATUS_READY) {
      data.status = STATUS_READY;
      data.unbondTime = 0;
      data.unbondShare = 0;
    }
    alpha.safeTransferFrom(msg.sender, address(this), amount);
    uint share = totalAlpha == 0 ? amount : amount.mul(totalShare).div(totalAlpha);
    totalAlpha = totalAlpha.add(amount);
    totalShare = totalShare.add(share);
    data.share = data.share.add(share);
  }

  function unbond(uint share) external nonReentrant {
    Data storage data = users[msg.sender];
    if (data.status != STATUS_READY) {
      data.status = STATUS_READY;
      data.unbondTime = 0;
      data.unbondShare = 0;
    }
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
    data.status = STATUS_READY;
    data.unbondTime = 0;
    data.unbondShare = 0;
    alpha.safeTransfer(msg.sender, amount);
  }

  function reward(uint amount) external onlyGov {
    require(totalShare >= 1e18, 'reward/share-too-small');
    alpha.safeTransferFrom(msg.sender, address(this), amount);
    totalAlpha = totalAlpha.add(amount);
  }

  function skim(uint amount) external onlyGov {
    alpha.safeTransfer(msg.sender, amount);
    require(alpha.balanceOf(address(this)) >= totalAlpha, 'skim/not-enough-balance');
  }

  function extract(uint amount) external onlyGov {
    totalAlpha = totalAlpha.sub(amount);
    alpha.safeTransfer(msg.sender, amount);
    require(totalAlpha >= 1e18, 'extract/too-low-total-alpha');
  }
}
