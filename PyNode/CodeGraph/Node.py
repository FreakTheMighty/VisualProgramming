import CodeGraph

class Function(object):

    def __init__(self, func_name):
        self.func_name = func_name
        self.name = func_name
        self.imports = []
        
    def add_import(self,module):
        self.imports.append(module)
        self.imports = list(set(self.imports))
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.func_name + "_%s" % id(self)
    
    @property
    def func(self):
        local_vars = locals()
        for i in self.imports:
            local_vars[i] = __import__(i)
        return eval(self.func_name,globals(),local_vars)
