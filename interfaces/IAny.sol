pragma solidity 0.6.12;

interface IAny {

    function STATUS_READY() external view returns (uint);

    function STATUS_UNBONDING() external view returns (uint);

    function UNBONDING_DURATION() external view returns (uint);

    function WITHDRAW_DURATION() external view returns (uint);

    function setWorker(address) external;

    function stake(uint) external;

    function stake(address, uint) external;

    function mint(address, uint) external;

    function mint(uint) external;

    function transfer(address, uint) external;

    function approve(address, uint) external;

    function reward(uint) external;

    function alpha() external view returns (address);

    function governor() external view returns (address);

    function pendingGovernor() external view returns (address);

    function worker() external view returns (address);

    function decimals() external view returns(uint);

    function owner() external view returns (address);

    function balanceOf(address) external view returns (uint);

    function totalAlpha() external view returns (uint);

    function totalShare() external view returns (uint);

    function getStakeValue(address) external view returns (uint);

    function unbond(uint) external;

    function withdraw() external;

    function users(address) external view returns (uint, uint, uint, uint);

    function setPendingGovernor(address) external;

    function acceptGovernor() external;

    function skim(uint) external;
    
    function extract(uint) external;

    function getProxyImplementation(address) external view returns (address);

    function setMerkle(address) external;
}