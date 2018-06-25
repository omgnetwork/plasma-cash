pragma solidity ^0.4.18;

import 'merkle.sol';
import 'Transaction.sol';


contract RootChain {
    using Merkle for bytes32;
    using Transaction for bytes;

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
    mapping(uint => exit) public exits;
    mapping(uint => challenge) public challenges;

    struct exit {
        bool hasValue;
        uint exitTime;
        uint exitTxBlkNum;
        bytes exitTx;
        uint txBeforeExitTxBlkNum;
        bytes txBeforeExitTx;
    }

    struct challenge {
        bool hasValue;
        bytes challengeTx;
        uint challengeTxBlkNum;
    }

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
        payable
        public
    {
        // TODO: handle the currency address if it's not zero
        if (currency == address(0)) {
            require(amount * 10**18 == msg.value);
        }
        bytes32 uid = keccak256(currency, msg.sender, depositCount);
        wallet[uid] = amount;
        depositCount += 1;
        Deposit(msg.sender, amount, uint256(uid));
    }

    // @dev Starts to exit a transaction
    // @param prevTx The previous transaction in bytes of the transaction that user wants to exit
    // @param prevTxProof The proof of the prevTx
    // @param prevTxBlkNum The block number of the prevTx
    // @param tx The transaction in bytes that user wants to exit
    // @param txProof The proof of the tx
    // @param txBlkNum The block number of the tx
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
        Transaction.Tx memory prevTxObj = prevTx.createTx();
        Transaction.Tx memory txObj = tx.createTx();

        require(prevTxBlkNum == txObj.prevBlock);
        require(prevTxObj.uid == txObj.uid);
        require(prevTxObj.amount == txObj.amount);
        require(prevTxObj.newOwner == txObj.signer);
        require(msg.sender == txObj.newOwner);

        bytes32 prevMerkleHash = sha3(prevTx);
        bytes32 prevRoot = childChain[prevTxBlkNum];
        bytes32 merkleHash = sha3(tx);
        bytes32 root = childChain[txBlkNum];
        require(prevMerkleHash.checkMembership(prevTxObj.uid, prevRoot, prevTxProof));
        require(merkleHash.checkMembership(txObj.uid, root, txProof));

        // Record the exit tx.
        require(!exits[txObj.uid].hasValue);
        exits[txObj.uid] = exit({
            hasValue: true,
            exitTime: block.timestamp + 2 weeks,
            exitTxBlkNum: txBlkNum,
            exitTx: tx,
            txBeforeExitTxBlkNum: prevTxBlkNum,
            txBeforeExitTx: prevTx
        });
    }

    function challengeExit(uint uid, bytes challengeTx, bytes proof, uint blkNum) public {
        require(exits[uid].hasValue);

        Transaction.Tx memory exitTxObj = (exits[uid].exitTx).createTx();
        Transaction.Tx memory txBeforeExitTxObj = (exits[uid].txBeforeExitTx).createTx();
        Transaction.Tx memory challengeTxObj = challengeTx.createTx();

        require(exitTxObj.uid == challengeTxObj.uid);
        require(exitTxObj.amount == challengeTxObj.amount);

        bytes32 merkleHash = sha3(challengeTx);
        bytes32 root = childChain[blkNum];
        require(merkleHash.checkMembership(uid, root, proof));

        if (exitTxObj.newOwner == challengeTxObj.signer) {
            // Challenge tx spent the exit tx. Cancel it.
            delete exits[uid].hasValue;
        } else if (blkNum < exits[uid].exitTxBlkNum
            && txBeforeExitTxObj.newOwner == challengeTxObj.signer) {
            // Exit tx double spent the previous tx. Cancel it.
            delete exits[uid].hasValue;
        } else if (blkNum < exits[uid].txBeforeExitTxBlkNum) {
            // Challenger provides a tx in history. Exitor needs to respond it.
            // TODO: An exit could be challenged many times simultaneously.
            challenges[uid] = challenge({
                hasValue: true,
                challengeTx: challengeTx,
                challengeTxBlkNum: blkNum
            });
        }
    }

    function respondChallengeExit(uint uid, bytes respondTx, bytes proof, uint blkNum) public {
        require(challenges[uid].hasValue);
        require(exits[uid].hasValue);

        Transaction.Tx memory challengeTxObj = (challenges[uid].challengeTx).createTx();
        Transaction.Tx memory respondTxObj = respondTx.createTx();

        require(challengeTxObj.uid == respondTxObj.uid);
        require(challengeTxObj.amount == respondTxObj.amount);
        require(challengeTxObj.newOwner == respondTxObj.signer);
        require(blkNum <= exits[uid].txBeforeExitTxBlkNum);

        bytes32 merkleHash = sha3(respondTx);
        bytes32 root = childChain[blkNum];
        require(merkleHash.checkMembership(uid, root, proof));

        // Challenge has been responded. Cancel it.
        delete challenges[uid].hasValue;
    }
}
