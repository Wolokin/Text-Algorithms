import pydot
import tempfile
from PIL import Image

ind = 0


class Node:

    def __init__(self, label):
        global ind
        self.ind = ind
        ind += 1
        self.label = label
        self.children = dict()


class suffixTree:

    def __init__(self, text):
        self.text = text
        self.root = Node(None)

    def pretty_print(self, name=None):
        graph = pydot.Dot(graph_type='graph')
        for c in self.root.children.values():
            graph.add_edge(pydot.Edge("ROOT", str(c.ind) + str(c.label)))
            self.dfs_helper(c, graph)
        if name is None:
            fout = tempfile.NamedTemporaryFile(suffix=".png")
            name = fout.name
        graph.write(name, format="png")
        Image.open(name).show()

    def dfs_helper(self, node, graph):
        for c in node.children.values():
            graph.add_edge(
                pydot.Edge(str(node.ind) + str(node.label),
                           str(c.ind) + str(c.label)))
            self.dfs_helper(c, graph)

    def split(self, node, key, index):
        child = node.children[key]
        split_index = child.label[0] + index
        new_node = Node((child.label[0], split_index))
        child.label = (split_index + 1, child.label[1])
        new_node.children[self.text[split_index + 1]] = child
        node.children[key] = new_node
        return new_node

    def slow_find(self, pattern, i, node):
        if not pattern[i] in node.children:
            return (node, i)
        key = pattern[i]
        child = node.children[key]
        start, end = child.label
        while start <= end:
            if pattern[i] != self.text[start]:
                return (self.split(node, key, start - child.label[0] - 1), i)
            i += 1
            start += 1
        return self.slow_find(pattern, i, child)

    def mc_creight(self):
        m = len(self.text)
        for i in range(m):
            print(i)
            pattern = self.text[i:]
            head, j = self.slow_find(pattern, 0, self.root)
            head.children[pattern[j]] = Node((i + j, m - 1))
            # self.pretty_print()


if __name__ == '__main__':
    # T = suffixTree("aabbabbc")
    # T.mc_creight()
    # print(T.search("tki"))
    # print(T.search("tkitek"))
    # print(T.search("krotkitekst"))
    # print(T.search("otko"))
    # print(T.search("otkt"))
    # T.pretty_print()
    with open("1997_714_head.txt", "r") as f:
        T = suffixTree(f.read()[:100] + "\0")
        T.mc_creight()
        T.pretty_print()
