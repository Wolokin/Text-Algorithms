from PIL import Image
import numpy as np
import pydot
import tempfile
from queue import Queue
from timeit import default_timer as timer


class Node:
    state_counter = 0

    def __init__(self, parent=None):
        self.state = Node.state_counter
        Node.state_counter += 1

        self.parent = parent
        self.children = dict()
        self.fail_link = parent

    # finds next state, using fail links if necessary
    def next_state(self, key):
        if self.parent == self:
            return self.children.get(key, self)
        return self.children.get(key, self.fail_link.next_state(key))

    def pretty_print(self, name=None, display=True):

        def dfs_helper(node, graph, visited):
            visited.add(node)
            for k, v in node.children.items():
                graph.add_edge(pydot.Edge(str(node.state), str(v.state), label=str(k)))
                if v not in visited:
                    dfs_helper(v, graph, visited)

        graph = pydot.Dot(graph_type='digraph')
        dfs_helper(self, graph, set())

        if name is None:
            fout = tempfile.NamedTemporaryFile(suffix=".png")
            name = fout.name
        else:
            name += "_trie.png"
        graph.write(name, format="png")
        if display:
            Image.open(name).show()


class PatternSearcher2d:
    neutral = '#'

    def __init__(self, pattern):
        self.pattern = self.convert_text(pattern, self.neutral)
        self.trie_root, self.accepting_states = None, None
        self.text = None

    def preprocess(self):
        self.trie_root, self.accepting_states = self.aho_corasick()
        return self

    def load_text(self, text):
        self.text = self.convert_text(text, self.neutral)
        return self

    # Neutral is a char non existent in the file we are going to scan
    # Only important when supplying a list of lines
    @staticmethod
    def convert_text(text, neutral='#'):
        if isinstance(text, list):   # Assumes text is a list of lines
            n = len(text)
            m = max([len(line) for line in text])
            arr = np.ndarray((n, m), dtype=object)
            for i in range(n):
                for j in range(m):
                    if j < len(text[i]):
                        arr[i, j] = text[i][j]
                    else:
                        arr[i, j] = neutral
            text = arr
        elif not isinstance(text, (np.ndarray)):
            Exception("Bad text format, has to be either list of lines or np.ndarray")
        # Assumes text is a numpy color array of shape (n,m,color_data)
        # where color_data is a list (so non_hashable)
        else:
            arr = np.ndarray(text.shape[:2], dtype=object)
            for i in range(text.shape[0]):
                for j in range(text.shape[1]):
                    arr[i, j] = tuple(text[i, j, :])   # 'Making' list hashable
            text = arr
        return text

    # pattern must be of type np.ndarray
    def aho_corasick(self, pattern=None):
        if pattern is None:
            pattern = self.pattern
        (n, m) = pattern.shape[:2]
        # Creating a simple trie
        trie = Node()
        trie.parent = trie
        trie.fail_link = trie
        accepting_states = []
        alphabet = set()
        for i in range(n):
            p = trie
            for j in range(m):
                key = pattern[i, j]
                if key not in p.children:
                    alphabet.add(key)
                    p.children[key] = Node(p)
                p = p.children[key]
            accepting_states.append(p.state)
        # trie.pretty_print("trie")
        # Creating fail links
        # Starting bfs from nodes with dist = 2, (dist={0,1} fail links are already correct)
        Q = Queue()
        [Q.put((k, v)) for c in trie.children.values() for k, v in c.children.items()]
        while not Q.empty():
            k, v = Q.get()
            v.fail_link = v.parent.fail_link.next_state(k)
            for k2, v2 in v.children.items():
                Q.put((k2, v2))

        # Determinization of the automaton
        Q = Queue()
        Q.put(trie)
        while not Q.empty():
            v = Q.get()
            for u in v.children.values():
                Q.put(u)
            for k, u in v.fail_link.children.items():
                if k not in v.children:
                    v.children[k] = u

        # trie.pretty_print("automaton")
        return trie, accepting_states

    def search(self):
        n, m = self.text.shape[:2]
        pn, pm = self.pattern.shape[:2]
        states = np.zeros(self.text.shape)
        for i in range(n):
            node = self.trie_root
            for j in range(m):
                node = node.children.get(self.text[i, j], self.trie_root)
                states[i, j] = node.state
        pattern_vert = self.convert_text([self.accepting_states])
        root, accepting_state = self.aho_corasick(pattern_vert)
        accepting_state = accepting_state[0]
        found_coords = []
        for j in range(m):
            node = root
            for i in range(n):
                node = node.children.get(states[i, j], root)
                if node.state == accepting_state:
                    found_coords.append((i - pn + 1, j - pm + 1))
        return found_coords

    @staticmethod
    def search_wrapper(text, pattern):
        return PatternSearcher2d(pattern).preprocess().load_text(text).search()


def find_same_letter_pos(text):
    alphabet = set()
    for line in text:
        for letter in line:
            alphabet.add(letter)
    res = dict()
    for letter in alphabet:
        if letter.isalpha():
            res[letter] = PatternSearcher2d.search_wrapper(text, [letter, letter])
    for k, v in sorted(res.items()):
        print(repr(k) + ":", v)


def flip_colors(im, where, size=(20, 20)):
    im = im.copy()
    for x, y in where:
        for i in range(size[0]):
            for j in range(size[1]):
                for k in range(3):
                    im[x + i, y + j, k] = 255 - im[x + i, y + j, k]
    return Image.fromarray(im.astype(np.uint8))


def bench(text, pattern, reps=10):
    P = PatternSearcher2d(pattern)
    P.load_text(text)

    t1 = timer()
    for _ in range(reps):
        P.preprocess()
    t2 = timer()
    print("Preprocessing time:", (t2 - t1) / reps)

    t1 = timer()
    for _ in range(reps):
        P.search()
    t2 = timer()
    print("Searching time:", (t2 - t1) / reps)


def divide_and_search(image, pattern, parts, reps=10):
    P = PatternSearcher2d(pattern)
    P.load_text(image)
    P.preprocess()

    size = image.shape[0]
    parts = [
        PatternSearcher2d.convert_text(image[i * size // parts:(i + 1) * size // parts, :])
        for i in range(parts)
    ]

    t1 = timer()
    for _ in range(reps):
        for part in parts:
            P.text = part
            P.search()
    t2 = timer()
    print("Searching time:", (t2 - t1) / reps)


if __name__ == '__main__':
    im = np.asarray(Image.open('../sources/haystack.png'))
    # print(PatternSearcher2d.search_wrapper(['aaabcd', 'eeaab', 'ppcba'],
    #                                        ["abc", "aab", "cba"]))
    with open("../sources/haystack.txt", "r") as f:
        text = f.readlines()
        # Task2
        find_same_letter_pos(text)
        # Task3
        print("th:", PatternSearcher2d.search_wrapper(text, ['th', 'th']))
        print("t h:", PatternSearcher2d.search_wrapper(text, ['t h', 't h']))
        # Task4
        r = np.asarray(Image.open('../patterns/r.png'))
        k = np.asarray(Image.open('../patterns/k.png'))
        o = np.asarray(Image.open('../patterns/o.png'))
        where = PatternSearcher2d.search_wrapper(im, r)
        flip_colors(im, where, r.shape).show()
        print("Found", len(where), "occurences of r.png")
        print("Should find", len(PatternSearcher2d.search_wrapper(text, ["r"])))
        where = PatternSearcher2d.search_wrapper(im, k)
        flip_colors(im, where, k.shape).show()
        print("Found", len(where), "occurences of k.png")
        print("Should find", len(PatternSearcher2d.search_wrapper(text, ["k"])))
        where = PatternSearcher2d.search_wrapper(im, o)
        flip_colors(im, where, o.shape).show()
        print("Found", len(where), "occurences of o.png")
        print("Should find", len(PatternSearcher2d.search_wrapper(text, ["o"])))
        # Task5
        pattern = np.asarray(Image.open('../patterns/pattern.png'))
        where = PatternSearcher2d.search_wrapper(im, pattern)
        flip_colors(np.asarray(Image.open('../sources/haystack.png')),
                    where,
                    size=pattern.shape).show()
        # Task6
        print("=========Small pattern=========")
        bench(im, np.asarray(Image.open("../patterns/small.png")), 10)
        print("=========Medium pattern=========")
        bench(im, np.asarray(Image.open("../patterns/medium.png")), 10)
        print("=========Big pattern=========")
        bench(im, np.asarray(Image.open("../patterns/big.png")), 10)
        # Task7
        for s in [2, 4, 8]:
            print("=========Divided into", s, "parts=========")
            divide_and_search(im, np.asarray(Image.open("../patterns/medium.png")), s)
