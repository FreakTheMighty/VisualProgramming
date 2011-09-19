import uuid
import redis
import pickle

class TaskNode(object):

    def __init__(self,channels=[], host="localhost",port=6379,nodeid=None):
        """TaskNode is meant to be subclassed.  An instance of that subclass will be run on the farm
        with its input and outputs defined by the isntance's location in the TaskGraph.  The forward definition
        of the nodeID with a UUID allows each Task in the graph to have full picture of the state of the rest of the 
        graph."""
        self.redis = redis.Redis(host=host,port=port)
        self.host = host
        self.port = port
        self.sub = self.redis.pubsub()
        self.inchannels = []

        self.sub.subscribe(self.inchannels)
        self.nodeID = uuid.uuid1() or nodeid
        self.name = self.__class__.__name__
        self.pos = (10,10)

        self._buffer = {}
        self._interface = []

    def __repr__(self):
        return "%s(channels=%s,host=%s,port=%s,nodeid=%s)" % (self.name,
                                                              repr(self.channels),
                                                              repr(self.port),
                                                              str(self.nodeID))

    def listen(self):
        for signal in self.sub.listen():
            key,name = signal['channel'].split("-")
            if name.isdigit():
                self._buffer[int(name)] = pickle.loads(signal['data'])
            else:
                self._buffer[name] = pickle.loads(signal['data'])
            interface = self.interface()
            interface.sort()
            curinterface = self._pos_buffer.keys()
            curinterface.sort()
            if interface == curinterface:
                break
        args = [self._buffer[val] for val in self._buffer if isintance(val,int)]
        kwargs = [self._buffer[val] for val in self._buffer if isintance(val,str)]
        self._buffer = {}
        return args,kwargs

    def talk(self,pub):
        self.redis.pub("something",pickle.dumps(pub))

    def go(self):
        args,kwargs = self.listen()
        results = self.run(*args,**kwargs)
        self.talk(results)

    def idToString(self):
        """Casts the uuid to a string."""
        return str(self.nodeID)

    def argCount(self):
        """Abstract method responsible for reporting the number available connections."""
        raise NotImplementedError

    def interface(self):
        return self._interface

    def run(self,*args,**kwargs):
        """Abstract method, represents the meat of the Task, executes code and produces results."""
        raise NotImplementedError
