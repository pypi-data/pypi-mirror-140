import os
from collections import defaultdict

from tree_sitter import Language, Parser


def get_parser():
    abs_path = os.path.abspath(__file__)
    dire = os.path.dirname(abs_path)
    C_LANGUAGE = Language(f'{dire}/tree-sitter.so', 'c')
    parser = Parser()
    parser.set_language(C_LANGUAGE)
    return parser


def get_tree(src: str):
    parser = get_parser()
    tree = parser.parse(bytes(src, 'utf8'))
    return tree


def get_cursor(src: str):
    parser = get_parser()
    tree = parser.parse(bytes(src, 'utf8'))
    return tree.walk()


def get_raw(s: str, start: tuple, end: tuple):
    """
    get raw text
    """
    lst = s.split('\n')
    s_row, s_col = start
    e_row, e_col = end

    if s_row > e_row or (s_row == e_row and s_col >= e_col):
        return None

    # potential bug: corresponding line does not have enough character
    if s_row == e_row:
        return lst[s_row][s_col:e_col]
    elif s_row + 1 == e_row:
        return lst[s_row][s_col:] +  '\n' + lst[e_row][:e_col]
    else:
        return lst[s_row][s_col:] \
                + '\n'.join(lst[s_row+1:e_row]) \
                + lst[e_row][:e_col]


def get_node_raw(s: str, node):
    return get_raw(s, node.start_point, node.end_point)


def find_node_by_type(cursor, node_type) -> list:
    """
    search node on tree according to node type 

    Args:
        cursor: cursor returned by tree.walk()
        node_type: a string or list of string indicating 
        node type, e.g. 'function_definition'

    Returns:
        a list containing the target nodes (they are in 
        tree-sitter build-in node type)

    """
    if type(node_type) == str:
        node_type = [node_type]

    node_lst = []
    while True:
        if cursor.node.type in node_type:
            node_lst.append(cursor.node)
        if not cursor.goto_first_child():
            while not cursor.goto_next_sibling():
                if not cursor.goto_parent():
                    return node_lst	


def find_node_by_field(cursor, field_name) -> list:
    """
    Search node on tree according to field_name. If node N
    is under the field_name field of some node, N will be collected.

    Args:
        cursor: cursor returned by tree.walk()
        field_name: a string or list of string indicating 
        field name. 

    Returns:
        a list containing the target nodes (they are in 
        tree-sitter build-in node type)

    """
    if type(field_name) == str:
        field_name = [field_name]

    node_lst = []
    while True:
        for _f in field_name:
            child = cursor.node.child_by_field_name(_f)
            if child:
                node_lst.append(child)
        if not cursor.goto_first_child():
            while not cursor.goto_next_sibling():
                if not cursor.goto_parent():
                    return node_lst