class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_children(self, node_id):
        self.children.append(node_id)


class Tree:
    def __init__(self):
        self.nodes = []

    def add_new_node(self, node_name):
        self.nodes.append(TreeNode(node_name))
        return len(self.nodes) - 1

    def add_children(self, node_id, child_node_id):
        self.nodes[node_id].add_children(child_node_id)

    def print_tree(self, node_id):
        lines = []
        lines.append(self.nodes[node_id].name)
        for i in range(len(self.nodes[node_id].children)):
            lines.extend(self.prepare_prev(self.print_tree(self.nodes[node_id].children[i]),
                                           i == len(self.nodes[node_id].children) - 1))
        return lines

    def prepare_prev(self, lines, last):
        lines = lines.copy()
        lines[0] = ('└── ' if last else '├── ') + lines[0]
        for line_number in range(1, len(lines)):
            lines[line_number] = ('    ' if last else '│   ') + lines[line_number]
        return lines

    def print_all(self):
        return '\n'.join(self.print_tree(len(self.nodes) - 3))