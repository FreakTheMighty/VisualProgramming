
def input():
    for i in range(20):
        yield i
    
def add(a,b):
    return a + b

def subtract(a,b):
    return a - b


def output(a):
    output.gui.ui.plainTextEdit.setPlainText(str(a))
