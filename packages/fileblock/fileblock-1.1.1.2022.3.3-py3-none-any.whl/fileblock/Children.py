from random import random
import json

class Children(list):
    
    def to_json(self, path:str, file_only=False, dir_only=False, force_abspath=False, indent=None):
        '''
            file_only 和 dir_only 同时为 True 则 全都输出
        '''
        def convert(child):
            if type(child) == Children:
                res = []
                for c in child:
                    tmp = convert(c)
                    if tmp:
                        res.append(tmp)
                return res
            if file_only and not dir_only:
                if child.isfile:
                    return child.abstract(force_abspath).__dict__
            elif dir_only and not file_only:
                if child.isdir:
                    return child.abstract(force_abspath).__dict__
            else:
                return child.abstract(force_abspath).__dict__

        data = convert(self)
        with open(path, "w+", encoding="utf8") as f:
            json.dump(data, f, indent=indent)
        
    def unfold(self):
        def proc(children):
            if type(children[0]) == Children:
                tmp = Children()
                for child in children:
                    tmp += proc(child)
                return tmp
            return children
        res = proc(self)
        return res

    def get_path(self, force_abspath = False, file_only=False):
        return [child.abspath if force_abspath else child.path for child in self]

    @staticmethod
    def make(*child):
        def proc(children):
            if hasattr(children[0], "__iter__"):
                res = Children()
                for child in children:
                    res.append(proc(child))
                return res
            return Children(children)
        return proc(child)

    @property
    def abspaths(self):
        return [child.abspath for child in self]
    
    @property
    def shuffle(self):
        res = self.copy()
        index = []
        le = res.__len__()
        for i in range(1, le+1):
            idx = int(random() * (le - i))
            index.append(idx)
            res[idx], res[le - i] = res[le - i], res[idx]
        return res

    def __add__(self, x):
        return Children(super().__add__(x))

if __name__  == "__main__":

    c = Children([1, 2, 3])
    x = c + Children([2, 3, 4])
    print(x)
    