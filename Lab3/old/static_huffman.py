from collections import deque
from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from pretty_print import PrettyPrint
from node import Node


class StaticHuffman(PrettyPrint):

    def __init__(self, text):
        super().__init__()
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
        return res[0], res[1]

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


class StaticCompressor:
    ''' This class can take any class with a 'calculate_huffman_tree()' method
    which returns a prefix-free tree root (using nodes from the 'Node' import)
    Probably not a very useful feature :)'''

    # File encoding metadata
    HUFFMAN_BIT_COUNT_SIZE = 16
    TRAILING_ZEROS_SIZE = 3
    HEADER_BIT_SIZE = None

    def __init__(self, filename, huffman_class=None):
        self.filename = filename
        self.huffman_tree_builder = huffman_class
        self.HEADER_BIT_SIZE = self.HUFFMAN_BIT_COUNT_SIZE + self.TRAILING_ZEROS_SIZE

    def encode(self, text, display_tree=False):
        '''Encodes 'text' to a file named self.filename\n
        current formatting is: bits[:16] - number of bits used for the huffman tree encoding
        bits[16:19] - trailing zeros count (automatically appended zeros at the end of file)
        then the tree is encoded followed by the text in huffman code followed by 0-7 trailing
        zeros'''

        def tree_encoder(node, code=''):
            '''Does post-order travelsal of the huffman tree
            When it finds an inner node, '0' is printed
            When it finds a leaf, it prints '1' followed by 8-bit ascii code
            The tree size is 2m-1 where m is the alphabet size
            hence the post-order travelsal takes (2m-1) + 8*m = (10m - 1) bits of space'''
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
        header_bit_count = [self.HEADER_BIT_SIZE]
        H = self.huffman_tree_builder(text)
        tree_encoder(H.calculate_huffman_tree())
        if display_tree:
            H.pretty_print()
        for c in text:
            bits.extend(bitarray(ascii_to_bin[c]))
        tmp = bitarray(int2ba(header_bit_count[0], self.HUFFMAN_BIT_COUNT_SIZE))
        length = (len(bits) + self.HEADER_BIT_SIZE)
        tmp.extend(bitarray(int2ba(8 - (length % 8),
                                   self.TRAILING_ZEROS_SIZE)))   # trailing zeros count

        tmp.extend(bits)
        with open(self.filename, "wb") as f:
            tmp.tofile(f)

    def decode(self):
        '''Decodes file 'self.filename' using formatting explained in the 'encode()' docstring'''

        def tree_decoder():
            stack = []
            i = self.HEADER_BIT_SIZE
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
        header_bit_count = ba2int(bits[:self.HUFFMAN_BIT_COUNT_SIZE])
        trailing_zeros_count = ba2int(bits[self.HUFFMAN_BIT_COUNT_SIZE:self.HEADER_BIT_SIZE])
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
    text = "abracadabra"
    S = StaticCompressor('static.compressed', StaticHuffman)
    S.encode(text, True)
    print(S.decode())
