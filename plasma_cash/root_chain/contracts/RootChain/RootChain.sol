pragma solidity ^0.4.18;

import 'Challenge.sol';
import 'merkle.sol';
import 'Transaction.sol';


contract RootChain {
    using Challenge for Challenge.challenge[];
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
    mapping(uint => funds) public wallet;
    mapping(uint => exit) public exits;
    mapping(uint => Challenge.challenge[]) public challenges;

    struct exit {
        bool hasValue;
        uint exitTime;
        uint exitTxBlkNum;
        bytes exitTx;
        uint txBeforeExitTxBlkNum;
        bytes txBeforeExitTx;
        address owner;
    }

    struct funds {
        bool hasValue;
        bool isConfirmed;
        uint amount;
        address depositor;
    }

    /*
     * Modifiers
     */
    modifier isAuthority() {
        require(msg.sender == authority);
        _;
    }


    constructor ()
        public
    {
        authority = msg.sender;
        depositCount = 0;
        currentBlkNum = 0;
    }

    // @dev Allows Plasma chain operator to submit block root
    // @param blkRoot The root of a child chain block
    // @param blknum The child chain block number
    function submitBlock(
        bytes32 blkRoot,
        uint blknum,
        bool isDepositBlock,
        bytes depositTx,
        bytes depositTxProof
    )
        public
        isAuthority
    {
        if (isDepositBlock) {
            Transaction.Tx memory txObj = depositTx.createTx();
            bytes32 merkleHash = keccak256(depositTx);
            // Check if the deposit is aborted
            require(wallet[txObj.uid].hasValue);
            require(merkleHash.checkMembership(txObj.uid, blkRoot, depositTxProof));
            wallet[txObj.uid].isConfirmed = true;
        }
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
        returns (uint)
    {
        // TODO: handle the currency address if it's not zero
        if (currency == address(0)) {
            require(amount * 10**18 == msg.value);
        }
        uint uid = uint256(keccak256(currency, msg.sender, depositCount));
        wallet[uid] = funds({
            hasValue: true,
            isConfirmed: false,
            amount: amount,
            depositor: msg.sender
        });
        depositCount += 1;
        emit Deposit(msg.sender, amount, uid);
        return uid;
    }

    // @dev Abort an deposit which is not included in child chain
    // @param uid The id to specify the deposit
    function abortDeposit(uint uid) public {
        require(!wallet[uid].isConfirmed);
        require(wallet[uid].depositor == msg.sender);

        msg.sender.transfer(wallet[uid].amount*10**18);
        delete wallet[uid].hasValue;
    }

    // @dev Starts to exit a deposit transaction
    // @param tx The transaction in bytes that user wants to exit
    // @param txProof The merkle proof of the tx
    // @param txBlkNum The block number of the tx
    function startDepositExit(bytes tx, bytes txProof, uint txBlkNum) public {
        Transaction.Tx memory txObj = tx.createTx();
        require(txObj.prevBlock == 0);
        require(msg.sender == txObj.newOwner);

        bytes32 merkleHash = keccak256(tx);
        bytes32 root = childChain[txBlkNum];
        require(merkleHash.checkMembership(txObj.uid, root, txProof));

        // Record the exit tx.
        require(!exits[txObj.uid].hasValue);
        exits[txObj.uid] = exit({
            hasValue: true,
            exitTime: block.timestamp + 2 weeks,
            exitTxBlkNum: txBlkNum,
            exitTx: tx,
            txBeforeExitTxBlkNum: 0,
            txBeforeExitTx: "",
            owner: msg.sender
        });
    }

    // @dev Starts to exit a transaction
    // @param prevTx The previous transaction in bytes of the transaction that user wants to exit
    // @param prevTxProof The merkle proof of the prevTx
    // @param prevTxBlkNum The block number of the prevTx
    // @param tx The transaction in bytes that user wants to exit
    // @param txProof The merkle proof of the tx
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

        bytes32 prevMerkleHash = keccak256(prevTx);
        bytes32 prevRoot = childChain[prevTxBlkNum];
        bytes32 merkleHash = keccak256(tx);
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
            txBeforeExitTx: prevTx,
            owner: msg.sender
        });
    }

    // @dev Challenge an exit transaction
    // @param uid The id to specify the exit transaction
    // @param challengeTx The transaction in bytes that user wants to challenge the exit
    // @param proof The merkle proof of the challenge transaction
    // @param blkNum The block number of the challenge transaction
    function challengeExit(uint uid, bytes challengeTx, bytes proof, uint blkNum) public {
        require(exits[uid].hasValue);

        Transaction.Tx memory exitTxObj = (exits[uid].exitTx).createTx();
        Transaction.Tx memory txBeforeExitTxObj = (exits[uid].txBeforeExitTx).createTx();
        Transaction.Tx memory challengeTxObj = challengeTx.createTx();

        require(exitTxObj.uid == challengeTxObj.uid);
        require(exitTxObj.amount == challengeTxObj.amount);

        bytes32 merkleHash = keccak256(challengeTx);
        bytes32 root = childChain[blkNum];
        require(merkleHash.checkMembership(uid, root, proof));

        if (blkNum > exits[uid].exitTxBlkNum && exitTxObj.newOwner == challengeTxObj.signer) {
            // Challenge tx spent the exit tx. Cancel it.
            delete exits[uid].hasValue;
        } else if (blkNum < exits[uid].exitTxBlkNum
            && txBeforeExitTxObj.newOwner == challengeTxObj.signer) {
            // Exit tx double spent the previous tx. Cancel it.
            delete exits[uid].hasValue;
        } else if (blkNum < exits[uid].txBeforeExitTxBlkNum) {
            // Challenger provides a tx in history. Exitor needs to respond it.
            if (!challenges[uid].contains(challengeTx)) {
                challenges[uid].push(Challenge.challenge({
                    hasValue: true,
                    challengeTx: challengeTx,
                    challengeTxBlkNum: blkNum
                }));
            }
        }
    }

    // @dev Respond to a challenge transaction
    // @param uid The id to specify the challenge transaction
    // @param challengeTx The transaction in bytes that user challenged before
    // @param respondTx The transaction in bytes that user responds to the challenge transaction
    // @param proof The merkle proof of the respond transaction
    // @param blkNum The block number of the respond transaction
    function respondChallengeExit(
        uint uid,
        bytes challengeTx,
        bytes respondTx,
        bytes proof,
        uint blkNum
    )
        public
    {
        require(challenges[uid].contains(challengeTx));
        require(exits[uid].hasValue);

        Transaction.Tx memory challengeTxObj = challengeTx.createTx();
        Transaction.Tx memory respondTxObj = respondTx.createTx();

        require(challengeTxObj.uid == respondTxObj.uid);
        require(challengeTxObj.amount == respondTxObj.amount);
        require(challengeTxObj.newOwner == respondTxObj.signer);
        require(blkNum <= exits[uid].txBeforeExitTxBlkNum);

        bytes32 merkleHash = keccak256(respondTx);
        bytes32 root = childChain[blkNum];
        require(merkleHash.checkMembership(uid, root, proof));

        // Challenge has been responded. Cancel it.
        challenges[uid].remove(challengeTx);
    }

    // @dev Finalize an exit
    // @param uid The id to specify the exit transaction
    function finalizeExit(uint uid) public {
        require(exits[uid].hasValue);
        require(now >= exits[uid].exitTime);
        for (uint i = 0; i < challenges[uid].length; i++) {
            require(!challenges[uid][i].hasValue);
        }

        exits[uid].owner.transfer(wallet[uid].amount*10**18);
        delete exits[uid].hasValue;
    }

    function isChallengeExisted(uint uid, bytes challengeTx) public returns (bool) {
        return challenges[uid].contains(challengeTx);
    }
}
