import os

from .utils import *
from .func import *


class CFile:
    def __init__(self, *, file_path = None) -> None:
        # file attr
        self.file_path = file_path
        self.file_content = None
        # functionality 
        self.func_lst = None
        # error report 
        self.err = []
    
    def set_path(self, file_path: str) -> bool:
        if os.path.exists(file_path):
            self.file_path = file_path
            return True
        return False
    
    def get_err(self) -> list:
        err = list(self.err)
        self.err = []
        return err

    def get_func(self):
        """ Get all functions in current file

        return list for success or None for failure
        """

        if self.func_lst != None:
            return self.func_lst

        if self.file_path == None:
            self.err.append('Add file path by set_path() first. ')
            return None

        if self.file_content == None:
            with open(self.file_path, 'r') as r:
                self.file_content = r.read()
        
        self.func_lst = []
        cursor = get_cursor(self.file_content)
        for _f in find_node_by_type(cursor, 'function_definition'):
            self.func_lst.append(CFunc(src = get_node_raw(self.file_content, _f)))
        
        return self.func_lst
