import pydot
import tempfile
from PIL import Image


class PrettyPrint:
    '''Base class for printing trees using pydot's write method
    Tree node needs to have 'left' and 'right' attributes'''

    def __init__(self):
        self.root = None

    def pretty_print(self, name=None, display=True):
        '''Prints a tree as an image\n
        name - if provided, saves tree image to that filename,
        display - wheter to display the image'''

        def dfs_helper(node, graph):
            for c in [node.left, node.right]:
                if c:
                    graph.add_edge(pydot.Edge(str(node), str(c)))
                    dfs_helper(c, graph)

        if self.root is None:
            print("Root is None!")
            return

        graph = pydot.Dot(graph_type='graph')
        dfs_helper(self.root, graph)
        if name is None:
            fout = tempfile.NamedTemporaryFile(suffix=".png")
            name = fout.name
        else:
            name += "_tree.png"
        graph.write(name, format="png")
        if display:
            Image.open(name).show()
