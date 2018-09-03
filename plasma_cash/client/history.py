import rlp
from rlp.sedes import CountableList, big_endian_int, binary

from .exceptions import TxHistoryNotFoundException


class History(rlp.Serializable):
    EMPTY_TX = b'\x00' * 32

    fields = [
        ('latest_tx_blk_num', big_endian_int),
        ('tx_history', CountableList(binary)),
        ('proofs', CountableList(binary)),
        ('blk_num', CountableList(big_endian_int))
    ]

    def __init__(self, deposit_tx_blk_num, tx, proof):
        self.latest_tx_blk_num = deposit_tx_blk_num
        self.tx_history = [tx]
        self.proofs = [proof]
        self.blk_num = [deposit_tx_blk_num]

    def update_tx_history(self, blk_num, tx, proof):
        if blk_num not in self.blk_num:
            if tx != self.EMPTY_TX:
                self.latest_tx_blk_num = max(self.latest_tx_blk_num, blk_num)
            self.tx_history.append(tx)
            self.proofs.append(proof)
            self.blk_num.append(blk_num)

    def get_data_by_block(self, blk_num):
        try:
            idx = self.blk_num.index(blk_num)
        except ValueError:
            raise TxHistoryNotFoundException('tx history not found')
        return self.tx_history[idx], self.proofs[idx]
