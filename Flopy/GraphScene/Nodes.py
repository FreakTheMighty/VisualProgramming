import copy
import glob
import json
import os
import subprocess
import sys
import tempfile
import yaml

import networkx

def Signature(*args):

    def inner_sig(f):

        def wrapped(*wargs,**wkwargs):
            func = f(*wargs,**wkwargs)
            func.next()
            op = Operator()
            op.operator = func
            op.name = func.__name__
            op.cls = func.__name__
            op.args = args
            return op

        return wrapped

    return inner_sig

class Node(object):

    def __init__(self):
        self.woot = []

    def engine(self, manager, *args, **kwargs):
        raise NotImplementedError

    
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
        self.cls = None
        self.manager = None

    def __repr__(self):
        if self.operator:
            return "<Operator object %s at %s>" % (self.operator.__name__,id(self))
        else:
            return "<Operator object %s at %s>" % (None,id(self))

    def argCount(self):
        return len(self.args)

    def data(self):
        return self.manager.instance(self)

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



class ProjectManager(object):

    def __init__(self, projectPath=None):
        self.projectPath = None
        self.setProject(projectPath)

    def setProject(self,projectPath):
        self.projectPath = os.path.abspath(projectPath)
        if self.projectPath not in sys.path:
            sys.path.append(os.path.join(self.projectPath,"Nodes"))


class DataManager(object):

    def __init__(self, project):
        self.project = project
        self.templates = {}
        self.instances = {}
        self.setProject(project)

    def setProject(self,project):
        self.project = project
        templateFiles = glob.glob(os.path.join(project.projectPath,"DataTemplates","*.json"))
        names = [os.path.basename(os.path.splitext(t)[0]) for t in templateFiles]
        for idx, template in enumerate(templateFiles):
            data = json.load(open(os.path.join(self.project.projectPath,"DataTemplates",template)))
            self.templates[names[idx]] = data

    def register(self,*nodes):
        for node in nodes:
            node.manager = self
            dataPath = os.path.join(self.project.projectPath,"Data",node.name)
            if os.path.exists(dataPath):
                data = json.load(open(dataPath))
            else:
                data = copy.copy(self.templates[node.cls])
            self.instances[node] = data

    def instance(self,node):
        return self.instances[node]

