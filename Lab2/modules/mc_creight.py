import pydot
import tempfile
from PIL import Image

ind = 0


class Node:

    def __init__(self, label):
        global ind
        self.ind = ind
        # print(ind)
        ind += 1
        self.label = label
        self.letter = None
        self.link = None
        self.parent = None
        self.children = dict()

    def connect(self, child, key):
        self.children[key] = child
        child.parent = self
        child.letter = key
        return child

    def length(self):
        return self.label[1] - self.label[0] + 1


class suffixTree:

    def __init__(self, text):
        self.text = text
        self.root = Node(None)
        self.root.parent = self.root
        self.root.link = self.root

    def pretty_print(self, name=None, display=True):

        def dfs_helper(node, graph):
            for c in node.children.values():
                graph.add_edge(
                    pydot.Edge(str(node.ind) + str(node.label),
                               str(c.ind) + str(c.label)))
                dfs_helper(c, graph)

        graph = pydot.Dot(graph_type='graph')
        for c in self.root.children.values():
            graph.add_edge(pydot.Edge("ROOT", str(c.ind) + str(c.label)))
            dfs_helper(c, graph)
        if name is None:
            fout = tempfile.NamedTemporaryFile(suffix=".png")
            name = fout.name
        else:
            name += "_tree.png"
        graph.write(name, format="png")
        if display:
            Image.open(name).show()

    def split(self, node, key, index):
        child = node.children[key]
        new_node = Node([child.label[0], index])
        child.label[0] = index + 1
        new_node.connect(child, self.text[index + 1])
        node.connect(new_node, key)
        return new_node

    def fast_find(self, i, j, node):
        # print("FAST")
        if i > j:
            return node
        child = node.children[self.text[i]]
        if (j - i + 1 > child.length()):
            return self.fast_find(i + child.length(), j, child)
        elif (j - i + 1 == child.length()):
            return child
        else:
            return self.split(node, self.text[i], child.label[0] + j - i)

    def slow_find(self, i, node):
        # print("SLOW")
        key = self.text[i]
        if key not in node.children:
            return (node, i)
        child = node.children[key]
        start, end = child.label
        while start <= end:
            if self.text[i] != self.text[start]:
                return (self.split(node, key, start - 1), i)
            i += 1
            start += 1
        return self.slow_find(i, child)

    def find(self, pattern, i, node):
        key = pattern[i]
        if key not in node.children:
            return False
        child = node.children[key]
        start, end = child.label
        while start <= end and i < len(pattern):
            if pattern[i] != self.text[start]:
                return False
            i += 1
            start += 1
        if i == len(pattern):
            return True
        return self.find(pattern, i, child)

    def mc_creight(self):
        m = len(self.text)
        last_head = head = self.root
        leaf = self.root.connect(Node([0, m - 1]), self.text[0])
        for i in range(1, m):
            p = last_head.label
            q = leaf.label
            if last_head == self.root:
                head, j = self.slow_find(q[0] + 1, self.root)
            else:
                u = last_head.parent
                if u == self.root:
                    v = self.fast_find(p[0] + 1, p[1], self.root)
                    j = q[0]
                else:
                    # print("LINK")
                    v = self.fast_find(p[0], p[1], u.link)
                    j = q[0]
                if len(v.children) == 1:
                    head = v
                else:
                    head, j = self.slow_find(q[0], v)
                last_head.link = v
            # print(j, m - 1)
            leaf = head.connect(Node([j, m - 1]), self.text[j])
            last_head = head
            self.pretty_print()

    def mc_creight_slow(self):
        m = len(self.text)
        for i in range(m):
            head, j = self.slow_find(i, self.root)
            head.connect(Node([j, m - 1]), self.text[j])


def suffixTreeFastWrapper(text):
    T = suffixTree(text)
    T.mc_creight()


def suffixTreeSlowWrapper(text):
    T = suffixTree(text)
    T.mc_creight_slow()


def create_treeplots(textlist):
    for text in textlist:
        global ind
        ind = 0
        T = suffixTree(text)
        T.mc_creight()
        T.pretty_print(text, False)


if __name__ == '__main__':
    #    create_treeplots(["bbbd", "aabbabd", "ababcd", "abcbccd"])
    with open("ustawa.txt", "r") as f:
        T = suffixTree("aabbabd" + "\0")
        T.mc_creight()
        T.pretty_print()
        print(T.find("dochodów2137", 0, T.root))
