import sys
import imp
import redis
import argparse

def parser():
    parser = argparse.ArgumentParser(description='Spawn an actor with inputs.')
    parser.add_argument('--search', dest='search',nargs="+",help='Search paths of module.')
    parser.add_argument('--channels', dest='channels',nargs="+",help='Search paths of module.')
    parser.add_argument('--module', dest='module',help='Name of module.')
    parser.add_argument('--cls', dest='cls',help='Class to import and run.')
    return parser.parse_args()


if __name__ == "__main__":
    args = parser()

    filedesc, filename, data = imp.find_module(args.module, args.search)
    module = imp.load_module(args.module,filedesc,filename,data)
    cls = getattr(module,args.cls)
    instance = cls(channels=args.channels)
    instance.listen()
