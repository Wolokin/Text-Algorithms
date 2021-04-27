import pydot
import tempfile
from PIL import Image


class Node:

    def __init__(self):
        self.children = dict()


def create_trie(text):
    trie = Trie()
    for i in range(len(text)):
        trie.insert(text[i:])
    return trie


class Trie:

    def __init__(self):
        self.root = Node()

    def pretty_print(self, name=None, display=True):

        def dfs_helper(node, label, graph):
            for c in node.children.keys():
                graph.add_edge(pydot.Edge(label, label + c))
                dfs_helper(node.children[c], label + c, graph)

        graph = pydot.Dot(graph_type='graph')
        for c in self.root.children.keys():
            graph.add_edge(pydot.Edge("ROOT", c))
            dfs_helper(self.root.children[c], c, graph)

        if name is None:
            fout = tempfile.NamedTemporaryFile(suffix=".png")
            name = fout.name
        else:
            name += "_trie.png"
        graph.write(name, format="png")
        if display:
            Image.open(name).show()

    def insert(self, string):
        p = self.root
        for i, c in enumerate(string):
            if c in p.children:
                p = p.children[c]
            else:
                break
        for j in range(i, len(string)):
            c = string[j]
            p.children[c] = Node()
            p = p.children[c]

    def search(self, string):
        p = self.root
        for c in string:
            if c in p.children:
                p = p.children[c]
            else:
                return False
        return True


def create_treeplots(textlist):
    for text in textlist:
        T = create_trie(text)
        T.pretty_print(text, False)


if __name__ == '__main__':
    # create_treeplots(["bbbd", "aabbabd", "ababcd", "abcbccd"])
    T = create_trie("aabbabbc")
    print(T.search("tki"))
    print(T.search("tkitek"))
    print(T.search("krotkitekst"))
    print(T.search("otko"))
    print(T.search("otkt"))
    T.pretty_print()
