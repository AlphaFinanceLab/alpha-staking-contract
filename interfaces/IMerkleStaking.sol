// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

interface IMerkleStaking {
  // Returns how much reward tokens have the user already claimed.
  function claimed(address _user) external view returns (uint amount);

  // Updates merkle root to the new one.
  function updateMerkleRoot(bytes32 _root) external;

  // Deposits reward tokens.
  function deposit(uint _amount) external;

  // Claim and stake ALPHA to Alpha Staking
  function claimAndStake(uint _reward, bytes32[] calldata _proof) external;

  // Withdraws reward tokens from the contract. Can only be called by owner/governor.
  function withdraw(uint _amount) external;
}
