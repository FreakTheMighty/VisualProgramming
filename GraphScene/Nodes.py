import subprocess
import os
import copy
import tempfile
import networkx

class Node(object):

    def __init__(self,name):
        self.name = name
        self.in_count = 1
        self.pos = (0,0)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s_%s" % (self.name, id(self))


def Op(f):
    def wrapped(*args,**kwargs):
        func = f(*args,**kwargs)
        func.next()
        op = Operator()
        op.op = func
        return op
    return wrapped

class OpInstance(object):

    def __init__(self,operator):
        self.operator = operator

    def __repr__(self):
        return "<%s object at %s>" % (self.operator().op.__name__,id(self))

class Operator(object):

    def __init__(self):
        self.arg_limit = None
        self.inputs = []
        self.outputs = []
        self.in_buffer = []
        self.op = None

    def __repr__(self):
        if self.op:
            return "<Operator object %s at %s>" % (self.op.__name__,id(self))
        else:
            return "<Operator object %s at %s>" % (None,id(self))



    def broadcast(self, val):
        for key, output in self.outputs:
            packet = Packet(key,val)
            output.send(packet)

    def send(self, val):

        try:
            val.key
        except AttributeError:
            val = Packet(*val)

        if len(self.in_buffer) < len(self.inputs):

            self.in_buffer.append(val)
            self.in_buffer.sort(key=lambda args: args.key)

            if len(self.in_buffer) == len(self.inputs):
                positional = filter(lambda arg: isinstance(arg.key,int), self.in_buffer)
                positional.sort()
                positional = [pos.val for pos in positional]
                keyword = filter(lambda arg: isinstance(arg.key,str), self.in_buffer)
                keyword_args = {}
                for arg in keyword:
                    keyword_args[arg.key]=arg.val
                self.op.send((self, positional,keyword_args))
                self.in_buffer = []

    def next(self):
        return self.op.next()

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
        self.tmp = tempfile.NamedTemporaryFile("w")
        self.interactive = False
        self.frame = networkx.MultiDiGraph()

    def refresh(self,launch=False):
        networkx.write_dot(self.frame,self.tmp.name+".dot")
        cmd = ["/Applications/Graphviz.app/Contents/MacOS/Graphviz",self.tmp.name+".dot"]
        if launch:
            subprocess.Popen(" ".join(cmd), shell=True)

    def add_edge(self, u, v, key=None, attr_dict=None, **attr):
        networkx.MultiDiGraph.add_edge(self, u, v, key=key, attr_dict=attr_dict, **attr)
        if self.interactive:
            self.refresh()

    def remove_edge(self, u, v, key=None):
        networkx.MultiDiGraph.remove_edge(self, u, v, key=key)
        if self.interactive:
            self.refresh()


    def updateFrame(self,local):
        for var in local:
            if local[var] in self:
                self.frame.add_node(var)

        for var in local:
            if local[var] in self:
                edges = self.in_edges(local[var])
                for edge in edges:
                    names = namestr(edge[0],local)
                    key = self.edge[edge[0]][edge[1]].keys()[0]
                    for name in names:
                        self.frame.add_edge(name,var,key)

        self.refresh()
