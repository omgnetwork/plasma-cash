from collections import OrderedDict
from ethereum.utils import sha3


class SparseMerkleTree(object):

    def __init__(self, leaves={}):
        self.depth = 4
        self.leaves = OrderedDict(sorted(leaves.items(), key=lambda t: t[0]))
        self.default_nodes = [b'\x00' * 32]
        self.create_default_nodes()
        if bool(leaves):
            self.root = self.create_tree()
        else:
            self.root = self.default_nodes[self.depth - 1]

    def create_default_nodes(self):
        for i in range(1, self.depth):
            prev_default = self.default_nodes[i - 1]
            self.default_nodes.append(sha3(prev_default + prev_default))

    def create_tree(self):
        tree_level = self.leaves
        for i in range(self.depth - 1):
            next_level = {}
            prev_index = -1
            for index, value in tree_level.items():
                if index % 2 == 0:
                    next_level[index // 2] = sha3(value + self.default_nodes[i])
                else:
                    if index == prev_index + 1:
                        next_level[index // 2] = sha3(tree_level[prev_index] + value)
                    else:
                        next_level[index // 2] = sha3(self.default_nodes[i] + value)
                prev_index = index
            tree_level = next_level
        return tree_level[0]
