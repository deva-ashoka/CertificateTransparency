import hashlib
from datetime import datetime
import csv
import os
import math
import graphviz as gv

children_dict = {}


class Node(object):
    def __init__(self):
        self.leftchild = None
        self.rightchild = None
        self.parent = None
        self.value = None
        self.timestamp = None


class Leaf_Hash_Node(object):
    def __init__(self):
        self.child = None
        self.parent = None
        self.value = None


class Leaf_Node(object):
    def __init__(self):
        self.child = None
        self.parent = None
        self.value = None
        self.timestamp = None


class Merkle_Tree(object):

    def __init__(self):
        self.size = 0
        self.root = None

    def get_leaf_hash_node(self, n, time_stamp):
        leaf_hash_node = Leaf_Hash_Node()
        leaf_node = Leaf_Node()
        leaf_node.value = n
        leaf_node.timestamp = time_stamp
        leaf_node.parent = leaf_hash_node
        leaf_hash_node.child = leaf_node

        init_string = "0x00"
        full_string = init_string + n
        full_string_bytes = str.encode(full_string)
        hash_object = hashlib.sha256(full_string_bytes)
        hex_dig = hash_object.hexdigest()
        leaf_hash_node.value = hex_dig

        return leaf_hash_node

    def get_last_node(self):
        root = self.root
        try:
            while root.rightchild is not None:
                root = root.rightchild
            return root
        except AttributeError as e:
            return root.parent

    def get_left_right_depth(self, node):
        left = 0
        right = 0
        temp = node
        while hasattr(temp, 'leftchild'):
            temp = temp.leftchild
            left += 1
        temp = node
        while hasattr(temp, 'rightchild'):
            temp = temp.rightchild
            right += 1
        return left, right

    def calculate_hash(self, added_node, time_stamp):
        init_string = "0x01"
        middle_string = added_node.leftchild.value
        last_string = added_node.rightchild.value
        full_string = init_string + middle_string + last_string
        hash_object = hashlib.sha256(str.encode(full_string))
        hex_dig = hash_object.hexdigest()
        added_node.value = hex_dig

        if added_node == self.root:
            added_node.timestamp = time_stamp

    def is_tree_full(self):
        n = self.size
        return n > 0 and (n & (n - 1)) == 0

    def get_sibling(self, node):
        if node.parent.leftchild == node:
            return node.parent.rightchild
        if node.parent.rightchild == node:
            return node.parent.leftchild

    def locate_node(self, index, start_node, tree_size):

        if tree_size <= 2:
            if index == 1:
                if hasattr(start_node, 'leftchild'):
                    return start_node.leftchild.child
                else:
                    return start_node.child
            else:
                return start_node.rightchild.child

        r = math.ceil(math.log(tree_size, 2) - 1)
        k = int(math.pow(2, r))
        if index > k:
            start_node = start_node.rightchild
            tree_size = tree_size - k
            index = index - k
        else:
            start_node = start_node.leftchild
            tree_size = k

        return self.locate_node(index, start_node, tree_size)

    def get_audit_path(self, index):
        audit_path = []

        leaf = self.locate_node(index, self.root, self.size)
        node = leaf.parent

        while node.parent is not None:
            sibling = self.get_sibling(node)
            if sibling is not None:
                audit_path.append(sibling.value)
            node = node.parent

        return leaf, audit_path

    def add_element(self, n, time_stamp):
        leaf_hash_node = self.get_leaf_hash_node(n, time_stamp)

        if self.size == 0:
            self.root = Node()
            self.root.leftchild = leaf_hash_node
            leaf_hash_node.parent = self.root
            self.root.value = leaf_hash_node.value

        else:

            if self.size % 2 == 1:

                add_to_node = self.get_last_node()

                if add_to_node.rightchild is None:
                    add_to_node.rightchild = leaf_hash_node
                    leaf_hash_node.parent = add_to_node
                    self.calculate_hash(add_to_node, time_stamp)

                else:
                    temp = add_to_node.rightchild
                    parent_node = Node()
                    parent_node.leftchild = temp
                    temp.parent = parent_node
                    parent_node.rightchild = leaf_hash_node
                    leaf_hash_node.parent = parent_node
                    parent_node.parent = add_to_node
                    add_to_node.rightchild = parent_node
                    while parent_node is not None:
                        self.calculate_hash(parent_node, time_stamp)
                        parent_node = parent_node.parent

            elif self.size % 2 == 0:

                if self.is_tree_full():
                    temp = self.root
                    self.root = Node()
                    self.root.leftchild = temp
                    temp.parent = self.root
                    self.root.rightchild = leaf_hash_node
                    leaf_hash_node.parent = self.root
                    self.calculate_hash(self.root, time_stamp)

                else:
                    temp = self.root
                    left_depth, right_depth = self.get_left_right_depth(temp)
                    while left_depth != right_depth:
                        temp = temp.rightchild
                        left_depth, right_depth = self.get_left_right_depth(temp)

                    parent_node = Node()
                    parent_node.parent = temp.parent
                    temp.parent.rightchild = parent_node

                    parent_node.leftchild = temp
                    temp.parent = parent_node
                    parent_node.rightchild = leaf_hash_node
                    leaf_hash_node.parent = parent_node

                    while parent_node is not None:
                        self.calculate_hash(parent_node, time_stamp)
                        parent_node = parent_node.parent

        self.size += 1

        leaf = leaf_hash_node.child

        leaf_node_info = {
            'LeafValue': leaf.value,
            'LeafHash': leaf_hash_node.value,
            'Index': self.size,
            'TimeStamp': time_stamp
        }

        return leaf_node_info


def print_in_order(root):
    if root:
        if hasattr(root, 'leftchild'):
            print_in_order(root.leftchild)
        else:
            print_in_order(root.child)
        if isinstance(root, Leaf_Node):
            print("Leaf:" + root.value)
        if isinstance(root, Leaf_Hash_Node):
            print("Leaf Hash:" + root.value)
        if isinstance(root, Node):
            print("Hash:" + root.value)
        if hasattr(root, 'rightchild'):
            print_in_order(root.rightchild)


def write_to_csv(write_info, csv_file_path):
    fieldnames = write_info.keys()
    file_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, 'a+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        writer.writerow(write_info)

    csvfile.close()


m_tree = Merkle_Tree()


def short(string):
    if len(string) > 5:
        string = string[:5]
    return string


def create_graph(root):
    global children_dict
    if root:
        if hasattr(root, 'leftchild'):
            create_graph(root.leftchild)
        else:
            create_graph(root.child)
        if isinstance(root, Leaf_Hash_Node):
            children_dict[short(root.value)] = [short(root.child.value)]
        if isinstance(root, Node):
            if root.rightchild is not None:
                children_dict[short(root.value)] = [short(root.leftchild.value), short(root.rightchild.value)]
            else:
                children_dict[short(root.value)] = [short(root.leftchild.value)]
        if hasattr(root, 'rightchild'):
            create_graph(root.rightchild)


def visualize_tree(m_tree):
    global children_dict
    create_graph(m_tree.root)

    graph = gv.Graph(format='svg')

    all_nodes = list(children_dict.keys())

    temp = []

    for node_str in all_nodes:
        children = children_dict.get(node_str)
        for child in children:
            if child not in all_nodes:
                temp.append(child)

    all_nodes.extend(temp)

    for node_str in all_nodes:
        graph.node(node_str)
        children = children_dict.get(node_str)
        if children is not None:
            for child in children:
                graph.edge(node_str, child)

    graph.render('graph')

    children_dict = {}


while 1 == 1:
    input_string = str(input("Enter command: "))

    if input_string == "exit":
        break

    command = input_string.split(' ')[0]

    if command == "audit":
        index = int(input_string.split(' ')[1])
        leaf, audit_path = m_tree.get_audit_path(index)
        print("Leaf Value: " + leaf.value)
        print("Audit Path: " + str(audit_path))

    if command == "add":
        input_array = (input_string.split(' ')[1]).split(',')
        time_stamp = datetime.now()
        added_nodes_info = []
        for element in input_array:
            node_info = m_tree.add_element(element, time_stamp)
            added_nodes_info.append(node_info)

        print_in_order(m_tree.root)
        print("------------------------------------------------------------")
        print("MTH: " + m_tree.root.value + " " + str(m_tree.root.timestamp))
        print("------------------------------------------------------------")

        visualize_tree(m_tree)

        for node_info in added_nodes_info:
            node_info['TreeHash'] = m_tree.root.value
            leaf, audit_path = m_tree.get_audit_path(node_info['Index'])
            audit_path_string = ""
            for element in audit_path:
                audit_path_string += element + "-"
            if audit_path_string != "":
                audit_path_string = audit_path_string[:-1]
            node_info['AuditPath'] = str(audit_path_string)

            write_to_csv(node_info, 'log.csv')
