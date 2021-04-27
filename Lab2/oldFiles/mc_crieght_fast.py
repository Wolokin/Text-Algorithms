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
        new_node = Node([child.label[0], index])
        child.label[0] = index + 1
        new_node.connect(child, self.text[index + 1])
        node.connect(new_node, key)
        return new_node

    # def up_link_down(self, sibling):
    #     letters = queue()
    #     while (sibling and not sibling.link):
    #         letters.put(sibling.letter)
    #         sibling = sibling.parent
    #     if (not sibling):
    #         return (None, None)
    #     node = sibling.link
    #     while not letters.empty():
    #         current_letter = letters.get()
    #         if (node.child(current_letter)):
    #             node = node.child(current_letter)
    #             sibling = sibling.child(current_letter)
    #             sibling.link = node
    #         else:
    #             break
    #     return (node, sibling)

    def fast_find(self, i, node):
        if not self.text[i] in node.children:
            return (node, i)
        child = node.children[self.text[i]]
        m = len(self.text)
        if (m - i > child.length()):
            return self.fast_find(i + child.length(), child)
        elif (m - i == child.length()):
            return (child, i)
        else:
            return self.slow_find(i, node)

    # def left_to_right(text):
    #     root = Node("")
    #     leaf = graft(root, text)
    #     root.children()[0].link = root
    #     for i in range(1, len(text)):
    #         head, sibling = self.up_link_down(leaf)
    #         if (not head):
    #             sibling = root.child(text[i - 1])
    #             sibling.link = root
    #             head = root
    #         graft(head, text[i + head.depth:], sibling)

    # def slow_find(self, pattern, i, node):
    #     if not pattern[i] in node.children:
    #         return (node, i)
    #     key = pattern[i]
    #     child = node.children[key]
    #     start, end = child.label
    #     while start <= end:
    #         if pattern[i] != self.text[start]:
    #             return (self.split(node, key, start - child.label[0] - 1), i)
    #         i += 1
    #         start += 1
    #     return self.slow_find(pattern, i, child)

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
        for i in range(m):
            print(i)
            # pattern = self.text[i:]
            head, j = self.slow_find(i, self.root)
            leaf = head.connect(Node([j, m - 1]), self.text[j])
            # self.pretty_print()


if __name__ == '__main__':
    T = suffixTree("asdsd$")
    T.mc_creight()
    T.pretty_print()
    # with open("1997_714_head.txt", "r") as f:
    #     T = suffixTree(f.read()[:100] + "\0")
    #     T.mc_creight()
    #     T.pretty_print()
