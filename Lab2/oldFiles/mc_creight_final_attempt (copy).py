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
        # self.root.parent = self.root

    def pretty_print(self, name=None):

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
        graph.write(name, format="png")
        Image.open(name).show()

    def split(self, node, key, index):
        child = node.children[key]
        new_node = Node([child.label[0], index])
        child.label[0] = index + 1
        new_node.connect(child, self.text[index + 1])
        node.connect(new_node, key)
        return new_node

    def fast_find(self, i, j, node):
        if not self.text[i] in node.children:
            return (node, i)
        child = node.children[self.text[i]]
        if (j - i > child.length()):
            return self.fast_find(i + child.length(), j, child)
        elif (j - i == child.length()):
            return (child, j)
        else:
            return (self.split(node, self.text[i], j), j)

    def slow_find(self, i, node):
        if not self.text[i] in node.children:
            return (node, i)
        key = self.text[i]
        child = node.children[key]
        start, end = child.label
        while start <= end:
            if self.text[i] != self.text[start]:
                return (self.split(node, key, start - 1), i)
            i += 1
            start += 1
        return self.slow_find(i, child)

    def mc_creight(self):
        m = len(self.text)
        last_head = head = self.root
        node = self.root
        leaf = self.root.connect(Node([0, m - 1]), self.text[0])
        for i in range(1, m):
            suffix_length = m - i
            if suffix_length <= leaf.length():
                head, j = self.slow_find(i, node)
                leaf = head.connect(Node([j, m - 1]), self.text[j])
                last_head = head
            else:
                if suffix_length <= leaf.length() + head.length() or not head.parent.link:
                    head, j = self.slow_find(i, node)
                    leaf = head.connect(Node([j, m - 1]), self.text[j])
                    last_head.link = head.parent
                    last_head = head
                else:
                    print(i)
                    self.pretty_print()
                    leaf_label = leaf.label
                    head_label = head.label
                    node = head.parent.link
                    node, j = self.fast_find(head_label[0], head_label[1], node)
                    if (len(node.children) == 1):
                        head = node
                    else:
                        head, j = self.slow_find(leaf_label[0], node)
                    leaf = head.connect(Node([j, m - 1]), self.text[j])
                    last_head.link = node
                    last_head = head
                    input()
                    self.pretty_print()
                    input()
        # for i in range(1, m):
        #     # suffix_length = m - i
        #     j = 0
        #     if last_head == self.root:
        #         last_head, j = self.slow_find(leaf.label[0] + 1, last_head)
        #         leaf = head.connect(Node([j, m - 1]), self.text[j])
        #         continue
        #     parent = last_head.parent
        #     if parent == self.root:
        #         link, j = self.fast_find(last_head.label[0] + 1, last_head.label[1], parent)
        #     else:
        #         link, j = self.fast_find(last_head.label[0], last_head.label[1], parent.link)
        #     if len(link.children) == 1:
        #         head = link
        #     else:
        #         head, j = self.slow_find(leaf.label[0], link)
        #     leaf = head.connect(Node([j, m - 1]), self.text[j])
        #     last_head.link = link
        #     last_head = head


if __name__ == '__main__':
    # T = suffixTree("abcabcabcabc$")
    # T.mc_creight()
    # T.pretty_print()
    with open("1997_714_head.txt", "r") as f:
        T = suffixTree(f.read()[:100] + "\0")
        T.mc_creight()
        T.pretty_print()
