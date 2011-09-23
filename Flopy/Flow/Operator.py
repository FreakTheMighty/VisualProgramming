import uuid
import redis
import pickle

RUN_CHANNEL="run"
CONTROL_CHANNEL="control"

class TaskNode(object):

    INTERFACE=[]

    def __init__(self,channels=[], host="localhost",port=6379,nodeid=None):
        """TaskNode is meant to be subclassed.  An instance of that subclass will be run on the farm
        with its input and outputs defined by the isntance's location in the TaskGraph.  The forward definition
        of the nodeID with a UUID allows each Task in the graph to have full picture of the state of the rest of the 
        graph."""
        self.INTERFACE.sort()
        self.redis = redis.Redis(host=host,port=port)
        self.host = host
        self.port = port
        self.sub = self.redis.pubsub()
        self.inchannels = []

        self.nodeId = uuid.uuid1() or nodeid
        self.name = self.__class__.__name__
        self.pos = (10,10)

        self._buffer = {}
        self._buffer = dict(zip(channels,self.INTERFACE))
        self.channels = channels
        self.channels.append("control::%s"%str(self.nodeId))
        self.subscribe()
        self._close = False

    def __repr__(self):
        return "%s(channels=%s,host=%s,port=%s,nodeid=%s)" % (self.name,
                                                              repr(self.channels),
                                                              repr(self.host),
                                                              repr(self.port),
                                                              repr(str(self.nodeId)))

    def subscribe(self):
        print self.channels
        self.sub.subscribe(self.channels)

    def listen(self):
        args = {}
        for signal in self.sub.listen():
            channel = signal['channel']
            data = signal['data']
            channelType, sourceNode = channel.split("::")
            if channelType == CONTROL_CHANNEL:
                func = getattr(self,data)
                func()
                return None,None
            else:
                arg = self._buffer[channel]
                args[arg] = pickle.loads(data)
                if args.keys() == self.INTERFACE:
                    break
                posargs = [args[val] for val in self.INTERFACE if isinstance(val,int)]
                kwargs = [(val,args[val]) for val in self.INTERFACE if isinstance(val,str)]
                return posargs,dict(kwargs)

    def close(self):
        self._close = True

    def talk(self,pub):
        self.redis.publish("run::%s" % str(self.nodeId),pickle.dumps(pub))

    def go(self):
        self.subscribe()
        while True:
            try:
                #Flush the pipe
                args, kwargs = self.listen()
                if self._close:
                    return
                try:
                    results = self.run(*args,**kwargs)
                except Exception, e:
                    results = e
                self.talk(results)
            except Exception:
                pass

    def idToString(self):
        """Casts the uuid to a string."""
        return str(self.nodeId)

    def run(self,*args,**kwargs):
        """Abstract method, represents the meat of the Task, executes code and produces results."""
        raise NotImplementedError
