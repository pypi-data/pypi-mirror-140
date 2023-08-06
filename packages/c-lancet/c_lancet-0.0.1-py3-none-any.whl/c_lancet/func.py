from .utils import *


class CFunc:
    def __init__(self, *, src = None) -> None:
        self.name = None
        self.para = None
        self.type = None
        self.src = src

        if self.src:
            self.func_sig()

    def set_src(self, src: str):
        self.src = src
        if src:
            self.func_sig()

    def func_sig(self):
        # analyse function signature
        cursor = get_cursor(self.src)
        if not cursor.goto_first_child() or cursor.node.type != 'function_definition':
            return
 
        type_node = cursor.node.child_by_field_name('type')
        # self.type = get_node_raw(self.src, type_node)
        self.type = get_raw(self.src, cursor.node.start_point, type_node.end_point)

        declarator_node = cursor.node.child_by_field_name('declarator')
        while declarator_node.type == 'pointer_declarator':
            self.type = self.type + ' *'
            declarator_node = declarator_node.child_by_field_name('declarator') 

        name_node = declarator_node.child_by_field_name('declarator')
        self.name = get_node_raw(self.src, name_node)

        paras_node = declarator_node.child_by_field_name('parameters')
        self.para = []

        if paras_node:
            for _para in paras_node.children:
                if _para.type in [',', '(', ')']:
                    continue
                if _para.type == 'variadic_parameter':
                    self.para.append(['...', '...'])
                    continue
                if _para.type == 'parameter_declaration':
                    id = find_node_by_type(_para.walk(), 'identifier')
                    if not id:
                        continue
                    id = id[-1]
                    type = get_raw(self.src, _para.start_point, id.start_point).strip()
                    self.para.append([type, get_node_raw(self.src, id)])

    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.type
    
    def get_para(self) -> list:
        return self.para