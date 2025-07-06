class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

def print_tree(node, prefix="", is_last=True):
    """Recursively prints the tree structure starting from `node`."""
    # Print the current node with the prefix and the connector
    connector = "└── " if is_last else "├── "
    print(prefix + connector + str(node.value))

    # Determine the new prefix for child nodes
    new_prefix = prefix + ("    " if is_last else "│   ")

    # Iterate through children, marking the last one appropriately
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        is_last_child = (i == child_count - 1)
        print_tree(child, new_prefix, is_last_child)

# Example usage:
if __name__ == "__main__":
    # Create the root node
    root = TreeNode("Root")

    # Add some children
    child1 = TreeNode("Child 1")
    child2 = TreeNode("Child 2")
    child3 = TreeNode("Child 3")
    root.add_child(child1)
    root.add_child(child2)
    root.add_child(child3)

    # Add grandchildren
    child1.add_child(TreeNode("Child 1.1"))
    child1.add_child(TreeNode("Child 1.2"))
    child2.add_child(TreeNode("Child 2.1"))

    # Print the tree
    print_tree(root)