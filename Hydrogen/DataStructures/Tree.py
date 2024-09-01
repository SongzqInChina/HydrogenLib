class Node:
    def __init__(self, data, next=None, parent=None):
        self.data = data
        self.children = [next] if next else []
        self.parent = parent

    def add_child(self, node):
        self.children.append(node)

    def remove_child(self, node):
        self.children.remove(node)

    def index(self, node):
        return self.children.index(node)

    def __eq__(self, other):
        return self.data == other.info

    def __str__(self):
        return f"TreeNode: data={self.data}, children_count={len(self.children)}"


class Tree:
    def __init__(self, root=None):
        self.root = root

    def dfs(self, node=None):
        """Depth-first search traversal."""
        if node is None:
            node = self.root
        yield node
        for child in node.children:
            yield from self.dfs(child)

    def bfs(self):
        """Breadth-first search traversal."""
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            yield node
            queue.extend(node.children)

    def find_node(self, data):
        """Find a node by its data."""
        for node in self.dfs():
            if node.data == data:
                return node
        return None
