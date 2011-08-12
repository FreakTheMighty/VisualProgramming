from Nodes import Op

@Op
def add():
    while True:
        ctrl,args,kwargs = (yield)
        ctrl.broadcast(args[0]+args[1])

@Op
def sum():
    while True:
        ctrl,args,kwargs = (yield)
        ctrl.broadcast(args[0]+args[1])

def test():
    return 1
