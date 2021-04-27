from collections import deque
import pydot
import tempfile
from PIL import Image
from bitarray import bitarray
from bitarray.util import ba2int, int2ba

ind = 0


class Node:

    def __init__(self, label=None, weight=None, left=None, right=None):
        global ind
        self.ind = ind
        ind += 1
        self.label = label
        self.weight = weight
        self.left = left
        self.right = right

    def join(self, node):
        return Node(None, self.weight + node.weight, self, node)

    def __repr__(self):
        if self.weight:
            return "Index: " + str(self.ind) + "\nLabel: " + str(
                self.label) + "\nWeight: " + str(round(self.weight, 2))
        else:
            return "Index: " + str(self.ind) + "\nLabel: " + str(self.label)


class ExtendedNode(Node):

    def __init__(self, index, label=None, weight=None, left=None, right=None, parent=None):
        super().__init__(label, weight, left, right)
        self.parent = parent
        self.index = index

    # def split(self, node, index):
    #     new_node = ExtendedNode(index, None, self.weight + node.weight, self, node,
    #                             self.parent)
    #     if self.parent.left == self:
    #         self.parent.left = new_node
    #     else:
    #         self.parent.right = new_node
    #     self.parent = new_node
    #     node.parent = new_node
    #     return new_node

    def swap_child_link(self, new_node, old_node):
        if self.left == old_node:
            self.left = new_node
        else:
            self.right = new_node

    def swap(self, node, lis):
        lis[self.index], lis[node.index] = lis[node.index], lis[self.index]
        self.index, node.index = node.index, self.index
        if self.parent:
            self.parent.swap_child_link(node, self)
        if node.parent:
            node.parent.swap_child_link(self, node)
        node.parent, self.parent = self.parent, node.parent

    def get_code(self):
        code = []
        node = self
        while node.parent is not None:
            if node.parent.left == node:
                code.append(False)
            else:
                code.append(True)
            node = node.parent
        return reversed(code)


class PrettyPrint:

    def __init__(self):
        self.root = None

    def pretty_print(self, name=None, display=True):

        def dfs_helper(node, graph):
            for c in [node.left, node.right]:
                if c:
                    graph.add_edge(pydot.Edge(str(node), str(c)))
                    dfs_helper(c, graph)

        if self.root is None:
            print("Root is None!")
            return

        graph = pydot.Dot(graph_type='graph')
        dfs_helper(self.root, graph)
        if name is None:
            fout = tempfile.NamedTemporaryFile(suffix=".png")
            name = fout.name
        else:
            name += "_tree.png"
        graph.write(name, format="png")
        if display:
            Image.open(name).show()


class StaticHuffman(PrettyPrint):

    def __init__(self, text):
        self.text = text

    def count_letter_frequency(self):
        atom = 1 / len(self.text)
        frequency = dict()
        for c in self.text:
            val = frequency.get(c, 0)
            frequency[c] = val + atom
        return frequency

    def get_two_min(self, A, B):
        res = []
        while len(res) < 2:
            a, b = 1, 1
            if A:
                a = A[0].weight
            if B:
                b = B[0].weight
            if a < b:
                res.append(A.popleft())
            else:
                res.append(B.popleft())
        return (res[0], res[1])

    def static_huffman(self, letter_frequency):
        trees = deque()
        leaves = [Node(label, frequency) for label, frequency in letter_frequency.items()]
        if len(leaves) == 1:
            return leaves[0]
        leaves.sort(key=lambda node: node.weight)
        leaves = deque(leaves)
        while leaves or len(trees) > 1:
            N1, N2 = self.get_two_min(trees, leaves)
            trees.append(N1.join(N2))
        return trees[0]

    def calculate_huffman_tree(self):
        self.root = self.static_huffman(self.count_letter_frequency())
        return self.root


class DynamicHuffmanCompressor(PrettyPrint):

    def __init__(self, filename):
        self.filename = filename
        self.nodelist = []

    def increment(self, node):
        swap_index = node.index
        while node.weight == self.nodelist[swap_index].weight:
            swap_index -= 1
        self.nodelist[swap_index].swap(node, self.nodelist)
        node.weight += 1

    def encode(self, text):
        empty_node = ExtendedNode(0, "##", 0)
        nodes = {"##": empty_node}
        self.nodelist.append(empty_node)
        bits = bitarray()
        for c in text:
            if c in nodes:
                bits.extend(nodes[c].get_code())
                self.increment(nodes[c])
            else:
                bits.frombytes(c.encode())
                empty_node = self.nodelist.pop()
                m = len(self.nodelist)
                new_leaf = ExtendedNode(m + 1, c, 1)
                nodes[c] = new_leaf
                new_inner_node = ExtendedNode(m,
                                              None,
                                              0,
                                              left=empty_node,
                                              right=new_leaf,
                                              parent=empty_node.parent)
                empty_node.parent.swap_child_link(new_inner_node, empty_node)
                new_leaf.parent = new_inner_node
                empty_node.parent = new_inner_node
                self.nodelist.append(new_inner_node)
                self.nodelist.append(new_leaf)
                self.nodelist.append(empty_node)
                empty_node.index = m + 2
                self.increment(new_inner_node)
        self.root = self.nodelist[0]
        self.pretty_print()
        print(bits)
        with open(self.filename, "wb") as f:
            bits.tofile(f)


class StaticCompressor:

    def __init__(self, filename, huffman_class=None):
        self.filename = filename
        self.huffman_tree_builder = huffman_class

    def encode(self, text, display_tree=False):

        def tree_encoder(node, code=''):
            if node.left:
                tree_encoder(node.left, code + '0')
            if node.right:
                tree_encoder(node.right, code + '1')
            if node.label:
                bits.append(1)
                bits.frombytes(node.label.encode())
                header_bit_count[0] += 9
                ascii_to_bin[node.label] = code
            else:
                bits.append(0)
                header_bit_count[0] += 1

        bits = bitarray()
        ascii_to_bin = dict()
        number_bit_count = 11   # tree bit count (8 bits) and trailing zeros count (3 bits)
        header_bit_count = [number_bit_count]
        H = self.huffman_tree_builder(text)
        tree_encoder(H.calculate_huffman_tree())
        if display_tree:
            H.pretty_print()
        for c in text:
            bits.extend(bitarray(ascii_to_bin[c]))
        tmp = bitarray(int2ba(header_bit_count[0], 8))
        length = (len(bits) + number_bit_count)
        tmp.extend(bitarray(int2ba(8 - (length % 8), 3)))   # trailing zeros count
        tmp.extend(bits)
        with open(self.filename, "wb") as f:
            tmp.tofile(f)

    def decode(self):

        def tree_decoder():
            stack = []
            i = 11
            while i < header_bit_count:
                if bits[i]:
                    i += 1
                    label = bits[i:i + 8].tobytes().decode()
                    i += 8
                    stack.append(Node(label))
                else:
                    i += 1
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(Node(left=left, right=right))
            return stack[0]

        bits = bitarray()
        with open(self.filename, "rb") as f:
            bits.fromfile(f)
        header_bit_count = ba2int(bits[:8])
        trailing_zeros_count = ba2int(bits[8:11])
        root = node = tree_decoder()
        # In case there is only one letter in the tree:
        if node.left is None:
            node.left = node
            node.right = node
        charlist = []
        for i in range(header_bit_count, len(bits) - trailing_zeros_count):
            if node.label is not None:
                charlist.append(node.label)
                node = root
            if bits[i]:
                node = node.right
            else:
                node = node.left

        charlist.append(node.label)
        return ''.join(charlist)


if __name__ == '__main__':
    text = "abbbcccccccddddddddeghi"
    # C = StaticCompressor('test.compressed', StaticHuffman)
    # C.encode(text, True)
    # with open('test.compressed', "rb") as f:
    #     a = bitarray()
    #     a.fromfile(f)
    # print(C.decode())
    C = DynamicHuffmanCompressor('test.compressed')
    C.encode(text)
    # with open('test.compressed', "rb") as f:
    #     a = bitarray()
    #     a.fromfile(f)
    # print(C.decode())
