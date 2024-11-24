# Hydrogen tests

import src.hydrolib
import src.hydrolib.utils.Auto
import src.hydrolib.utils.Namespace


def class_namespace_namespace_test(args):
    nsp = src.HydrogenLib.Class.Namespace.Namespace()
    for k in args:
        nsp.set(k, None)
    return list(nsp.keys())


def class_auto_autos_test(a, b, c, d, d2, e, f, g):
    class A(src.HydrogenLib.Class.Auto.AutoStr):
        _str_attrs = ['a']
        a = None

    class B(src.HydrogenLib.Class.Auto.AutoInfo):
        _str_attrs = ['b']
        b = None

    class C(src.HydrogenLib.Class.Auto.AutoRepr):
        _repr_attrs = ['c']
        c = None

    class D(src.HydrogenLib.Class.Auto.AutoCompare):
        _compare_attrs = ['d']
        d = None

    class E(src.HydrogenLib.Class.Auto.AutoOperator):
        oper = src.HydrogenLib.Class.Auto.AutoOperatorFunc(globs=globals())
        e = 100

        @oper.operator('+')
        def add(self, other):
            return self.e + other

        @oper.operator('-')
        def sub(self, other):
            return self.e - other

        @oper.operator('*')
        def mul(self, other):
            return self.e * other

        @oper.operator('//')
        def floordiv(self, other):
            return self.e // other

    class F(src.HydrogenLib.Class.Auto.AutoState):
        _state_attrs = ['f']
        f = None

    class G(src.HydrogenLib.Class.Auto.AutoRegDict):
        default_value = 0
        isdeepcopy = False

    ca = A()
    cb = B()
    cc = C()
    cd = D()
    cd2 = D()
    ce = E()
    cf = F()
    cg = G()

    ca.a, cb.b, cc.c, cd.d, ce.e, cf.f = a, b, c, d, e, f
    cd2 = d2
    return str(a), str(b), repr(c), cd < cd2, (ce * ce, ce - ce, ce + ce, ce // ce), f.__getstate__(), (
        cg['a'], cg['b'])
