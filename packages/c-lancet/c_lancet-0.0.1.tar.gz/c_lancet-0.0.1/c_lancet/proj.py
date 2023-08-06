import os

from .utils import *


class CProj:
    def __init__(self, *, proj_path = None) -> None:
        self.proj_path = proj_path
        self.err = []
    
    def set_path(self, proj_path):
        if os.path.exists(proj_path):
            self.proj_path = proj_path
            return True
        return False
    
    def count_ext(self, ext = ['c', 'h', 'so']):
        """ count the number of different file extensions
        
        """

        if not os.path.exists(self.proj_path):
            self.err.append('Set correct proj_path by set_path(). ')
            return None
        
        res = defaultdict(int)
        for _r, _d, _fs in os.walk(self.proj_path):
            for _f in _fs:
                for _e in ext:
                    if _f.endswith('.' + _e):
                        res[_e] += 1
        return res
    
    def get_ext(self, ext: list) -> list:
        """ get all files with assigned extensions

        ext: a list containing file extensions, like ['c', 'h']
        
        """
        if not os.path.exists(self.proj_path):
            self.err.append('Set correct proj_path by set_path(). ')
            return None
        
        res = []
        for _r, _d, _fs in os.walk(self.proj_path):
            for _f in _fs:
                for _e in ext:
                    if _f.endswith('.' + _e):
                        res.append(os.path.join(_r, _f))
        return res
