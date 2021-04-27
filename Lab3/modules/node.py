class Node:
    node_count = 0

    def __init__(self, label=None, weight=None, left=None, right=None):
        self.ind = Node.node_count
        Node.node_count += 1
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
