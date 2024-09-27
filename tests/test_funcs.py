# Hydrogen tests

import src.HydrogenLib
import src.HydrogenLib.Class.Namespace


def class_namespace_namespace_test(args):
    nsp = src.HydrogenLib.Class.Namespace.Namespace()
    for k in args:
        nsp.set(k, None)
    return list(nsp.keys())
