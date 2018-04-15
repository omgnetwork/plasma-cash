from collections import OrderedDict
from ethereum.utils import sha3


class SparseMerkleTree(object):

    def __init__(self, leaves={}):
        self.depth = 256
        # Sort the transaction dict by index.
        self.leaves = OrderedDict(sorted(leaves.items(), key=lambda t: t[0]))
        self.default_nodes = [b'\x00' * 32]
        self.create_default_nodes()
        if leaves:
            self.root = self.create_tree()
        else:
            self.root = self.default_nodes[self.depth - 1]

    def create_default_nodes(self):
        # Default nodes are the nodes whose children are both empty nodes at each level.
        for level in range(1, self.depth):
            prev_default = self.default_nodes[level - 1]
            self.default_nodes.append(sha3(prev_default + prev_default))

    def create_tree(self):
        tree_level = self.leaves
        for level in range(self.depth - 1):
            next_level = {}
            prev_index = -1
            for index, value in tree_level.items():
                if index % 2 == 0:
                    # If the node is a left node, assume the right sibling is a default node.
                    next_level[index // 2] = sha3(value + self.default_nodes[level])
                else:
                    # If the node is a right node, check if its left sibling is a default node.
                    if index == prev_index + 1:
                        next_level[index // 2] = sha3(tree_level[prev_index] + value)
                    else:
                        next_level[index // 2] = sha3(self.default_nodes[level] + value)
                prev_index = index
            tree_level = next_level
        return tree_level[0]
