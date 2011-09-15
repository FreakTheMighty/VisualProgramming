import os
import imp
import inspect

class Manager(object):

    def __init__(self):
        self.searchPaths = []
        self.classes = []

    def findPlugins(self):
        classes = []
        for path in self.searchPaths:
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith(".py"):
                        name = f.rstrip(".py")
                        fileObj, path, meta = imp.find_module(name,[root])
                        module = imp.load_module(name,fileObj,path,meta)
                        for attr in module.__dict__:
                            if inspect.isclass(module.__dict__[attr]):
                                cls = module.__dict__[attr]
                                if hasattr(cls,"NODE_TYPE"):
                                    classes.append(cls)

        self.classes = classes
        return classes

