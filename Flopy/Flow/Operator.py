import inspect
import pickle
import redis
import uuid

RUN_CHANNEL="run"
CONTROL_CHANNEL="control"

IN_PORT="IN"
OUT_PORT="OUT"

class Empty(object):

    def __init__(self):
        self.empty = True

class Packet(object):

    def __init__(self, functionName,args,kwargs):
        self.functionName = functionName
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return "Packet(%s,%s,%s)"%(repr(self.functionName),repr(self.args),repr(self.kwargs))

    def pickleMe(self):
        return pickle.dumps(self)

class ProxyFunction(object):

    def __init__(self,node,funcname):
        self.node = node
        self.funcname=funcname

    def __call__(self,*args,**kwargs):
        packet = Packet(self.funcname,args,kwargs)
        return self.node.communicate(packet)

class ProxyNode(object):

    def __init__(self,host="localhost",port=6379,nodeId=None):
        self.host = host
        self.port = port
        self.nodeId = nodeId
        self.redis = redis.Redis(host=host,port=port)
        self.sub = self.redis.pubsub()

        self.sub.subscribe(str(self.nodeId))

        listAttrPacket = Packet("_listAttrs",[],{})
        self.proxyfuncs, self.proxyattrs = self.communicate(listAttrPacket)

        for func in self.proxyfuncs:
            if not func.startswith("__"):
                setattr(self,func,ProxyFunction(self,func))

    def communicate(self,packet):
        self.redis.publish("node.control::"+str(self.nodeId),packet.pickleMe())
        result = self.sub.listen().next()
        return pickle.loads(result['data'])

    def connect(self,port,node):
        self.communicate(Packet("subscribe",[port,node.nodeIdToString()],{}))

class TaskNode(object):

    INTERFACE=[]

    def __init__(self,host="localhost",port=6379,nodeId=None):
        """TaskNode is meant to be subclassed.  An instance of that subclass will be run on the farm
        with its input and outputs defined by the isntance's location in the TaskGraph.  The forward definition
        of the nodeID with a UUID allows each Task in the graph to have full picture of the state of the rest of the 
        graph."""
        self.INTERFACE.sort()
        self.redis = redis.Redis(host=host,port=port)
        self.host = host
        self.port = port
        self.sub = self.redis.pubsub()

        if nodeId:
            self.nodeId = nodeId
        else:
            self.nodeId = uuid.uuid1()
        self.name = self.__class__.__name__
        self.pos = (10,10)

        
        self._channelToValueMap = {}
        self._portToChannelConnections = dict([(key,None) for key in self.INTERFACE])

        self.sub.subscribe(["node.control::"+str(self.nodeId)])
        self._close = False

        self.currentChannel = None
        self.currentResult = None

    def __repr__(self):
        return "%s(host=%s,port=%s,nodeId=%s)" % (self.name,
                                                  repr(self.host),
                                                  repr(self.port),
                                                  repr(str(self.nodeId)))


    def _listAttrs(self):
        functionList = []
        attrList = []
        for attr in dir(self):
            if inspect.ismethod(getattr(self,attr)):
                    functionList.append(attr)
            else:
                attrList.append(attr)
        return functionList,attrList

    def getPorts(self):
        return self.INTERFACE

    def subscribe(self,port,channel):
        """Setup node to listen on a channel and map that channel key in the flow buffer"""
        self.sub.subscribe(channel)
        self._portToChannelConnections[port] = channel

    def flowFull(self):
        """Returns True all of the Empty objects have been replaced with arguments to be applied to the 
        run function."""
        receivedChannels = self._channelToValueMap.keys()
        receivedChannels.sort()

        subscribed = self._portToChannelConnections.values()
        subscribed.sort()

        return  receivedChannels == subscribed

    def flow(self,arg):
        """Updates flow buffer until the INTERFACE has been satisfied, then applies
        the buffer to the run function as specified in the interface."""
        self._channelToValueMap[self.currentChannel] = arg
        if self.flowFull():
            posargs = [self._channelToValueMap[self._portToChannelConnections[val]]\
                       for val in self.INTERFACE if isinstance(val,int)]
            kwargs = [(val,self._channelToValueMap[self._portToChannelConnections[val]])\
                        for val in self.INTERFACE if isinstance(val,str)]
            result = self.run(*posargs,**dict(kwargs))
            self._channelToValueMap = {}
            return result

    def listen(self):
        """Listen for the signal - parse out the function to be called for the given signal
        and apply the args passed along in the data."""
        for signal in self.sub.listen():
            self.currentChannel = signal['channel']
            data = signal['data']
            packet = pickle.loads(data)
            func = getattr(self,packet.functionName)
            result = func(*packet.args,**packet.kwargs)
            self.currentResult = result
            return self.talk(str(self.nodeId),result)
    
    def getResult(self):
        return self.currentResult

    def nodeIdToString(self):
        return str(self.nodeId)

    def talk(self,channel, pub):
        self.redis.publish(channel,pickle.dumps(pub))

    def go(self):
        while True and not self._close:
            try:
                self.listen()
            except TypeError,e:
                print e
            except AttributeError,e:
                print e

    def close(self):
        self._close = True

    def idToString(self):
        """Casts the uuid to a string."""
        return str(self.nodeId)

    def run(self,*args,**kwargs):
        """Abstract method, represents the meat of the Task, executes code and produces results."""
        raise NotImplementedError
