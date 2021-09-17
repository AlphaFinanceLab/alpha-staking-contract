// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC20/IERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC20/SafeERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/utils/ReentrancyGuard.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/cryptography/MerkleProof.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/math/SafeMath.sol';
import '../../interfaces/IMerkleStaking.sol';
import '../../interfaces/IAlphaStaking.sol';

contract MockMerkleStaking is IMerkleStaking, Ownable, ReentrancyGuard {
  using SafeERC20 for IERC20;
  using SafeMath for uint;

  bytes32 public root;
  address public immutable token;
  mapping(address => uint) public override claimed;
  IAlphaStaking public staking;

  event UpdateRoot(bytes32 indexed root);
  event UpdateStaking(address staking);
  event Deposit(uint amount);
  event Withdraw(uint amount);
  event ClaimAndStake(address indexed account, uint claimAmount, uint sAlphaShare);

  constructor(
    address _token,
    address _staking,
    bytes32 _root
  ) public {
    token = _token;
    _updateMerkleRoot(_root);
    _updateStaking(_staking);
  }

  function updateMerkleRoot(bytes32 _root) external override onlyOwner {
    _updateMerkleRoot(_root);
  }

  function _updateMerkleRoot(bytes32 _root) internal {
    root = _root;
    emit UpdateRoot(_root);
  }

  function updateStaking(address _staking) external onlyOwner {
    _updateStaking(_staking);
  }

  function _updateStaking(address _staking) internal {
    staking = IAlphaStaking(_staking);
    emit UpdateStaking(_staking);
  }

  function deposit(uint _amount) external override onlyOwner {
    IERC20(token).safeTransferFrom(msg.sender, address(this), _amount);
    emit Deposit(_amount);
  }

  function withdraw(uint _amount) external override onlyOwner {
    IERC20(token).safeTransfer(msg.sender, _amount);
    emit Withdraw(_amount);
  }

  function claimAndStake(uint _reward, bytes32[] calldata _proof) external override nonReentrant {
    bytes32 leaf = keccak256(abi.encodePacked(msg.sender, _reward));
    require(MerkleProof.verify(_proof, root, leaf), 'claim-and-stake: invalid proof');
    uint claimAmount = _reward.sub(claimed[msg.sender]);

    require(claimAmount > 0, "claim-and-stake: account don't have reward to claim");
    IERC20(token).approve(address(staking), claimAmount);
    uint share = staking.stakeFor(msg.sender, claimAmount);
    claimed[msg.sender] = _reward;
    emit ClaimAndStake(msg.sender, claimAmount, share);
  }

  /// @dev not allow renouncing.
  function renounceOwnership() public override onlyOwner {
    revert('renounce-ownership: not allowed');
  }

  // @dev withdraw tokens in unexpected scenarios. Emergency use only!
  function extract(address _token, uint _amount) external onlyOwner {
    IERC20(_token).safeTransfer(msg.sender, _amount);
  }
}
