from GraphScene.Nodes import Signature

@Signature(0,1)
def add():
    while True:
        ctrl,args,kwargs = (yield)
        ctrl.broadcast(args[0]+args[1])

@Signature(0,1)
def sum():
    while True:
        ctrl,args,kwargs = (yield)
        ctrl.broadcast(args[0]+args[1])

@Signature(0,1)
def sumprint():
    while True:
        ctrl,args,kwargs = (yield)
        print args[0]+args[1]

def test():
    return 1
