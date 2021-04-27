from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from math import log2, ceil


class LZW:
    """Lempel-Ziv-Welch algorithm implementation with variable compression block
    The compression block dynamically changes as the dictionary fills. Default variability
    range is from 9 to 16 (first character is encoded with 8 bits).
    Changing block size can yield much better compression ratio,
    especially on natural language texts"""

    BLOCK_SIZE = 16
    ASCII_LEN = 256

    def __init__(self, filename):
        self.filename = filename
        self.MAX_LEN = int(2**self.BLOCK_SIZE)

    def encode(self, text):
        base_table = dict()
        for i in range(self.ASCII_LEN):
            base_table[chr(i)] = int2ba(i, self.BLOCK_SIZE)
        bits = bitarray()
        table = base_table.copy()
        table_len = self.ASCII_LEN
        string = text[0]
        for i in range(1, len(text)):
            char = text[i]
            if string + char in table:
                string += char
            else:
                bits.extend(table[string][-ceil(log2(table_len)):])
                if table_len == self.MAX_LEN:
                    table = base_table.copy()
                    table_len = self.ASCII_LEN
                table[string + char] = int2ba(table_len, self.BLOCK_SIZE)
                table_len += 1
                string = char
        bits.extend(table[string][-ceil(log2(table_len)):])
        with open(self.filename, "wb") as f:
            bits.tofile(f)

    def decode(self):
        table = [None] * self.MAX_LEN
        for i in range(self.ASCII_LEN):
            table[i] = chr(i)
        bits = bitarray()
        with open(self.filename, "rb") as f:
            bits.fromfile(f)
        table_len = self.ASCII_LEN
        start = ceil(log2(table_len))
        string = table[ba2int(bits[:start])]
        text = string
        # If the character count is not a multiply of BLOCK_SIZE, there were some
        # automatically appended zeros at the end of file to fill whole byte, we skip these
        # It's not actually needed to work, but is a nice thing to expose
        actual_size = len(bits) - (len(bits) % self.BLOCK_SIZE)
        i = start
        while i < actual_size:
            if table_len == self.MAX_LEN:
                table_len = self.ASCII_LEN
            jump = ceil(log2(table_len + 1))
            code = ba2int(bits[i:i + jump])
            if code >= table_len:
                entry = string + string[0]
            else:
                entry = table[code]
            text += entry
            table[table_len] = string + entry[0]
            table_len += 1
            string = entry
            i += jump
        return text


if __name__ == '__main__':
    text = 'abracadabra'
    C = LZW('compressed.lzw')
    # C.encode(text)
    print(C.decode())
