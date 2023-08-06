conversions = []

#%% NexworkX graph

try:
    import networkx as nx

    nx_type = nx.classes.graph.Graph
    nx_di_type = nx.classes.digraph.DiGraph

    def nx_to(G):
        string = ""
        for line in nx.generate_graphml(G):
            string += line + "\n"
        return string

    def nx_from(string):
        return nx.parse_graphml(string)

    conversions.append((nx_type, nx_to, nx_from))
    conversions.append((nx_di_type, nx_to, nx_from))
except:
    pass

#%% List


def list_to(l):
    d = {}
    for i in range(len(l)):
        d[str(i)] = l[i]
    return d


def list_from(d):
    l = []
    for i in range(len(d)):
        l.append(d[str(i)])
    return l


conversions.append((list, list_to, list_from))
#%% Tuple


def tuple_to(t):
    return list_to(t)


def tuple_from(d):
    return tuple(list_from(d))


conversions.append((tuple, tuple_to, tuple_from))
#%% Nonetype


def none_to(*_):
    return "None"


def none_from(*_):
    return None


#%% Numpy random number generator

try:
    import numpy as np
    import pickle
    import base64

    rng_type = np.random.Generator

    def get_state(rng):
        return base64.encodebytes(pickle.dumps(rng)).decode("utf-8")

    def set_state(rng_bin):
        return pickle.loads(base64.decodebytes(rng_bin.encode("utf-8")))

    conversions.append((rng_type, get_state, set_state))
except:
    pass

conversions.append([type(None), none_to, none_from])
#%% datetime object
from datetime import datetime


def date_to(d):
    return datetime.timestamp(d)


def date_from(ts):
    return datetime.fromtimestamp(ts)


conversions.append((datetime, date_to, date_from))

#%% Fallback modes conversions
import pickle


def pickle_to(data):
    return pickle.dumps(data, protocol=0)


def pickle_from(data):
    return pickle.loads(data)


conversions.append(("representation", format, lambda x: x))
# conversions.append(("pickle", pickle.dumps, pickle.loads))
# Pickle is not safe, will only use it if user directly select it for fallback
