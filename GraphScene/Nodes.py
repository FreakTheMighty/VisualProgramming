import subprocess
import os
import copy
import tempfile

import networkx
import json

class Node(object):

    def __init__(self,op):
        self.operator = op
        self.name = self.operator().operator.__name__
        self.pos = (0,0)

    def argCount(self):
        return len(self.operator().args)
    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s object at %s>" % (self.operator().operator.__name__,id(self))


def Signature(*args):

    def inner_sig(f):

        def wrapped(*wargs,**wkwargs):
            func = f(*wargs,**wkwargs)
            func.next()
            op = Operator()
            op.operator = func
            op.name = func.__name__
            op.args = args
            return op

        return wrapped

    return inner_sig

class Operator(object):

    def __init__(self):

        self.pos = (0,0)
        self.graph = None
        self.arg = []

        self.inputs = []
        self.outputs = []

        #In buffer needs to be filled before the next message is broadcast
        self.in_buffer = []

        self.operator = None
        self.name = None

    def __repr__(self):
        if self.operator:
            return "<Operator object %s at %s>" % (self.operator.__name__,id(self))
        else:
            return "<Operator object %s at %s>" % (None,id(self))

    def argCount(self):
        return len(self.args)

    def broadcast(self, val):
        for u, out in self.graph.out_edges():
            key = self.graph.edge[u][out].keys()[0]
            packet = Packet(key,val)
            out.send(packet)

    def send(self, val):

        try:
            val.key
        except AttributeError:
            val = Packet(*val)

        if len(self.in_buffer) < len(self.args):

            self.in_buffer.append(val)
            self.in_buffer.sort(key=lambda args: args.key)

            if len(self.in_buffer) == len(self.args):
                positional = filter(lambda arg: isinstance(arg.key,int), self.in_buffer)
                positional.sort()
                positional = [pos.val for pos in positional]
                keyword = filter(lambda arg: isinstance(arg.key,str), self.in_buffer)
                keyword_args = {}
                for arg in keyword:
                    keyword_args[arg.key]=arg.val
                self.operator.send((self, positional,keyword_args))
                self.in_buffer = []

    def next(self):
        return self.operator.next()

class Packet(object):

    def __init__(self,key,val):
        self.key = key
        self.val = val

    def __repr__(self):
        return "Packet(%s,%s)" % (self.key,self.val)

    def __str__(self):
        return str(self.val)

def connect(operator1,operator2,key):
    if operator2.arg_limit:
        if len(operator2.inputs) < operator2.arg_count:
            operator2.inputs.append(operator1)
            operator1.outputs.append((key,operator2))
    else:
        operator2.inputs.append(operator1)
        operator1.outputs.append((key,operator2))

def disconnect(operator1,operator2,key):
    if (key, operator1) in operator2.outputs:
        operator2.outputs.remove((key,operator1))
    elif operator1 in operator2.inputs:
        operator2.inputs.remove(operator1)

    if (key,operator2)in operator1.outputs:
        operator1.outputs.remove((key,operator2))
    elif operator2 in operator1.inputs:
        operator1.inputs.remove(operator2)

def drawdotgraph(graph):
    tmp = tempfile.NamedTemporaryFile("w")
    networkx.write_dot(graph,tmp.name+".dot")
    cmd = ["/Applications/Graphviz.app/Contents/MacOS/Graphviz",tmp.name+".dot"]

    subprocess.Popen(cmd)

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

class CodeGraph(networkx.MultiDiGraph):

    def __init__(self):
        networkx.MultiDiGraph.__init__(self)
        self.frame = networkx.MultiDiGraph()

    def add_node(self,node):
        node.graph = self
        self.makeUniqueName(node)
        networkx.MultiDiGraph.add_node(self,node)

    def makeUniqueName(self,node):
        names = [n.name for n in self.nodes()]
        partitioned_names = [n.rpartition("_") for n in names]
        if node.name in names and node not in self.nodes():

            #Sort filter and sort the existing nodes.
            #  Filter by matching node names
            #  Sort by trailing number
            indexed = filter(lambda n: n[0] == node.name, partitioned_names)
            indexed = sorted(indexed,key=lambda k: k[-1])
            if len(indexed):
                next_idx =  str(int(indexed[0][-1])+1)
                name = node.name.rpartition("_")
                if name[-1].isdigit():
                    node.name = "".join(name)
                    return
                else:
                    node.name = node.name + "_" + next_idx
                    return
            else:
                node.name = node.name+"_1"

    def add_edge(self, u, v, key=None, attr_dict=None, **attr):
        self.add_node(u)
        self.add_node(v)
        networkx.MultiDiGraph.add_edge(self, u, v, key=key, attr_dict=attr_dict, **attr)




class ConfigManager(object):

    def __init__(self,path):
        self.project = path
        self.config = json.load(open(os.path.join(path,"configs","bind.json")))
        self.configMap = {}
        self.loadConfigs()

    def loadConfigs(self):
        for operator, config in self.config:
            self.configMap[operator] =json.load(open(os.path.join(self.project,"configs",config)))

    def registerNode(self,node):
        node.name
