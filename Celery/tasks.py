import cPickle
import uuid

from celery.task import task
from celery.task.sets import subtask
from celery.task import Task

import redis
import TaskGraph

class NodeRunner(Task):
    
    Task.name = "WOOT"

    def __init__(self,name=None):
        self.redis = redis.Redis(host="localhost", port=6379)

    def run(self, graph, node, *args,**kwargs):
        """This function is called by celery."""

        positional,keyword = self.getResults(node)
        positional.extend(args)
        keyword.update(kwargs)
        result = node.func(*positional,**keyword)
        self.setResult(node,result)

        forExecution = self.checkDownStream(graph,node)
        for node in forExecution:
            task = NodeRunner()
            task.delay(graph,node)


