pragma solidity ^0.4.18;

import 'merkle.sol';
import 'RLP.sol';


contract RootChain {
    using Merkle for bytes32;
    using RLP for bytes;
    using RLP for RLP.RLPItem;
    using RLP for RLP.Iterator;

    /*
     * Events
     */
    event Deposit(address depositor, uint256 amount, uint256 uid);

    /*
     * Storage
     */
    address public authority;
    uint public depositCount;
    uint public currentBlkNum;
    mapping(uint => bytes32) public childChain;
    mapping(bytes32 => uint) public wallet;
    mapping(uint => uint) public exits;

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
        Deposit(msg.sender, amount, uint256(uid));
    }

    function startExit(
        bytes prevTx,
        bytes prevTxProof,
        uint prevTxBlkNum,
        bytes tx,
        bytes txProof,
        uint txBlkNum
    )
        public
    {
        var prevTxList = prevTx.toRLPItem().toList();
        var txList = tx.toRLPItem().toList();
        require(prevTxList.length == 5);
        require(txList.length == 5);

        // TODO: Should optimize these lines with more readability.
        // TODO: Should check the transaction signature.
        require(prevTxBlkNum == txList[0].toUint());
        require(prevTxList[1].toUint() == txList[1].toUint());
        require(txList[2].toUint() == txList[2].toUint());
        require(msg.sender == txList[3].toAddress());
        uint uid = txList[1].toUint();

        bytes32 prevMerkleHash = sha3(prevTx);
        bytes32 prevRoot = childChain[prevTxBlkNum];
        bytes32 merkleHash = sha3(tx);
        bytes32 root = childChain[txBlkNum];
        require(prevMerkleHash.checkMembership(uid, prevRoot, prevTxProof));
        require(merkleHash.checkMembership(uid, root, txProof));

        // Record the exitable timestamp.
        require(exits[uid] == 0);
        exits[uid] = block.timestamp + 2 weeks;
    }
}
