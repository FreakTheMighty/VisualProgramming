import copy
import networkx
import CodeGraph

class Code(networkx.DiGraph):
    
    def __init__(self):
        networkx.DiGraph.__init__(self)
        self.groups = {}
        
    def add_func(self,node,group_name="__main__"): 
        node.name = CodeGraph.getUniqueNodeName(self, node.func_name)
        if group_name not in self.groups.keys():
            self.groups[group_name] = self.subgraph([])
        self.groups[group_name].add_node(node)
        self.add_node(node)
        node.imports = copy.copy(self.groups[group_name].nodes()[0].imports)
        
    def add_import(self,import_string,group="__main__"):
        group = self.groups[group]
        for node in group:
            node.add_import(import_string)
        