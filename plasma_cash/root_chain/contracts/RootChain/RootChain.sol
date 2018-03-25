pragma solidity ^0.4.18;


contract RootChain {
    /*
     * Events
     */
    event Deposit(address depositor, uint256 amount, bytes32 uid);

    /*
     * Storage
     */
    address public authority;
    uint public depositCount;
    uint public currentBlkNum;
    mapping(uint => bytes32) public childChain;
    mapping(bytes32 => uint) public wallet;

    /*
     * Modifiers
     */
    modifier isAuthority() {
        require(msg.sender == authority);
        _;
    }


    function RootChain()
        public
    {
        authority = msg.sender;
        depositCount = 0;
        currentBlkNum = 0;
    }

    // @dev Allows Plasma chain operator to submit block root
    // @param blkRoot The root of a child chain block
    // @param blknum The child chain block number
    function submitBlock(bytes32 blkRoot, uint blknum)
        public
        isAuthority
    {
        require(currentBlkNum + 1 == blknum);
        childChain[blknum] = blkRoot;
        currentBlkNum += 1;
    }

    // @dev Allows anyone to deposit funds into the Plasma chain
    // @param currency The address of currency or zero if deposit Eth
    // @param amount The amount of currency to deposit
    function deposit(address currency, uint amount)
        public
    {
        // TODO: handle the currency address if it's not zero
        bytes32 uid = keccak256(currency, msg.sender, depositCount);
        wallet[uid] = amount;
        depositCount += 1;
        Deposit(msg.sender, amount, uid);
    }
}
