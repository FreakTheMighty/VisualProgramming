GUI = {}

def input(gui):
    for i in range(20):
        yield i
    
def add(gui,a,b):
    return a + b

def subtract(gui,a,b):
    return a - b


def output(gui,a):
    gui.textEdit.setPlainText(str(a))
