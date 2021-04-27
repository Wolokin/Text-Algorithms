from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from pretty_print import PrettyPrint
from node import Node


class ExtendedNode(Node):

    def __init__(self, index, label=None, weight=None, left=None, right=None, parent=None):
        super().__init__(label, weight, left, right)
        self.parent = parent
        self.index = index

    def swap_child_link(self, new_node, old_node):
        if self.left == old_node:
            self.left = new_node
        else:
            self.right = new_node

    def swap_index(self, node, lis):
        lis[self.index], lis[node.index] = lis[node.index], lis[self.index]
        self.index, node.index = node.index, self.index

    def swap(self, node, lis):
        self.swap_index(node, lis)
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


class DynamicHuffmanCompressor(PrettyPrint):
    '''This class realizes dynamic huffman encoding and decoding'''

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.nodelist = []

    def increment(self, node):
        '''Takes care of weight increases and swaps if required'''
        swap_index = node.index
        while swap_index >= 0 and node.weight == self.nodelist[swap_index].weight:
            swap_index -= 1
        to_swap = self.nodelist[swap_index + 1]
        if to_swap != node and to_swap != node.parent:
            self.nodelist[swap_index + 1].swap(node, self.nodelist)
        node.weight += 1
        if node.parent:
            self.increment(node.parent)

    def create_inner_node(self, empty_node, new_leaf):
        '''Creates new inner node, used when a new letter is met'''
        new_inner_node = ExtendedNode(len(self.nodelist),
                                      None,
                                      0,
                                      left=empty_node,
                                      right=new_leaf,
                                      parent=empty_node.parent)
        if empty_node.parent:
            empty_node.parent.swap_child_link(new_inner_node, empty_node)
        new_leaf.parent = new_inner_node
        empty_node.parent = new_inner_node
        self.nodelist.append(new_inner_node)
        new_inner_node.swap_index(empty_node, self.nodelist)
        return new_inner_node

    def add_letter(self, c, empty_node):
        '''Adds a new letter to the tree'''
        new_leaf = ExtendedNode(len(self.nodelist), c, 1)
        self.nodelist.append(new_leaf)
        new_inner_node = self.create_inner_node(empty_node, new_leaf)
        self.increment(new_inner_node)
        return new_leaf

    def encode(self, text):
        '''Dynamically encodes text as binary; every time a new letter is met, binary code of
        the empty_node (representing all not yet met letters) is appended to binary code followed
        by the ascii code of the letter; otherwise if a letter has already been in the tree, its
        current code is appended and its weight is increased which also means that tree update
        (increasing parents weights and swaping some nodes) may be required'''
        empty_node = ExtendedNode(0, "##", 0)
        nodes = {"##": empty_node}
        self.nodelist = [empty_node]
        bits = bitarray()
        for c in text:
            if c in nodes:
                bits.extend(nodes[c].get_code())
                self.increment(nodes[c])
            else:
                bits.extend(empty_node.get_code())
                bits.frombytes(c.encode())
                nodes[c] = self.add_letter(c, empty_node)

        self.root = self.nodelist[0]
        trailing_zeros = (8 - ((len(bits) + 3) % 8)) % 8
        tmp = bitarray(int2ba(trailing_zeros, 3))
        tmp.extend(bits)
        with open(self.filename, "wb") as f:
            tmp.tofile(f)

    def decode(self):
        """Decodes binary file encoded by the 'encode(text)' method. Similarly to the encoding,
        here the huffman tree is also dynamically adjusted while reading the binary file. Hence
        it is not required to explicitly save huffman tree in the file thus allowing potentially
        slighlty better compression ratio"""
        empty_node = ExtendedNode(0, "##", 0)
        nodes = {"##": empty_node}
        self.nodelist = [empty_node]
        bits = bitarray()
        with open(self.filename, "rb") as f:
            bits.fromfile(f)
        trailing_zeros = ba2int(bits[:3])
        charlist = []
        i = 3
        while i < len(bits) - trailing_zeros:
            node = self.nodelist[0]
            # nodes always have either both children or none, so checking for one is sufficient
            while node.left:
                if bits[i]:
                    node = node.right
                else:
                    node = node.left
                i += 1
            if node == empty_node:
                letter = bits[i:i + 8].tobytes().decode()
                i += 8
                nodes[letter] = self.add_letter(letter, empty_node)
            else:
                letter = node.label
                self.increment(nodes[letter])
            charlist.append(letter)
        return ''.join(charlist)


if __name__ == '__main__':
    text = "abracadabra"
    D = DynamicHuffmanCompressor('compressed.dynamic')
    D.encode(text)
    print(D.decode())
