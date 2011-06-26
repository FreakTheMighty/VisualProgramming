import networkx


def getUniqueNodeName(graph, basename):
    """Given a base name the function returns a unique version by appending "_%02d"
    """
    nodes = [node.name.split("_") for node in graph.nodes() if node.name.startswith(basename)]
    if nodes:
        nodes.sort()
        padding = "".join(["%","0",str(len(nodes[-1][1])),"d"])
        number = int(nodes[-1][1])
    else:
        padding = "%02d"
        number = 0
        
    return basename + "_" + padding % (number+1)


def generatorWrapper(node,split,gui,*args):
    if split < 1:
        split = 1
    
    #print args
    if args:
        for arg in itertools.izip(*args):
            for s in range(split):
                yield node.func(gui,*arg)
    else:
        for val in node.func(gui):
            for s in range(split):
                yield val
