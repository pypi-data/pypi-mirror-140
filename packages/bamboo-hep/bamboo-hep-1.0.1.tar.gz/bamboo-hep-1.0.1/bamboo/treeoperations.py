"""
Object representation of operations on TTree branches

The aim is to provide provide sufficiently flexible and complete foundation
for the development of efficient histogram-filling programs
through the use of python wrappers (see e.g. treeproxies).
"""

import binascii
import hashlib
import logging
from collections import defaultdict
from itertools import chain, combinations, repeat, zip_longest

logger = logging.getLogger(__name__)

boolType = "bool"
intType = "int"
floatType = "double"
SizeType = "std::size_t"


def equal_elements(seqA, seqB):
    return all(ia == ib for ia, ib in zip_longest(seqA, seqB))


def op_digest(*args):
    h = hashlib.blake2b(digest_size=16, salt=b"bamboo TupleOp")
    for arg in args:
        if isinstance(arg, TupleOp):
            h.update(arg.digest)
        elif isinstance(arg, str):
            h.update(arg.encode())
        elif isinstance(arg, bytes):
            h.update(arg)
        else:
            raise ValueError(f"Unsupported content: {arg!r}")
    return h.digest()


def hexStr_digest(digest):
    return binascii.b2a_hex(digest).decode()


def op_hash(*args):
    if len(args) == 1:
        return hash(args[0])
    else:
        return hash(tuple(args))


class TupleOpCache:
    __slots__ = ("hash", "repr", "digest")

    def __init__(self):
        self.hash = None
        self.repr = None
        self.digest = None

    def __bool__(self):
        return self.hash is not None or self.repr is not None


class TupleOp:
    """ Interface & base class for operations on leafs and resulting objects / values

    Instances should be defined once, and assumed immutable by all observers
    (they should only ever be modified just after construction, preferably by the owner).
    Since a value-based hash (and repr) is cached on first use, violating this rule
    might lead to serious bugs. In case of doubt the clone method can be used to
    obtain an independent copy.
    Subclasses should define a result property and clone, _repr, _eq, and optionally deps methods.
    """
    # this means all deriving classes need to define __slots__ (for performance)
    __slots__ = ("typeName", "_cache", "canDefine")

    def __init__(self, typeName):
        self.typeName = typeName
        self._cache = TupleOpCache()
        self.canDefine = True

    def clone(self, memo=None, select=lambda nd: True, selClones=None):
        """ Create an independent copy (with empty repr/hash cache) of the (sub)expression """
        if memo is None:  # top-level, construct the dictionary
            memo = dict()
        if id(self) in memo:
            return memo[id(self)]
        else:
            cp = self._clone(memo, select, selClones=selClones)
            cln = cp if cp is not None else self
            memo[id(self)] = cln
            return cln

    # simple version, call clone of attributes without worrying about memo
    def _clone(self, memo, select, selClones=None):
        """
        Implementation of clone - to be overridden by all subclasses
            (memo is dealt with by clone, so simply construct, calling
            .clone(memo=memo, select=select) on TupleOp attributes.
            Return None if no clone is needed (based on select)
        """
        if select(self):
            cln = self.__class__(self.typeName)
            if selClones is not None:
                selClones.append(cln)
            return cln

    def deps(self, defCache=None, select=(lambda x: True), includeLocal=False):
        """ Dependent TupleOps iterator """
        yield from []

    @property
    def result(self):
        """ Proxy to the result of this (sub)expression """
        from .treeproxies import makeProxy
        return makeProxy(self)

    # subclasses should define at least _clone, _repr, and _eq (value-based)
    def __repr__(self):
        """ String representation (used for hash, and lazily cached) """
        if self._cache.repr is None:
            self._cache.repr = self._repr()
        return self._cache.repr

    def _repr(self):
        """
        __repr__ implementation - to be overridden by all subclasses
            (caching is in top-level __repr__)
        """
        return f"TupleOp({self.typeName})"

    def __hash__(self):
        """ Value-based hash (lazily cached) """
        if self._cache.hash is None:
            self._cache.hash = self._hash()
        return self._cache.hash

    def _hash(self, fun=op_hash):
        """
        __hash__ and digest implementation - subclasses please override
            (caching is in top-level)
        """
        return fun(repr(self))

    @property
    def digest(self):
        """ Get a 16-byte digest (cached) """
        if self._cache.digest is None:
            self._cache.digest = self._hash(fun=op_digest)
        return self._cache.digest

    def __eq__(self, other):
        """
        Identity or value-based equality comparison
            (same object and unequal should be fast)
        """
        # _eq may end up being quite expensive, but should almost never be called
        return (id(self) == id(other)
                or (self.__hash__() == hash(other) and self.__class__ == other.__class__
                    and self._eq(other)))

    def _eq(self, other):
        """
        value-based __eq__ implementation - to be overridden by all subclasses
            (protects against hash collisions; hash and class are checked to be equal already)
        """
        return True

    def get_cppStr(self, defCache=None):
        """ Interface method: generate a C++ string from the operation

        :param defCache: cache with defined operations and symbols;
            a minimal implementation is :py:class:`~bamboo.treeoperations.CppStrRedir`
            (which does not do any caching)
        """
        pass


# implementations are split out, see treeproxies
class TupleBaseProxy:
    """
    Interface & base class for proxies
    """
    def __init__(self, op):
        self._parent = op

    @property
    def op(self):
        if self._parent is None:
            raise ValueError(f"Cannot get operation for {self!r}, abstract base class / empty parent")
        return self._parent

    @property
    def _typeName(self):
        return self._parent.typeName


class CppStrRedir:
    """ Expression cache interface. Default implementation: no caching """
    def __init__(self):
        self._iFun = 0

    def __call__(self, arg):
        return arg.get_cppStr(defCache=self)

    def symbol(self, decl):
        """
        Define (or get) a new C++ symbol for the declaration

        decl should contain the code, with <<name>> where the name should go.  Returns the unique name
        """
        raise NotImplementedError(f"Asked to add defined symbol for {decl}, but that's not supported")

    def stop(self, op):
        return False

    def getColName(self, op):
        return None

    def shouldDefine(self, arg):
        return False


cppNoRedir = CppStrRedir()


class ForwardingOp(TupleOp):
    """ Transparent wrapper (base for marking parts of the tree, e.g. things with systematic variations) """
    __slots__ = ("wrapped",)

    def __init__(self, wrapped, canDefine=None):
        self.wrapped = wrapped
        super().__init__(self.wrapped.typeName)
        self.canDefine = canDefine if canDefine is not None else self.wrapped.canDefine

    def _clone(self, memo, select, selClones=None):
        clWr = self.wrapped.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if isSel or id(clWr) != id(self.wrapped):
            cln = self.__class__(clWr, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            if select(self.wrapped):
                yield self.wrapped
            yield from self.wrapped.deps(defCache=defCache, select=select, includeLocal=includeLocal)

    @property
    def result(self):
        wrapRes = self.wrapped.result
        wrapRes._parent = self
        return wrapRes

    def _repr(self):
        return f"{self.__class__.__name__}({self.wrapped!r})"

    def _hash(self, fun=op_hash):
        return fun(self.wrapped)

    def _eq(self, other):
        return self.wrapped == other.wrapped

    def get_cppStr(self, defCache=cppNoRedir):
        return defCache(self.wrapped)


class Const(TupleOp):
    """ Hard-coded number (or expression) """
    __slots__ = ("value")

    def __init__(self, typeName, value):
        super().__init__(typeName)
        self.value = value

    def _clone(self, memo, select, selClones=None):
        if select(self):
            cln = self.__class__(self.typeName, self.value)
            if selClones is not None:
                selClones.append(cln)
            return cln

    def _repr(self):
        return f"{self.__class__.__name__}({self.typeName!r}, {self.value!r})"

    def _hash(self, fun=op_hash):
        return fun(self._repr())

    def _eq(self, other):
        return self.typeName == other.typeName and self.value == other.value

    # backends
    def get_cppStr(self, defCache=None):
        try:
            if abs(self.value) == float("inf"):  # may raise an exception
                return "std::numeric_limits<{0}>::{mnmx}()".format(
                    self.typeName, mnmx=("lowest" if self.value < 0. else "max"))
        except Exception:
            pass
        return str(self.value)  # should maybe be type-aware...

    def getPyROOT(self, gbl):
        if self.typeName == "std::string":
            return self.value.strip('"')
        return self.value


class Parameter(Const):
    """ Constant that should not be hardcoded, to reduce the amount of generated code """
    __slots__ = tuple()

    def __init__(self, typeName, value):
        super().__init__(typeName, value)

    @property
    def name(self):  # unique and usable as value. Will be replaced by myArg* where needed
        tStr = str(self.typeName).replace(":", "_")
        return f"/* par_{tStr} */ {self.value!s} "

    def get_cppStr(self, defCache=None):
        return self.name


class GetColumn(TupleOp):
    """ Get a column value """
    __slots__ = ("typeName", "name")

    def __init__(self, typeName, name):
        super().__init__(typeName)
        self.name = name

    def _clone(self, memo, select, selClones=None):
        if select(self):
            cln = self.__class__(self.typeName, self.name)
            if selClones is not None:
                selClones.append(cln)
            return cln

    def _repr(self):
        return f"{self.__class__.__name__}({self.typeName!r}, {self.name!r})"

    def _hash(self, fun=op_hash):
        return fun(self._repr())

    def _eq(self, other):
        return self.typeName == other.typeName and self.name == other.name

    def get_cppStr(self, defCache=None):
        return self.name


class GetArrayColumn(TupleOp):
    """ Get the number from a leaf """
    __slots__ = ("valueType", "name", "length")

    def __init__(self, valueType, name, length):
        super().__init__(f"{valueType}[]")
        self.valueType = valueType
        self.name = name
        self.length = length

    def _clone(self, memo, select, selClones=None):
        lnCl = self.length.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if isSel or id(lnCl) != id(self.length):
            cln = self.__class__(self.typeName, self.name, lnCl)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            if select(self.length):
                yield self.length
            yield from self.length.deps(defCache=defCache, select=select, includeLocal=includeLocal)

    @property
    def result(self):
        from .treeproxies import ArrayProxy
        return ArrayProxy(self, self.valueType, self.length.result)

    def _repr(self):
        return f"{self.__class__.__name__}({self.typeName!r}, {self.name!r}, {self.length!r})"

    def _hash(self, fun=op_hash):
        return fun(self._repr())

    def _eq(self, other):
        return self.typeName == other.typeName and self.name == other.name and self.length == other.length

    def get_cppStr(self, defCache=None):
        return self.name


# helper
def adaptArg(arg, typeHint=None):
    if isinstance(arg, TupleBaseProxy):
        return arg.op
    elif isinstance(arg, TupleOp):
        return arg
    elif typeHint is not None:  # make a constant
        from . import treeproxies as _tp
        if isinstance(arg, str):  # string, needs quote
            return Const(typeHint, f'"{arg}"')
        elif typeHint in _tp._boolTypes:
            return Const(typeHint, "true" if arg else "false")
        elif isinstance(arg, int):
            # TODO apply C++ rules for type of an integer literal
            return Const(typeHint, arg)
        elif isinstance(arg, float):
            return Const(typeHint, arg)
        else:
            logger.warning(f"Constructing unchecked literal of type {typeHint}: {arg}")
            return Const(typeHint, arg)
    else:
        raise ValueError("Should either get an expression, or some kind of type hint")


def _moTp_1EnsureFloat(arg):
    from . import treeproxies as _tp
    if arg.typeName in _tp._floatTypes:
        return arg.typeName
    else:
        if arg.typeName not in _tp._integerTypes:
            logger.warning(f"Unknown numeric type {arg.typeName}, promoting to {floatType}")
        return floatType


def _moTp_combMaybeFloat(*args):
    from . import treeproxies as _tp
    if any(arg.typeName in _tp._floatTypes for arg in args):
        if any(arg.typeName in ("Double_t", "double") for arg in args):
            return "double"  # 64-bit
        else:
            return "float"  # 32-bit
    else:  # TODO apply the rules for integers
        return args[0].typeName


def _moTp_minmax(a, b):
    from . import treeproxies as _tp
    if a.typeName == b.typeName:
        return a.typeName
    elif a.typeName in _tp._floatTypes or b.typeName in _tp._floatTypes:
        return floatType
    else:  # TODO apply the rules for integers
        return a.typeName


mathOpFuns_typeAndCppStr = {
    "add": (_moTp_combMaybeFloat, (lambda *args: "( {} )".format(" + ".join(args)))),
    "multiply": (_moTp_combMaybeFloat, (lambda *args: "( {} )".format(" * ".join(args)))),
    "subtract": (_moTp_combMaybeFloat, "( {} - {} )".format),
    "divide": ((lambda a1, a2: a1.typeName), "( {} / {} )".format),
    "floatdiv": (floatType, "( 1.*{} / {} )".format),
    "mod": ((lambda a1, a2: a1.typeName), "( {} % {} )".format),
    "neg": (None, "( -{} )".format),
    #
    "lt": (boolType, "( {} <  {} )".format),
    "le": (boolType, "( {} <= {} )".format),
    "eq": (boolType, "( {} == {} )".format),
    "ne": (boolType, "( {} != {} )".format),
    "gt": (boolType, "( {} >  {} )".format),
    "ge": (boolType, "( {} >= {} )".format),
    "and": (boolType, (lambda *args: "( {} )".format(" && ".join(args)))),
    "or": (boolType, (lambda *args: "( {} )".format(" || ".join(args)))),
    "not": (boolType, "( ! {} )".format),
    #
    # TODO next three: apply the rules for integer type
    "band": (intType, lambda *args: "( {} )".format(" & ".join(args))),
    "bor": (intType, lambda *args: "( {} )".format(" | ".join(args))),
    "bxor": (intType, lambda *args: "( {} )".format(" ^ ".join(args))),
    "bnot": (None, "( ~ {} )".format),
    "lshift": ((lambda a1, a2: a1.typeName), "( {}<<{} )".format),
    "rshift": ((lambda a1, a2: a1.typeName), "( {}>>{} )".format),
    #
    "abs": (None, "std::abs( {} )".format),
    "sqrt": (_moTp_1EnsureFloat, "std::sqrt( {} )".format),
    "pow": ((lambda a1, a2: _moTp_1EnsureFloat(a1)), "std::pow( {}, {} )".format),
    "exp": (_moTp_1EnsureFloat, "std::exp( {} )".format),
    "log": (_moTp_1EnsureFloat, "std::log( {} )".format),
    "log10": (_moTp_1EnsureFloat, "std::log10( {} )".format),
    "sin": (_moTp_1EnsureFloat, "std::sin( {} )".format),
    "cos": (_moTp_1EnsureFloat, "std::cos( {} )".format),
    "tan": (_moTp_1EnsureFloat, "std::tan( {} )".format),
    "asin": (_moTp_1EnsureFloat, "std::asin( {} )".format),
    "acos": (_moTp_1EnsureFloat, "std::acos( {} )".format),
    "atan": (_moTp_1EnsureFloat, "std::atan( {} )".format),
    "max": (_moTp_minmax, "std::max( {}, {} )".format),
    "min": (_moTp_minmax, "std::min( {}, {} )".format),
    #
    "switch": ((lambda t, a, b: _moTp_minmax(a, b)), "( ( {} ) ? ( {} ) : ( {} ) )".format)
}


class MathOp(TupleOp):
    """ Mathematical function N->1, e.g. sin, abs, ( lambda x, y : x*y ) """
    @staticmethod
    def findResultType(op, args, hint=None):
        opStrat, _ = mathOpFuns_typeAndCppStr[op]
        fromStrat = None
        if isinstance(opStrat, str):  # operations that always return the same type, e.g. bool
            fromStrat = opStrat
        elif len(args) == 1 and opStrat is None:
            fromStrat = args[0].typeName  # unary -> same type by default
        elif opStrat:
            fromStrat = opStrat(*args)
        if fromStrat:
            return fromStrat
        if not hint:
            raise RuntimeError(f"No type could be inferred for MathOp {op!r}")
        return hint
    __slots__ = ("op", "args")

    def __init__(self, op, *args, **kwargs):
        self.op = op
        self.args = tuple(adaptArg(a, typeHint=floatType) for a in args)
        super().__init__(MathOp.findResultType(op, self.args, kwargs.pop("outType", None)))
        self.canDefine = kwargs.pop("canDefine", all(a.canDefine for a in self.args))
        assert len(kwargs) == 0

    def _clone(self, memo, select, selClones=None):
        argsCl = tuple(a.clone(memo=memo, select=select, selClones=selClones) for a in self.args)
        isSel = select(self)
        if isSel or any(id(aCl) != id(aOrig) for aCl, aOrig in zip(argsCl, self.args)):
            cln = self.__class__(self.op, *argsCl, outType=self.typeName, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in self.args:
                if select(arg):
                    yield arg
                yield from arg.deps(defCache=defCache, select=select, includeLocal=includeLocal)

    def _repr(self):
        return "{}({}, {}, outType={!r})".format(
            self.__class__.__name__, self.op,
            ", ".join(repr(arg) for arg in self.args), self.typeName)

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.op, self.typeName, *self.args)

    def _eq(self, other):
        return self.typeName == other.typeName and self.op == other.op and self.args == other.args

    def get_cppStr(self, defCache=cppNoRedir):
        return mathOpFuns_typeAndCppStr[self.op][1](*(defCache(arg) for arg in self.args))


class GetItem(TupleOp):
    """ Get item from array (from function call or from array leaf) """
    __slots__ = ("arg", "_index")

    def __init__(self, arg, valueType, index, indexType=SizeType, canDefine=None):
        super().__init__(valueType)
        self.arg = adaptArg(arg)
        self._index = adaptArg(index, typeHint=indexType)
        self.canDefine = (canDefine if canDefine is not None
                          else (self.arg.canDefine and self._index.canDefine))

    def _clone(self, memo, select, selClones=None):
        argCl = self.arg.clone(memo=memo, select=select, selClones=selClones)
        idxCl = self._index.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if isSel or id(argCl) != id(self.arg) or id(self._index) != id(idxCl):
            cln = self.__class__(argCl, self.typeName, idxCl, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in (self.arg, self._index):
                if select(arg):
                    yield arg
                yield from arg.deps(defCache=defCache, select=select, includeLocal=includeLocal)

    @property
    def index(self):
        return self._index.result

    def _repr(self):
        return f"{self.__class__.__name__}({self.arg!r}, {self.typeName!r}, {self._index!r})"

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.arg, self.typeName, self._index)

    def _eq(self, other):
        return (self.arg == other.arg and self.typeName == other.typeName
                and self._index == other._index)

    def get_cppStr(self, defCache=cppNoRedir):
        return f"{defCache(self.arg)}[{defCache(self._index)}]"


class Construct(TupleOp):
    __slots__ = ("args",)

    def __init__(self, typeName, args, canDefine=None):
        super().__init__(typeName)
        self.args = tuple(adaptArg(a, typeHint=floatType) for a in args)
        self.canDefine = canDefine if canDefine is not None else all(a.canDefine for a in self.args)

    def _clone(self, memo, select, selClones=None):
        argsCl = tuple(a.clone(memo=memo, select=select, selClones=selClones) for a in self.args)
        isSel = select(self)
        if isSel or any(id(argCl) != id(arg) for argCl, arg in zip(argsCl, self.args)):
            cln = self.__class__(self.typeName, argsCl, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in self.args:
                if select(arg):
                    yield arg
                yield from arg.deps(defCache=defCache, select=select, includeLocal=includeLocal)

    def _repr(self):
        return "{}({!r}, {})".format(
            self.__class__.__name__, self.typeName, ", ".join(repr(a) for a in self.args))

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.typeName, *self.args)

    def _eq(self, other):
        return self.typeName == other.typeName and self.args == other.args

    def get_cppStr(self, defCache=cppNoRedir):
        return "{0}{{{1}}}".format(self.typeName, ", ".join(defCache(a) for a in self.args))

    def getPyROOT(self, gbl):
        if len(self.args) == 1 and isinstance(self.args[0], InitList):
            ret = getattr(gbl, self.typeName)()
            for elm in self.args[0].elms:
                ret.push_back(elm.getPyROOT(gbl))
            return ret
        else:
            return getattr(gbl, self.typeName)(*(arg.getPyROOT(gbl) for arg in self.args))


def guessReturnType(mp):
    from .root import gbl
    oneDecl = None
    if hasattr(mp, "func_doc") and hasattr(mp, "func_name"):
        oneDecl = mp.func_doc.split("\n")[0]  # overloads should have the same return type
    elif ((hasattr(gbl, "TemplateProxy") and isinstance(mp, gbl.TemplateProxy))
          or (type(mp).__name__ == "TemplateProxy")):
        oneDecl = mp.__doc__.split("\n")[0]
    if oneDecl:
        toks = list(oneDecl.split())
        # left and right strip const * and &
        while toks[-1].rstrip("&") in ("", "const", "static"):
            toks = toks[:-1]
        while toks[0].rstrip("&") in ("", "const", "static"):
            toks = toks[1:]
        while any(tok.endswith("unsigned") for tok in toks):
            iU = next(i for i, tok in enumerate(toks) if tok.endswith("unsigned"))
            toks[iU] = " ".join((toks[iU], toks[iU + 1]))
            del toks[iU + 1]
        if len(toks) == 2:
            return toks[0].rstrip("&")
        else:
            nOpen = 0
            i = 0
            while i < len(toks) and (i == 0 or nOpen != 0):
                nOpen += (toks[i].count("<") - toks[i].count(">"))
                i += 1
            return " ".join(toks[:i]).rstrip("&")
    else:
        return "Float_t"


class CallMethod(TupleOp):
    """
    Call a method
    """
    __slots__ = ("name", "args")

    def __init__(self, name, args, returnType=None, getFromRoot=True, canDefine=None):
        super().__init__(returnType if returnType
                         else CallMethod._initReturnType(name, getFromRoot=getFromRoot))
        self.name = name  # NOTE can only be a hardcoded string this way
        self.args = tuple(adaptArg(arg) for arg in args)
        self.canDefine = (canDefine if canDefine is not None
                          else all(a.canDefine for a in self.args))

    @staticmethod
    def _initReturnType(name, getFromRoot=True):
        mp = None
        if getFromRoot:
            try:
                from .root import gbl
                if "::" in name:
                    res = gbl
                    for tok in name.split("::"):
                        res = getattr(res, tok)
                    if res != gbl:
                        mp = res
                else:
                    mp = getattr(gbl, name)
            except Exception as ex:
                logger.error(f"Exception in getting method pointer {name}: {ex}")
        return guessReturnType(mp)

    def _clone(self, memo, select, selClones=None):
        argsCl = tuple(a.clone(memo=memo, select=select, selClones=selClones) for a in self.args)
        isSel = select(self)
        if isSel or any(id(argCl) != id(arg) for argCl, arg in zip(argsCl, self.args)):
            cln = self.__class__(self.name, argsCl, returnType=self.typeName, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.add(cln)
            return cln

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in self.args:
                if select(arg):
                    yield arg
                yield from arg.deps(defCache=defCache, select=select, includeLocal=includeLocal)

    def _repr(self):
        return "{}({!r}, ({}), returnType={!r})".format(
            self.__class__.__name__, self.name,
            ", ".join(repr(arg) for arg in self.args), self.typeName)

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.name, self.typeName, *self.args)

    def _eq(self, other):
        return self.name == other.name and self.typeName == other.typeName and self.args == other.args

    # backends
    def get_cppStr(self, defCache=cppNoRedir):
        return "{}({})".format(self.name, ", ".join(defCache(arg) for arg in self.args))


class CallMemberMethod(TupleOp):
    """ Call a member method """
    __slots__ = ("this", "name", "args", "byPointer")

    def __init__(self, this, name, args, byPointer=False, returnType=None, canDefine=None):
        self.this = adaptArg(this)
        self.name = name  # NOTE can only be a hardcoded string this way
        self.args = tuple(adaptArg(arg) for arg in args)
        self.byPointer = byPointer
        super().__init__(returnType if returnType
                         else guessReturnType(getattr(this._typ, self.name)))
        self.canDefine = (canDefine if canDefine is not None
                          else self.this.canDefine and all(a.canDefine for a in self.args))

    def _clone(self, memo, select, selClones=None):
        thisCl = self.this.clone(memo=memo, select=select, selClones=selClones)
        argsCl = tuple(a.clone(memo=memo, select=select, selClones=selClones)
                       for a in self.args)
        isSel = select(self)
        if (isSel or id(thisCl) != id(self.this)
                or any(id(argCl) != id(arg) for argCl, arg in zip(argsCl, self.args))):
            cln = self.__class__(
                thisCl, self.name, argsCl, byPointer=self.byPointer,
                returnType=self.typeName, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in chain((self.this,), self.args):
                if select(arg):
                    yield arg
                yield from arg.deps(defCache=defCache, select=select, includeLocal=includeLocal)

    def _repr(self):
        return "{}({!r}, {!r}, ({}), byPointer={!r}, returnType={!r})".format(
            self.__class__.__name__, self.this, self.name,
            ", ".join(repr(arg) for arg in self.args), self.byPointer, self.typeName)

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.this, self.name,
                   repr(self.byPointer), self.typeName, *self.args)

    def _eq(self, other):
        return (self.this == other.this and self.name == other.name
                and self.byPointer == other.byPointer
                and self.typeName == other.typeName and self.args == other.args)

    def get_cppStr(self, defCache=cppNoRedir):
        if self.name == "__call__":
            call = ""
        elif self.byPointer:
            call = f"->{self.name}"
        else:
            call = f".{self.name}"
        return "{}{}({})".format(
            defCache(self.this), call, ", ".join(defCache(arg) for arg in self.args))


class GetDataMember(TupleOp):
    """ Get a data member """
    __slots__ = ("this", "name", "byPointer")

    def __init__(self, this, name, byPointer=False, returnType=None, canDefine=None):
        self.this = adaptArg(this)
        self.name = name  # NOTE can only be a hardcoded string this way
        self.byPointer = byPointer
        super().__init__(returnType if returnType else GetDataMember._initType(this, name))
        self.canDefine = canDefine if canDefine is not None else self.this.canDefine

    @staticmethod
    def _initType(this, name):
        try:
            protoTp = this._typ
            proto = protoTp()  # should *in principle* work for most ROOT objects
            att = getattr(proto, name)
            tpNm = type(att).__name__
            if protoTp.__name__.startswith("pair<") and name in ("first", "second"):
                tpNms = tuple(tok.strip() for tok in protoTp.__name__[5:-1].split(","))
                return (tpNms[0] if name == "first" else tpNms[1])
            return tpNm
        except Exception as e:
            logger.error(f"Problem getting type of data member {name} of {this!r}", e)
            return "void"

    def _clone(self, memo, select, selClones=None):
        thisCl = self.this.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if isSel or id(thisCl) != id(self.this):
            cln = self.__class__(
                thisCl, self.name, byPointer=self.byPointer,
                returnType=self.typeName, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            if select(self.this):
                yield self.this
            yield from self.this.deps(defCache=defCache, select=select, includeLocal=includeLocal)

    def _repr(self):
        return f"{self.__class__.__name__}({self.this!r}, {self.name!r}, {self.byPointer!r})"

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.this, self.name, repr(self.byPointer))

    def _eq(self, other):
        return (self.this == other.this and self.name == other.name
                and self.byPointer == other.byPointer)

    def get_cppStr(self, defCache=cppNoRedir):
        return "{}{}{}".format(defCache(self.this), ("->" if self.byPointer else "."), self.name)


class ExtVar(TupleOp):
    """ Externally-defined variable (used by name) """
    __slots__ = ("name",)

    def __init__(self, typeName, name):
        super().__init__(typeName)
        self.name = name

    def _clone(self, memo, select, selClones=None):
        if select(self):
            cln = self.__class__(self.typeName, self.name)
            if selClones is not None:
                selClones.append(cln)
            return cln

    def _repr(self):
        return f"{self.__class__.__name__}({self.typeName!r}, {self.name!r})"

    def _hash(self, fun=op_hash):
        return fun(self._repr())

    def _eq(self, other):
        return self.typeName == other.typeName and self.name == other.name

    def get_cppStr(self, defCache=None):
        return self.name


class DefinedSymbol(TupleOp):
    """ Defined variable (used by name), first use will trigger definition """
    __slots__ = ("definition", "_nameHint")

    def __init__(self, typeName, definition, nameHint=None):
        super().__init__(typeName)
        self.definition = definition
        self._nameHint = nameHint

    def _clone(self, memo, select, selClones=None):
        if select(self):
            cln = self.__class__(self.typeName, self.definition, nameHint=self._nameHint)
            if selClones is not None:
                selClones.append(cln)
            return cln

    def _repr(self):
        return (f"{self.__class__.__name__}({self.typeName!r}, {self.definition!r}, "
                f"nameHint={self._nameHint!r})")

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.typeName,
                   self.definition, (self._nameHint or 'None'))

    def _eq(self, other):
        return (self.typeName == other.typeName and self.definition == other.definition
                and self._nameHint == other._nameHint)

    def get_cppStr(self, defCache=cppNoRedir):
        return defCache.symbol(self.definition, nameHint=self._nameHint)


class InitList(TupleOp):
    """ Initializer list """
    __slots__ = ("elms",)

    def __init__(self, typeName, elms, elmType=None, canDefine=None):
        super().__init__(typeName)
        self.typeName = typeName
        self.elms = tuple(adaptArg(e, typeHint=elmType) for e in elms)
        self.canDefine = (canDefine if canDefine is not None
                          else all(elm.canDefine for elm in self.elms))

    def _clone(self, memo, select, selClones=None):
        elmsCl = tuple(elm.clone(memo=memo, select=select, selClones=selClones)
                       for elm in self.elms)
        isSel = select(self)
        if isSel or any(id(elmCl) != id(elm) for elmCl, elm in zip(elmsCl, self.elms)):
            cln = self.__class__(self.typeName, elmsCl, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for elm in self.elms:
                if select(elm):
                    yield elm
                yield from elm.deps(defCache=defCache, select=select, includeLocal=includeLocal)

    def _repr(self):
        return "{}<{}>({})".format(
            self.__class__.__name__, self.typeName,
            ", ".join(repr(elm) for elm in self.elms))

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.typeName, *self.elms)

    def _eq(self, other):
        return self.typeName == other.typeName and self.elms == other.elms

    def get_cppStr(self, defCache=cppNoRedir):
        return "{{ {0} }}".format(", ".join(defCache(elm) for elm in self.elms))


class LocalVariablePlaceholder(TupleOp):
    """
    Placeholder type for a local variable connected to an index
        (first step in a specific-to-general strategy)
    """
    __slots__ = ("_parent", "i")

    def __init__(self, typeName, parent=None, i=None):
        super().__init__(typeName)
        self._parent = parent
        self.i = i  # FIXME this one is set **late** - watch out with what we call
        self.canDefine = False

    def _clone(self, memo, select, selClones=None):
        if select(self):
            raise RuntimeError("LocalVariablePlaceholder should not be cloned")
            return self.__class__(self.typeName, parent=self._parent, i=self.i)

    @property
    def name(self):
        if self.i is None:
            raise RuntimeError("Using LocalVariablePlaceholder before giving it an index")
        return f"i{self.i:d}"

    def get_cppStr(self, defCache=None):
        return self.name

    def _repr(self):
        return f"{self.__class__.__name__}({self.typeName!r}, i={self.i!r})"

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.typeName, str(self.i))

    def _eq(self, other):
        # fine for the LocalVariablePlaceholder to be equal from different sub-expressions because
        # it will never be defined and if equal to an expression that can be defined, it's fine
        return self.typeName == other.typeName and self.i is not None and self.i == other.i


def collectNodes(expr, defCache=cppNoRedir, select=(lambda nd: True), includeLocal=True):
    # simple helper
    if select(expr):
        yield expr
    yield from expr.deps(defCache=defCache, select=select, includeLocal=includeLocal)


def _triggerDefinitions(self, defCache=cppNoRedir):
    for dep in self.deps(defCache=defCache, select=lambda op: defCache.shouldDefine(op)):
        cn = defCache(dep)
        if not cn:
            logger.warning(f"Probably a problem in triggering definition for {dep}")


def _collectDeps(self, defCache=cppNoRedir):
    return {dep for dep in self.deps(defCache=defCache, select=(
        lambda op: (isinstance(op, GetColumn) or isinstance(op, GetArrayColumn)
                    or isinstance(op, LocalVariablePlaceholder) or isinstance(op, Parameter)
                    or defCache.shouldDefine(op) or (defCache.getColName(op) is not None))))}


class StopAt:
    def __init__(self, stopPred):
        self.stopPred = stopPred

    def __call__(self, arg):
        raise NotImplementedError("This is only to control the loops")

    def symbol(self, decl):
        raise NotImplementedError(
            f"Asked to add defined symbol for {decl}, but that's not supported; "
            "this is only to control the loop")

    def stop(self, op):
        return self.stopPred(op)

    def _getColNme(self, op):
        return None


class VisitOnceAndStopAt(StopAt):
    def __init__(self, stopPred=None):
        self.visitedIds = set()
        super().__init__(stopPred)

    def stop(self, op):
        opId = id(op)
        seenBefore = (opId in self.visitedIds)
        if not seenBefore:
            self.visitedIds.add(opId)
        return seenBefore or (self.stopPred is not None and self.stopPred(op))


# replacement for cases that don't have the full definition cache (e.g. during construction)
stopAtDefinedOrCan = StopAt(lambda op: op.canDefine or isinstance(op, DefineOnFirstUse))


def _canDefine(expr, local):
    return not any(ind is not None for ind in collectNodes(
        expr, defCache=stopAtDefinedOrCan, includeLocal=False,
        select=(lambda nd: isinstance(nd, LocalVariablePlaceholder) and nd not in local)))


def _isRangeAndHasMxi(op):
    return isinstance(op, RangeOp) and op._mxi is not None


def _maxLVIdx(expr):
    return max(chain([-1], ((nd._mxi if nd._mxi is not None else -1) for nd in collectNodes(
        expr, defCache=VisitOnceAndStopAt(_isRangeAndHasMxi), select=_isRangeAndHasMxi))))


def _convertFunArgs(deps, defCache=cppNoRedir):
    from . import treeproxies as _tp
    capDeclCall = []
    for ld in deps:
        if isinstance(ld, GetArrayColumn):
            capDeclCall.append((f"&{ld.name}",
                                f"const ROOT::VecOps::RVec<{ld.valueType}>& {ld.name}",
                                ld.name, ld.name))
        elif isinstance(ld, GetColumn):
            if any(ld.typeName in basicTp for basicTp in (
                    _tp._boolTypes, _tp._integerTypes, _tp._floatTypes)):  # by value
                capDeclCall.append((ld.name, f"{ld.typeName} {ld.name}", ld.name, ld.name))
            else:  # by const-ref
                capDeclCall.append((f"&{ld.name}",
                                    f"const {ld.typeName}& {ld.name}",
                                    ld.name, ld.name))
        elif isinstance(ld, LocalVariablePlaceholder):
            if not ld.name:
                print(f"ERROR: no name for local {ld}")
            capDeclCall.append((ld.name, f"{ld.typeName} {ld.name}", ld.name, ld.name))
        elif defCache.shouldDefine(ld) or (defCache.getColName(ld) is not None):
            nm = defCache.getColName(ld)
            if not nm:
                print(f"ERROR: no column name for {ld}")
            if not any(f"&{nm}" == icap[0] for icap in capDeclCall):
                capDeclCall.append((f"&{nm}", f"const {ld.result._typeName}& {nm}", nm, nm))
            else:
                print(f"WARNING: dependency {nm} is there twice")
        elif isinstance(ld, Parameter):
            capDeclCall.append((ld.name, f"{ld.typeName} {ld.name}", ld.name, str(ld.value)))
        else:
            raise AssertionError(f"Dependency with unknown type: {ld}")
    if capDeclCall:
        # sort by declaration (alphabetic for the same type)
        return zip(*sorted(capDeclCall, key=(lambda elm: elm[1])))
    else:
        return [], [], [], []


class RangeOp(TupleOp):
    __slots__ = ("rng",)

    def __init__(self, rng, typeName):
        self.rng = rng
        super().__init__(typeName)

    @property
    def _mxi(self):
        return None


class Select(RangeOp):
    """ Define a selection on a range """
    __slots__ = ("predExpr", "_i")

    def __init__(self, rng, predExpr, idx, canDefine=None):
        super().__init__(rng, f"ROOT::VecOps::RVec<{SizeType}>")
        self.predExpr = predExpr
        self._i = idx
        self.canDefine = (
            canDefine if canDefine is not None
            else self.rng.canDefine and _canDefine(self.predExpr, (self._i,)))

    @property
    def _mxi(self):
        return self._i.i

    def _clone(self, memo, select, selClones=None):
        rngCl = self.rng.clone(memo=memo, select=select, selClones=selClones)
        predCl = self.predExpr.clone(memo=memo, select=select, selClones=selClones)
        iCl = self._i.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if (isSel or id(rngCl) != id(self.rng) or id(predCl) != id(self.predExpr)
                or id(iCl) != id(self._i)):
            cln = self.__class__(rngCl, predCl, iCl, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    @staticmethod
    def fromRngFun(rng, pred):
        """ Factory method from a range and predicate (callable) """
        idx = LocalVariablePlaceholder(SizeType)
        predExpr = adaptArg(pred(rng._getItem(idx.result)))
        idx.i = _maxLVIdx(predExpr) + 1
        res = Select(adaptArg(rng.idxs), predExpr, idx)
        idx._parent = res
        from .treeproxies import SelectionProxy
        return SelectionProxy(rng._base, res, valueType=rng.valueType)

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in (self.rng, self.predExpr):
                if select(arg) and (includeLocal or arg != self._i):
                    yield arg
                for dp in arg.deps(defCache=defCache, select=select, includeLocal=includeLocal):
                    if includeLocal or dp != self._i:
                        yield dp

    @property
    def result(self):
        from .treeproxies import VectorProxy
        return VectorProxy(self, itemType=SizeType)

    def _repr(self):
        return f"{self.__class__.__name__}({self.rng!r}, {self.predExpr!r}, {self._i!r})"

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.rng, self.predExpr, self._i)

    def _eq(self, other):
        return self.rng == other.rng and self.predExpr == other.predExpr and self._i == other._i

    def get_cppStr(self, defCache=cppNoRedir):
        _triggerDefinitions(self, defCache=defCache)
        captures, _, _, _ = _convertFunArgs(_collectDeps(self, defCache=defCache), defCache=defCache)
        return "rdfhelpers::select({idxs},\n    [{captures}] ( {i} ) {{ return {predExpr}; }})".format(
            idxs=defCache(self.rng),
            captures=",".join(captures),
            i=f"{self._i.typeName} {self._i.name}",
            predExpr=defCache(self.predExpr)
        )


class Sort(RangeOp):
    """ Sort a range (ascendingly) by the value of a function on each element """
    __slots__ = ("funExpr", "_i")

    def __init__(self, rng, funExpr, idx, canDefine=None):
        super().__init__(rng, f"ROOT::VecOps::RVec<{SizeType}>")
        self.funExpr = funExpr
        self._i = idx
        self.canDefine = (
            canDefine if canDefine is not None
            else self.rng.canDefine and _canDefine(self.funExpr, (self._i,)))

    @property
    def _mxi(self):
        return self._i.i

    def _clone(self, memo, select, selClones=None):
        rngCl = self.rng.clone(memo=memo, select=select, selClones=selClones)
        funCl = self.funExpr.clone(memo=memo, select=select, selClones=selClones)
        iCl = self._i.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if (isSel or id(rngCl) != id(self.rng) or id(funCl) != id(self.funExpr)
                or id(iCl) != id(self._i)):
            cln = self.__class__(rngCl, funCl, iCl, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    @staticmethod
    def fromRngFun(rng, fun):
        idx = LocalVariablePlaceholder(SizeType)
        funExpr = adaptArg(fun(rng._getItem(idx.result)))
        idx.i = _maxLVIdx(funExpr) + 1
        res = Sort(adaptArg(rng.idxs), funExpr, idx)
        idx._parent = res
        from .treeproxies import SelectionProxy
        return SelectionProxy(rng._base, res, valueType=rng.valueType)

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in (self.rng, self.funExpr):
                if select(arg) and (includeLocal or arg != self._i):
                    yield arg
                for dp in arg.deps(defCache=defCache, select=select, includeLocal=includeLocal):
                    if includeLocal or dp != self._i:
                        yield dp

    @property
    def result(self):
        from .treeproxies import VectorProxy
        return VectorProxy(self, itemType=SizeType)

    def _repr(self):
        return f"{self.__class__.__name__}({self.rng!r}, {self.funExpr!r}, {self._i!r})"

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.rng, self.funExpr, self._i)

    def _eq(self, other):
        return self.rng == other.rng and self.funExpr == other.funExpr and self._i == other._i

    def get_cppStr(self, defCache=cppNoRedir):
        _triggerDefinitions(self, defCache=defCache)
        captures, _, _, _ = _convertFunArgs(_collectDeps(self, defCache=defCache), defCache=defCache)
        return "rdfhelpers::sort({idxs},\n    [{captures}] ( {i} ) {{ return {funExpr}; }})".format(
            idxs=defCache(self.rng),
            captures=",".join(captures),
            i=f"{self._i.typeName} {self._i.name}",
            funExpr=defCache(self.funExpr)
        )


class Map(RangeOp):
    """ Create a list of derived values for a collection (mostly useful for storing on skims) """
    __slots__ = ("funExpr", "_i", "mappedType")

    def __init__(self, rng, funExpr, idx, mappedType, canDefine=None):
        # self.rng are the input indices
        super().__init__(rng, f"ROOT::VecOps::RVec<{mappedType}>")
        self.funExpr = funExpr
        self._i = idx
        self.mappedType = mappedType
        self.canDefine = (
            canDefine if canDefine is not None
            else self.rng.canDefine and _canDefine(self.funExpr, (self._i,)))

    @property
    def _mxi(self):
        return self._i.i

    def _clone(self, memo, select, selClones=None):
        rngCl = self.rng.clone(memo=memo, select=select, selClones=selClones)
        funCl = self.funExpr.clone(memo=memo, select=select, selClones=selClones)
        iCl = self._i.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if (isSel or id(rngCl) != id(self.rng) or id(funCl) != id(self.funExpr)
                or id(iCl) != id(self._i)):
            cln = self.__class__(rngCl, funCl, iCl, self.mappedType, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    @staticmethod
    def fromRngFun(rng, fun, typeName=None):
        idx = LocalVariablePlaceholder(SizeType)
        val = fun(rng._getItem(idx.result))
        funExpr = adaptArg(val)
        idx.i = _maxLVIdx(funExpr) + 1
        res = Map(adaptArg(rng.idxs), funExpr, idx,
                  (typeName if typeName is not None else val._typeName))
        idx._parent = res
        return res.result

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in (self.rng, self.funExpr):
                if select(arg) and (includeLocal or arg != self._i):
                    yield arg
                for dp in arg.deps(defCache=defCache, select=select, includeLocal=includeLocal):
                    if includeLocal or dp != self._i:
                        yield dp

    @property
    def result(self):
        from .treeproxies import VectorProxy
        return VectorProxy(self, itemType=self.mappedType)

    def _repr(self):
        return f"{self.__class__.__name__}({self.rng!r}, {self.funExpr!r}, {self._i!r}, {self.mappedType!r})"

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.rng, self.funExpr, self._i, self.mappedType)

    def _eq(self, other):
        return (self.rng == other.rng and self.funExpr == other.funExpr
                and self._i == other._i and self.mappedType == other.mappedType)

    def get_cppStr(self, defCache=cppNoRedir):
        _triggerDefinitions(self, defCache=defCache)
        captures, _, _, _ = _convertFunArgs(_collectDeps(self, defCache=defCache), defCache=defCache)
        return "rdfhelpers::map<{valueType}>({idxs},\n    [{capt}] ( {i} ) {{ return {funExpr}; }})".format(
            valueType=self.mappedType,
            idxs=defCache(self.rng),
            capt=",".join(captures),
            i=f"{self._i.typeName} {self._i.name}",
            funExpr=defCache(self.funExpr)
        )


class Next(RangeOp):
    """ Define a search (first matching item, for a version that processes the whole range see Reduce) """
    __slots__ = ("predExpr", "_i")

    def __init__(self, rng, predExpr, idx, canDefine=None):
        # self.rng are the input indices
        super().__init__(rng, SizeType)
        self.predExpr = predExpr
        self._i = idx
        self.canDefine = (
            canDefine if canDefine is not None
            else self.rng.canDefine and _canDefine(self.predExpr, (self._i,)))

    @property
    def _mxi(self):
        return self._i.i

    def _clone(self, memo, select, selClones=None):
        rngCl = self.rng.clone(memo=memo, select=select, selClones=selClones)
        predCl = self.predExpr.clone(memo=memo, select=select, selClones=selClones)
        iCl = self._i.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if (isSel or id(rngCl) != id(self.rng) or id(predCl) != id(self.predExpr)
                or id(iCl) != id(self._i)):
            cln = self.__class__(rngCl, predCl, iCl, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    @staticmethod
    def fromRngFun(rng, pred):  # FIXME you are here
        idx = LocalVariablePlaceholder(SizeType)
        predExpr = adaptArg(pred(rng._getItem(idx.result)))
        idx.i = _maxLVIdx(predExpr) + 1
        res = Next(adaptArg(rng.idxs), predExpr, idx)
        idx._parent = res
        return rng._getItem(res)

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in (self.rng, self.predExpr):
                if select(arg) and (includeLocal or arg != self._i):
                    yield arg
                for dp in arg.deps(defCache=defCache, select=select, includeLocal=includeLocal):
                    if includeLocal or dp != self._i:
                        yield dp

    def _repr(self):
        return f"{self.__class__.__name__}({self.rng!r}, {self.predExpr!r}, {self._i!r})"

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.rng, self.predExpr, self._i)

    def _eq(self, other):
        return self.rng == other.rng and self.predExpr == other.predExpr and self._i == other._i

    def get_cppStr(self, defCache=cppNoRedir):
        _triggerDefinitions(self, defCache=defCache)
        captures, _, _, _ = _convertFunArgs(_collectDeps(self, defCache=defCache), defCache=defCache)
        return "rdfhelpers::next({idxs},\n     [{captures}] ( {i} ) {{ return {predexpr}; }}, -1)".format(
            idxs=defCache(self.rng),
            captures=",".join(captures),
            i=f"{self._i.typeName} {self._i.name}",
            predexpr=defCache(self.predExpr),
        )


class Reduce(RangeOp):
    """ Reduce a range to a value (could be a transformation, index...) """
    __slots__ = ("start", "accuExpr", "_i", "_prevRes")

    def __init__(self, rng, resultType, start, accuExpr, idx, prevRes, canDefine=None):
        # self.rng are the input indices
        super().__init__(rng, resultType)
        self.start = start
        self.accuExpr = accuExpr
        self._i = idx
        self._prevRes = prevRes
        self.canDefine = (
            canDefine if canDefine is not None
            else self.rng.canDefine and start.canDefine
            and _canDefine(accuExpr, (self._i, self._prevRes)))

    @property
    def _mxi(self):
        return self._prevRes.i

    def _clone(self, memo, select, selClones=None):
        rngCl = self.rng.clone(memo=memo, select=select, selClones=selClones)
        startCl = self.start.clone(memo=memo, select=select, selClones=selClones)
        accuCl = self.accuExpr.clone(memo=memo, select=select, selClones=selClones)
        iCl = self._i.clone(memo=memo, select=select, selClones=selClones)
        prevCl = self._prevRes.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if (isSel or id(rngCl) != id(self.rng) or id(startCl) != id(self.start)
                or id(accuCl) != id(self.accuExpr) or id(iCl) != id(self._i)
                or id(prevCl) != id(self._prevRes)):
            cln = self.__class__(rngCl, self.typeName, startCl, accuCl,
                                 iCl, prevCl, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(self)
            return cln

    @staticmethod
    def fromRngFun(rng, start, accuFun):
        resultType = start._typeName
        idx = LocalVariablePlaceholder(SizeType)
        prevRes = LocalVariablePlaceholder(resultType, i=-1)
        accuExpr = adaptArg(accuFun(prevRes.result, rng._getItem(idx.result)))
        maxLVIdx = _maxLVIdx(accuExpr)
        idx.i = maxLVIdx + 1
        prevRes.i = maxLVIdx + 2

        res = Reduce(adaptArg(rng.idxs), resultType, adaptArg(start), accuExpr, idx, prevRes)
        idx._parent = res
        prevRes._parent = res
        return res.result

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in (self.rng, self.start, self.accuExpr):
                if select(arg) and (includeLocal or arg not in (self._i, self._prevRes)):
                    yield arg
                for dp in arg.deps(defCache=defCache, select=select, includeLocal=includeLocal):
                    if includeLocal or dp not in (self._i, self._prevRes):
                        yield dp

    def _repr(self):
        return (f"{self.__class__.__name__}({self.rng!r}, {self.typeName!r}, "
                f"{self.start!r}, {self.accuExpr!r}, {self._i!r}, {self._prevRes!r})")

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.rng, self.typeName,
                   self.start, self.accuExpr, self._i, self._prevRes)

    def _eq(self, other):
        return (self.rng == other.rng and self.typeName == other.typeName
                and self.start == other.start and self.accuExpr == other.accuExpr
                and self._i == other._i and self._prevRes == other._prevRes)

    def get_cppStr(self, defCache=cppNoRedir):
        _triggerDefinitions(self, defCache=defCache)
        captures, _, _, _ = _convertFunArgs(_collectDeps(self, defCache=defCache), defCache=defCache)
        return ("rdfhelpers::reduce({idxs}, {start},\n"
                "     [{captures}] ( {prevRes}, {i} ) {{ return {accuexpr}; }})").format(
            idxs=defCache(self.rng),
            start=defCache(self.start),
            captures=",".join(captures),
            prevRes=f"{self._prevRes.typeName} {self._prevRes.name}",
            i=f"{self._i.typeName} {self._i.name}",
            accuexpr=defCache(self.accuExpr)
        )


class Combine(RangeOp):
    __slots__ = ("candPredExpr", "_i")

    def __init__(self, ranges, candPredExpr, idx, canDefine=None):
        # self.rng is [ input index lists ]
        super().__init__(ranges, f"ROOT::VecOps::RVec<rdfhelpers::Combination<{len(ranges):d}>>")
        self.candPredExpr = candPredExpr
        self._i = idx
        self.canDefine = (
            canDefine if canDefine is not None
            else all(rng.canDefine for rng in self.rng) and _canDefine(candPredExpr, self._i))

    @property
    def _mxi(self):
        return self._i[-1].i

    @property
    def n(self):
        return len(self.rng)

    def _clone(self, memo, select, selClones=None):
        rngCl = tuple(rng.clone(memo=memo, select=select, selClones=selClones) for rng in self.rng)
        predCl = self.candPredExpr.clone(memo=memo, select=select, selClones=selClones)
        iCl = tuple(i.clone(memo=memo, select=select, selClones=selClones) for i in self._i)
        isSel = select(self)
        if (isSel or any(id(rCl) != id(rng) for rCl, rng in zip(rngCl, self.rng))
                or id(predCl) != id(self.candPredExpr)
                or any(id(iiCl) != id(iOr) for iiCl, iOr in zip(iCl, self._i))):
            cln = self.__class__(rngCl, predCl, iCl, canDefine=self.canDefine)
            if selClones is not None and isSel:
                selClones.append(isSel)
            return cln

    @staticmethod
    def fromRngFun(num, ranges, candPredFun, samePred=None):
        ranges = ranges if len(ranges) > 1 else list(repeat(ranges[0], num))
        idx = tuple(LocalVariablePlaceholder(SizeType, i=-1 - i) for i in range(num))
        candPred = candPredFun(*(rng._getItem(iidx.result) for rng, iidx in zip(ranges, idx)))
        candPredExpr = adaptArg(candPred)
        if samePred:
            from . import treefunctions as op
            areDiff = op.AND(*(
                samePred(ra._getItem(ia.result), rb._getItem(ib.result))
                for ((ia, ra), (ib, rb)) in combinations(zip(idx, ranges), 2)
                if ra._base == rb._base))
            if len(areDiff.op.args) > 0:
                candPredExpr = adaptArg(op.AND(areDiff, candPred))
        maxLVIdx = _maxLVIdx(candPredExpr)
        for i, ilvp in enumerate(idx):
            ilvp.i = maxLVIdx + 1 + i
        res = Combine(tuple(adaptArg(rng.idxs) for rng in ranges), candPredExpr, idx)
        for ilvp in idx:
            ilvp._parent = res
        from .treeproxies import CombinationListProxy
        return CombinationListProxy(ranges, res)

    def deps(self, defCache=cppNoRedir, select=(lambda x: True), includeLocal=False):
        if not defCache.stop(self):
            for arg in chain(self.rng, [self.candPredExpr]):
                if select(arg) and (includeLocal or arg not in self._i):
                    yield arg
                for dp in arg.deps(defCache=defCache, select=select, includeLocal=includeLocal):
                    if includeLocal or dp not in self._i:
                        yield dp

    def _repr(self):
        return f"{self.__class__.__name__}({self.rng!r}, {self.candPredExpr!r}, {self._i!r})"

    def _hash(self, fun=op_hash):
        return fun(*chain([self.__class__.__name__], self.rng, [self.candPredExpr], self._i))

    def _eq(self, other):
        return (equal_elements(self.rng, other.rng) and self.candPredExpr == other.candPredExpr
                and self._i == other._i)

    def get_cppStr(self, defCache=cppNoRedir):
        _triggerDefinitions(self, defCache=defCache)
        captures, _, _, _ = _convertFunArgs(_collectDeps(self, defCache=defCache), defCache=defCache)
        return (
            "rdfhelpers::combine(\n"
            "     [{captures}] ( {predIdxArgs} ) {{ return {predExpr}; }},\n"
            "     {ranges})").format(
                captures=",".join(captures),
                predIdxArgs=", ".join(f"{i.typeName} {i.name}" for i in self._i),
                predExpr=defCache(self.candPredExpr),
                ranges=", ".join(defCache(rng) for rng in self.rng)
        )


# FIXME to be implemented
class PseudoRandom(TupleOp):
    """ Pseudorandom number (integer or float) within range """
    def __init__(self, xMin, xMax, seed, isIntegral=False):
        super().__init__()
        self.xMin = xMin
        self.xMax = xMax
        self.seed = seed
        self.isIntegral = isIntegral

    @property
    def resultType(self):
        return "Int_" if self.isIntegral else "Float_t"
    # deps from xMin, xMax and seed
    # seed can be event-based or object-based, depending?
    # TODO implement C++ side as well


class OpWithSyst(ForwardingOp):
    """
    Interface and base class for nodes that can change the systematic variation
        of something they wrap
    """
    def __init__(self, wrapped, variations=None):
        super().__init__(wrapped)
        self.variations = variations

    def _clone(self, memo, select, selClones=None):
        clWr = self.wrapped.clone(memo=memo, select=select, selClones=selClones)
        isSel = select(self)
        if isSel or id(clWr) != id(self.wrapped):
            cln = self.__class__(clWr, variations=self.variations)
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def changeVariation(self, newVariation):
        """ Assumed to be called on a fresh copy - *will* change the underlying value
        """
        if self._cache:  # validate this assumption
            raise RuntimeError("Cannot change variation of an expression that is already frozen")
        if newVariation not in self.variations:
            raise ValueError(f"Invalid variation: {newVariation}")
        self._changeVariation(newVariation)

    def _changeVariation(self, newVariation):
        """
        changeVariation specifics (after validating newVariation, and changability) -
            to be implemented by concrete classes
        """
        pass

    def _repr(self):
        return "{}({!r}, {!r}, {!r})".format(self.__class__.__name__, self.wrapped, self.variations)

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.wrapped, str(self.variations))

    def _eq(self, other):
        return super()._eq(other) and self.variations == other.variations


class SystAltOp(OpWithSyst):
    """ Change the wrapped operation (from a map) """
    def __init__(self, wrapped, varMap, valid=None):
        super().__init__(wrapped)
        self.variations = valid if valid is not None else tuple(varMap.keys())
        self.varMap = varMap

    def _clone(self, memo, select, selClones=None):
        clWr = self.wrapped.clone(memo=memo, select=select, selClones=selClones)
        varCl = {nm: vop.clone(memo=memo, select=select, selClones=selClones)
                 for nm, vop in self.varMap.items()}
        isSel = select(self)
        if (isSel or id(clWr) != id(self.wrapped)
                or any(id(vCl) != id(self.varMap[ky]) for ky, vCl in varCl.items())):
            cln = self.__class__(clWr, varCl, valid=tuple(self.variations))
            if selClones is not None and isSel:
                selClones.append(cln)
            return cln

    def _repr(self):
        return f"{self.__class__.__name__}({self.wrapped!r}, {self.variations!r}, {self.varMap!r})"

    def _hash(self, fun=op_hash):
        return fun(self.__class__.__name__, self.wrapped, str(self.variations),
                   *chain.from_iterable(self.varMap.items()))

    def _eq(self, other):
        return super()._eq(other) and self.variations == other.variations and self.varMap == other.varMap

    def _changeVariation(self, newVariation):
        if newVariation in self.varMap:
            self.wrapped = self.varMap[newVariation]
            self.typeName = self.wrapped.typeName


class DefineOnFirstUse(ForwardingOp):
    """ Node marked for definition as a column on first use """
    __slots__ = tuple()

    def __init__(self, wrapped, canDefine=None):
        super().__init__(wrapped, canDefine=canDefine)


def collectSystVars(exprs):
    # { varName : { expr : [ nodes to change ] } }
    systVars = defaultdict(dict)
    for expr in exprs:
        toChangeForThis = defaultdict(list)
        for nd in set(collectNodes(expr,
                                   select=(lambda nd: isinstance(nd, OpWithSyst) and nd.variations),
                                   defCache=VisitOnceAndStopAt())):
            for vari in nd.variations:
                toChangeForThis[vari].append(nd)
        for vari, variNodes in toChangeForThis.items():
            systVars[vari][expr] = variNodes
    return systVars
