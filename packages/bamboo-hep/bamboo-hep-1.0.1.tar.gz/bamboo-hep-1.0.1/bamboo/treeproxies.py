"""
Wrapper classes for TTree/ROOT::RDataFrame

The goal is to make it easier to work with flat trees by generating structs
"on the fly", and allow postponing evaluation to a later stage
(as in RDataFrame, or previously with a code-generating backend).
This is done by providing proxy objects to parts of the record content,
and "operations" derived from these, which are again wrapped in proxies,
to allow easy constructing the expression tree for the backend.
As an example: 'myTreeProxy.event_id' will return an integer proxy,
with as 'op' attribute a 'GetColumn(tree, "event_id")' operation.
"""

import functools
import re

from . import treeoperations as top
from .treeoperations import SizeType, TupleBaseProxy, adaptArg

_boolTypes = {"bool", "Bool_t"}
_integerTypes = {
    "Int_t", "UInt_t", "Char_t", "UChar_t", "ULong64_t", "int", "unsigned", "unsigned short",
    "char", "signed char", "unsigned char", "long", "Short_t", "size_t", "std::size_t",
    "unsigned short", "unsigned long"}
_floatTypes = {"Float_t", "Double_t", "float", "double"}
# TODO lists are probably not complete
vecPat = re.compile(r"(?:vector|ROOT\:\:VecOps\:\:RVec)\<(?P<item>[a-zA-Z_0-9\<\>\: \*]+)(,[a-zA-Z_0-9\<\>,\: \*]+)?\>$")  # noqa: 501


def makeProxy(op):
    if op.typeName in _boolTypes:
        return BoolProxy(op)
    elif op.typeName in _integerTypes:
        return IntProxy(op)
    elif op.typeName in _floatTypes:
        return FloatProxy(op)
    else:
        m = vecPat.match(op.typeName)
        if m:
            return VectorProxy(op, itemType=m.group("item"))
        else:
            return ObjectProxy(op)


def makeConst(value, typeHint):
    return makeProxy(adaptArg(value, typeHint))


class NumberProxy(TupleBaseProxy):
    def __init__(self, parent):
        super().__init__(parent)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._parent!r})"

    def _binaryOp(self, opName, other, reverseOrder=False):
        if reverseOrder:
            return top.MathOp(opName, other, self).result
        return top.MathOp(opName, self, other).result

    def _unaryOp(self, opName):
        return top.MathOp(opName, self)


for nm, opNm in {
        "__add__": "add",
        "__sub__": "subtract",
        "__mul__": "multiply",
        "__pow__": "pow",
        "__radd__": "add",
        "__rmul__": "multiply"}.items():
    setattr(NumberProxy, nm, functools.partialmethod(
        (lambda self, oN, other: self._binaryOp(oN, other)), opNm))
for nm, opNm in {
        "__rsub__": "subtract",
        "__rpow__": "rpow"}.items():
    setattr(NumberProxy, nm, functools.partialmethod(
        (lambda self, oN, other: self._binaryOp(oN, other, reverseOrder=True)), opNm))
for nm in ("__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__"):
    setattr(
        NumberProxy, nm,
        (lambda oN: (lambda self, other: self._binaryOp(oN, other)))(nm.strip("_")))
for name in ("__neg__",):
    setattr(NumberProxy, name, functools.partialmethod(
        (lambda self, oN: self._unaryOp(oN)), name.strip("_")))


class IntProxy(NumberProxy):
    def __init__(self, parent):
        super().__init__(parent)


for nm, opNm in {
        "__truediv__": "floatdiv",
        "__floordiv__": "divide",
        "__mod__": "mod",
        "__lshift__": "lshift",
        "__rshift__": "rshift",
        "__and__": "band",
        "__or__": "bor",
        "__xor__": "bxor",
        "__rand__": "band",
        "__ror__": "bor",
        "__rxor__": "bxor"}.items():
    setattr(IntProxy, nm, functools.partialmethod(
        (lambda self, oN, other: self._binaryOp(oN, other)),
        opNm))
for nm, opNm in {
        "__rtruediv__": "floatdiv",
        "__rfloordiv__": "divide",
        "__rmod__": "mod",
        "__rlshift__": "lshift",
        "__rrshift__": "rshift"}.items():
    setattr(IntProxy, nm, functools.partialmethod(
        (lambda self, oN, other: self._binaryOp(oN, other, reverseOrder=True)),
        opNm))
for name, opName in {"__invert__": "bnot"}.items():
    setattr(IntProxy, name, functools.partialmethod(
        (lambda self, oN: self._unaryOp(oN)), opName))


class BoolProxy(IntProxy):
    """ Proxy for a boolean type """
    def __init__(self, parent):
        super().__init__(parent)

    def __repr__(self):
        return f"BoolProxy({self._parent!r})"


for nm, opNm in {
        "__and__": "and",
        "__or__": "or",
        "__invert__": "not",
        "__xor__": "ne",
        "__rand__": "and",
        "__ror__": "or",
        "__rxor__": "ne"}.items():
    setattr(BoolProxy, nm, functools.partialmethod(
        (lambda self, oN, oT, other: self._binaryOp(oN, other)), opNm))
for name, opName in {"__invert__": "not"}.items():
    setattr(BoolProxy, name, functools.partialmethod(
        (lambda self, oN: self._unaryOp(oN)), opName))


class FloatProxy(NumberProxy):
    def __init__(self, parent):
        super().__init__(parent)


for nm, opNm in {"__truediv__": "floatdiv"}.items():
    setattr(FloatProxy, nm, functools.partialmethod(
        (lambda self, oN, other: self._binaryOp(oN, other)),
        opNm))
for nm, opNm in {"__rtruediv__": "floatdiv"}.items():
    setattr(FloatProxy, nm, functools.partialmethod(
        (lambda self, oN, other: self._binaryOp(oN, other, reverseOrder=True)),
        opNm))


class ArrayProxy(TupleBaseProxy):
    """ (possibly var-sized) array of anything """
    def __init__(self, parent, valueType, length):
        super().__init__(parent)
        self._length = length
        self.valueType = valueType

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.step and index.step != 1:
                raise RuntimeError("Slices with non-unit step are not implemented")
            return SliceProxy(self, index.start, index.stop, valueType=self.valueType)
        else:
            return top.GetItem(self, self.valueType, index).result

    def __len__(self):
        return self._length

    def __repr__(self):
        return f"ArrayProxy({self._parent!r}, {self._typeName!r}, {self._length!r})"


class LeafGroupProxy(TupleBaseProxy):
    """ Base class for proxies with a prefix (leaf group, container) """
    def __init__(self, prefix, parent):
        super().__init__(parent)
        self._prefix = prefix

    def __repr__(self):
        return f"{self.__class__.__name__}({self._prefix!r}, {self._parent!r})"


def fullPrefix(prefix, parent):  # TODO check if we actually need it (probably yes for nested)
    if parent:
        return "".join(fullPrefix(parent._prefix, parent._parent), prefix)
    else:
        return prefix


class TreeBaseProxy(LeafGroupProxy):
    """ Tree proxy base class """
    def __init__(self, tree):
        self._tree = tree
        super().__init__("", None)

    @property
    def op(self):
        return None

    def __repr__(self):
        return f"{self.__class__.__name__}({self._tree!r})"

    def deps(self, defCache=None, select=(lambda x: True), includeLocal=False):
        yield from []

    def __eq__(self, other):
        return self._tree == other._tree

    def __deepcopy__(self, memo):
        # *never* copy the TTree, although copying proxies is fine
        return self.__class__(self._tree)


class ListBase:
    """ Interface definition for range proxies (Array/Vector, split object vector, selection/reordering)

    Important for users: _base always contains a basic container (e.g. ContainerGroupProxy), and idxs
    the indices out of _base this list contains (so _base[idxs[i]] for i in range(len) are always valid).

    TODO verify / stress-tests (selection of selection, next of selection of selection etc.)
    """
    def __init__(self):
        self.valueType = None
        self._base = self  # TODO get rid of _
        super().__init__()

    def __getitem__(self, index):
        """ Get item using index of this range """
        if isinstance(index, slice):
            if index.step and index.step != 1:
                raise RuntimeError("Slices with non-unit step are not implemented")
            return SliceProxy(self, index.start, index.stop, valueType=self.valueType)
        else:
            return self._getItem(adaptArg(index, SizeType))

    def _getItem(self, baseIndex):
        """ Get item using index of base range """
        return self._base[baseIndex]

    def __len__(self):
        pass  # need overridde

    @property
    def idxs(self):
        # FIXME uint->int narrowing
        return top.Construct(f"rdfhelpers::IndexRange<{SizeType}>", (adaptArg(self.__len__()),)).result


class ItemProxyBase(TupleBaseProxy):
    """ Proxy for an item in some container """
    def __init__(self, parent):
        # NOTE subclasses should define _idx and _base
        super().__init__(parent)

    @property
    def idx(self):
        return self._idx.result

    @property
    def isValid(self):
        return self.idx != -1

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise RuntimeError(
                "Cannot compare proxies of different types: "
                f"{other.__class__.__name__} and {self.__class__.__name__}")
        if self._base != other._base:
            raise RuntimeError("Cannot compare elements from different containers")
        return self.idx == other.idx

    def __ne__(self, other):
        from bamboo.treefunctions import NOT
        return NOT(self == other)


class ContainerGroupItemProxy(ItemProxyBase):
    """ Proxy for an item in a structure of arrays """
    def __init__(self, parent, idx):
        self._idx = adaptArg(idx, typeHint=SizeType)
        super().__init__(parent)

    @property
    def _base(self):
        return self._parent._base

    def __repr__(self):
        return f"{self.__class__.__name__}({self._parent!r}, {self._idx!r})"


class ContainerGroupProxy(LeafGroupProxy, ListBase):
    """ Proxy for a structure of arrays """
    def __init__(self, prefix, parent, size, valueType):
        ListBase.__init__(self)
        self._size = size
        self.valueType = valueType
        super().__init__(prefix, parent)

    def __len__(self):
        return self._size.result

    def _getItem(self, baseIndex):
        return self.valueType(self, baseIndex)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._parent!r}, {self._size!r})"


class ObjectProxy(NumberProxy):
    """
    Imitate an object
    """
    __slots__ = ("_isPointer",)

    def __init__(self, parent):
        super().__init__(parent)
        self._isPointer = self._typeName.endswith("*")

    @property
    def _typ(self):
        from .root import gbl
        try:
            typeName = self._typeName
            if self._isPointer:
                typeName = typeName[:-1]
            ret = getattr(gbl, typeName)
        # if the above raises an AttributeError, __getattr__ will be called, resulting in infinite recursion
        except AttributeError as e:
            raise RuntimeError(e)
        else:
            return ret

    def __getattr__(self, name):
        typ = self._typ
        if name not in dir(typ):
            raise AttributeError(f"Type {self._typeName} has no member {name}")
        from .root import gbl
        if hasattr(typ, name) and (
                (isinstance(getattr(typ, name), gbl.MethodProxy)
                    if hasattr(gbl, "MethodProxy")
                    else getattr(typ, name).__class__.__name__ == "CPPOverload")
                or ((hasattr(gbl, "TemplateProxy") and isinstance(getattr(typ, name), gbl.TemplateProxy))
                    or (type(getattr(typ, name)).__name__ == "TemplateProxy"))):
            return ObjectMethodProxy(self, name)
        else:
            return top.GetDataMember(self, name, byPointer=self._isPointer).result

    def __call__(self, *args):
        if callable(self._typ):
            return top.CallMemberMethod(self, "__call__", args, byPointer=self._isPointer).result
        else:
            raise RuntimeError(f"No operator() for type {self._typeName}")

    def __repr__(self):
        return f"ObjectProxy({self._parent!r})"


class ObjectMethodProxy(TupleBaseProxy):  # TODO data members?
    """
    Imitate a member method of an object
    """
    __slots__ = ("_objStb", "_name")

    def __init__(self, objStb, name):
        self._objStb = objStb
        self._name = name
        super().__init__(None)

    def __call__(self, *args, **kwargs):
        # TODO maybe this is a good place to resolve the right overload? or do some arguments checking
        return top.CallMemberMethod(
            self._objStb, self._name, tuple(args), byPointer=self._objStb._isPointer,
            returnType=kwargs.get("returnType")).result

    def __repr__(self):
        return f"ObjectMethodProxy({self._objStb!r}, {self._name!r})"


class MethodProxy(TupleBaseProxy):
    """
    Imitate a free-standing method
    """
    __slots__ = ("_name", "_returnType", "_getFromRoot")

    def __init__(self, name, returnType=None, getFromRoot=True):
        self._name = name
        self._returnType = returnType
        self._getFromRoot = getFromRoot
        super().__init__(None)

    def __call__(self, *args):
        # TODO maybe this is a good place to resolve the right overload? or do some arguments checking
        return top.CallMethod(
            self._name, tuple(args), returnType=self._returnType,
            getFromRoot=self._getFromRoot).result

    def __repr__(self):
        return f"MethodProxy({self._name!r})"


class VectorProxy(ObjectProxy, ListBase):
    """ Vector-as-array (maybe to be eliminated with var-array branches / generalised into object) """
    def __init__(self, parent, itemType=None):
        ListBase.__init__(self)
        if itemType:
            self.valueType = itemType
        else:
            from .root import gbl
            vecClass = getattr(gbl, parent.typeName)
            if hasattr(vecClass, "value_type"):
                value = vecClass.value_type
                if hasattr(value, "__cpp_name__"):
                    self.valueType = value.__cpp_name__
                elif str(value) == value:
                    self.valueType = value
                else:
                    raise RuntimeError(
                        f"value_type attribute of {parent.typeName} is neither "
                        f"a PyROOT class nor a string, but {value}")
            else:
                self.valueType = vecPat.match(parent.typeName).group("item")
        super().__init__(parent)

    def _getItem(self, index):
        return top.GetItem(self, self.valueType, index).result

    def __len__(self):
        return self.size()

    def __repr__(self):
        return f"VectorProxy({self._parent!r}, {self.valueType!r})"


class SelectionProxy(TupleBaseProxy, ListBase):
    """ Proxy for a selection from an iterable (ContainerGroup/ other selection etc.) """
    def __init__(self, base, parent, valueType=None):  # 'parent' is a Select or Sort TupleOp
        ListBase.__init__(self)
        self._base = base
        self.valueType = valueType if valueType else self._base.valueType
        # the list of indices is stored as the parent
        super().__init__(parent)

    @property
    def _typeName(self):
        return None

    @property
    def idxs(self):
        return self._parent.result

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.step and index.step != 1:
                raise RuntimeError("Slices with non-unit step are not implemented")
            return SliceProxy(self, index.start, index.stop, valueType=self.valueType)
        else:
            return self._getItem(self.idxs[index])

    def _getItem(self, baseIndex):
        itm = self._base[baseIndex]
        if self.valueType and self.valueType != self._base.valueType:
            return self.valueType(itm._parent, itm._idx)
        else:
            return itm

    def __len__(self):
        return self.idxs.__len__()

    def __repr__(self):
        return f"SelectionProxy({self._base!r}, {self._parent!r}, valueType={self.valueType!r})"


class SliceProxy(TupleBaseProxy, ListBase):
    """ Proxy for part of an iterable (ContainerGroup/selection etc.) """
    def __init__(self, parent, begin, end, valueType=None):
        # 'parent' is another proxy (ListBase, will become _base of this one)
        ListBase.__init__(self)
        self.parent = parent  # parent proxy (slices are always created with a proxy)
        self._base = parent._base if parent is not None else None
        self._begin = adaptArg(begin, SizeType).result if begin is not None else None  # None signals 0
        self._end = (
            adaptArg(end, SizeType).result if end is not None
            else makeConst(parent.__len__(), SizeType))
        self.valueType = valueType if valueType else parent.valueType
        super().__init__(adaptArg(parent) if parent is not None else None)

    @property
    def _typeName(self):
        return None

    def _offset(self, idx):
        # from index in slice to index in slice's parent
        if self._begin is not None:
            return self._begin + idx
        else:
            return idx

    @property
    def begin(self):
        if self._begin:
            return self._begin
        else:
            return makeConst(0, SizeType)

    def __getitem__(self, key):
        if isinstance(key, slice):
            # slice of a slice: just adjust the range
            if key.step and key.step != 1:
                raise RuntimeError("Slices with non-unit step are not implemented")
            return SliceProxy(
                self.parent,
                (self._offset(key.start) if key.start is not None else self._begin),
                (self._offset(key.stop) if key.stop is not None else self._end),
                valueType=self.valueType)
        else:
            # item of a slice -> ask parent
            itm = self.parent[self._offset(key)]
            if self.valueType and self.valueType != self.parent.valueType:
                itm = self.valueType(itm._parent, itm._idx)
            return itm

    @property
    def idxs(self):
        return top.Construct(
            f"rdfhelpers::IndexRangeSlice<{SizeType},{self.parent.idxs._typeName}::const_iterator>",
            (self.parent.idxs.begin(),
                (self._begin if self._begin is not None else 0), self._end)).result

    def _getItem(self, baseIndex):  # correct but not used by __getitem__
        # (finding base index depends on self.parent, could be anything)
        itm = self.parent._getItem(baseIndex)
        if self.valueType and self.valueType != self.parent.valueType:
            itm = self.valueType(itm._parent, itm._idx)
        return itm

    def __len__(self):
        return self._end - self.begin

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self._parent!r}, "
            f"{self._begin!r}, {self._end!r}, valueType={self.valueType!r})")


class AltLeafVariations(TupleBaseProxy):
    """ Branch with alternative names """
    def __init__(self, parent, brMap):
        super().__init__(parent)
        self.brMap = brMap

    @property
    def _typeName(self):
        return self.brMap["nomWithSyst"].typeName

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise ValueError(f"Getting variation with non-string key {key!r}")
        if key not in self.brMap:
            raise KeyError(f"No such variation: {key}")
        return self.brMap[key].result


class AltLeafGroupVariations(TupleBaseProxy):
    """ Set of groups with alternative names for some branches """
    def __init__(self, parent, orig, brMapMap, altProxyType):
        self.orig = orig
        self.brMapMap = brMapMap
        self.altProxyType = altProxyType
        super().__init__(parent)

    @property
    def _typeName(self):
        return None

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise ValueError(f"Getting variation with non-string key {key!r}")
        if key not in self.brMapMap:
            raise KeyError(f"No such variation: {key}")
        return self.altProxyType(self._parent, self.orig, self.brMapMap[key])


class AltLeafGroupProxy(TupleBaseProxy):
    """ Group with alternative names for some branches """
    # base class like LeafGroupProxy, but with a brMap
    def __init__(self, parent, orig, brMap, typeName="struct"):
        self.orig = orig
        self.brMap = brMap
        super().__init__(parent)

    @property
    def _typeName(self):
        return self.brMap.get("nomWithSyst", next(self.brMap.values())).typeName

    def __repr__(self):
        return f"{self.__class__.__name__}({self._parent!r}, {self.brMap!r})"


class AltCollectionVariations(TupleBaseProxy):
    """ Set of collections with alternative names for some branches """
    def __init__(self, parent, orig, brMapMap, altItemType=None):
        self.orig = orig
        self.brMapMap = brMapMap
        self.altItemType = altItemType if altItemType else orig.valueType
        super().__init__(parent)

    @property
    def _typeName(self):
        return None

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise ValueError(f"Getting variation with non-string key {key!r}")
        if key not in self.brMapMap:
            raise KeyError(
                f"No such variation: {key}. If stored on the NanoAOD: "
                "are the branch names in the correct format; "
                "if calculated on the fly: has the calculator been configured?")
        return AltCollectionProxy(
            self._parent, self.orig, self.brMapMap[key], itemType=self.altItemType)


class AltCollectionProxy(TupleBaseProxy, ListBase):
    """ Collection with alternative names for some branches """
    def __init__(self, parent, orig, brMap, itemType=None):
        ListBase.__init__(self)
        self.orig = orig
        self.valueType = orig.valueType  # for ListBase
        self.itemType = itemType  # for actual items
        self.brMap = brMap
        super().__init__(parent)

    @property
    def _typeName(self):
        return None

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.step and index.step != 1:
                raise RuntimeError("Slices with non-unit step are not implemented")
            return SliceProxy(self, index.start, index.stop, valueType=self.valueType)
        else:
            return self.itemType(self, index)

    def __len__(self):
        return self.orig.__len__()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._parent!r}, {self.brMap!r}, {self.itemType!r})"


class CalcVariationsBase:
    """ extra base class for AltCollectionVariations or AltLeafGroupVariations with calculator """
    def __init__(self, withSystName=None):
        self.calc = None
        self.calcProd = None
        self.withSystName = withSystName

    def _initCalc(self, calcProxy, calcHandle=None, args=None):
        self.calc = calcHandle  # handle to the actual module object
        import bamboo.treefunctions as op
        # define on-demand (does nothing if done explicitly) to limit worst-case behaviour
        self.calcProd = op.defineOnFirstUse(calcProxy.produce(*args))

    def _available(self, att=""):
        return list(str(iav) for iav in self.calc.available(att))

    def _initFromCalc(self):
        for attN in self.brMapMap[self.withSystName].keys():
            for i, nm in enumerate(self._available(attN)):
                if nm not in self.brMapMap:
                    self.brMapMap[nm] = dict()
                self.brMapMap[nm][attN] = adaptArg(
                    getattr(self.calcProd, attN)(
                        top.Parameter(SizeType, f"{i:d}ul").result))
        nonVarNames = (self.withSystName, "nominal", "raw")
        for attN in self.brMapMap[self.withSystName].keys():
            self.brMapMap[self.withSystName][attN] = top.SystAltOp(
                self.brMapMap["nominal"][attN],
                {var: brMap[attN] for var, brMap in self.brMapMap.items()
                 if var not in nonVarNames and attN in brMap},
                valid=[vr for vr in self.brMapMap.keys()
                       if vr not in nonVarNames])


class CalcLeafGroupVariations(AltLeafGroupVariations, CalcVariationsBase):
    """ Set of groups with alternative names for some branches, with calculator """
    def __init__(self, parent, orig, brMapMap, altProxyType, withSystName=None):
        super().__init__(parent, orig, brMapMap, altProxyType)
        CalcVariationsBase.__init__(self, withSystName=withSystName)


class CalcCollectionVariations(AltCollectionVariations, CalcVariationsBase):
    """ Set of collections with alternative names for some branches, with calculator """
    def __init__(self, parent, orig, brMapMap, altItemType=None, withSystName=None):
        super().__init__(parent, orig, brMapMap, altItemType=altItemType)
        CalcVariationsBase.__init__(self, withSystName=withSystName)


class CombinationProxy(ItemProxyBase, ListBase):
    """ Decorated combinations item """
    def __init__(self, cont, parent):
        self.cont = cont
        ItemProxyBase.__init__(self, parent)  # parent is a GetItem
        ListBase.__init__(self)
        if self.cont.isFromSameCollection:
            self._base = self.cont.base(0)
            self.valueType = self.cont.ranges[0].valueType
        else:
            self._base = None

    @property
    def _typeName(self):
        return None

    @property
    def _idx(self):
        return self._parent._index

    def __repr__(self):
        return f"{self.__class__.__name__}({self.cont!r}, {self._parent!r})"

    def __len__(self):
        return makeConst(len(self.cont.ranges), SizeType)

    @property
    def idxs(self):
        if not self.cont.isFromSameCollection:
            raise RuntimeError("Combination can only be used as a range "
                               "if all elements come from the same collection")
        from .treefunctions import defineOnFirstUse
        return defineOnFirstUse(self._parent.result.asRange())

    @property
    def asRange(self):
        # self.idxs will trigger equality check
        return SelectionProxy(self._base, adaptArg(self.idxs), valueType=self.valueType)

    def _getItem(self, i):
        return self.asRange._getItem(i)

    def __getitem__(self, i):
        if isinstance(i, int):  # compile-time, always works
            idx = makeConst(i, SizeType)
            return self.cont.base(i)[self._parent.result.get(idx)]
        else:  # try to interpret as a range (only if from the same base)
            return self.asRange[i]

    def __iter__(self):
        for i in range(len(self.cont.ranges)):
            yield self[i]


class CombinationListProxy(TupleBaseProxy, ListBase):
    # NOTE list of decorated rdfhelpers::Combination
    def __init__(self, ranges, parent):
        ListBase.__init__(self)
        self.valueType = CombinationProxy
        self.ranges = ranges
        super().__init__(parent)

    @property
    def _typeName(self):
        return None

    def _getItem(self, idx):
        return CombinationProxy(self, adaptArg(self._parent.result[idx]))

    def base(self, i):
        return self.ranges[i]._base

    def __len__(self):
        return self._parent.result.size()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.ranges!r})"

    @property
    def isFromSameCollection(self):
        return all(rng._base == self.ranges[0]._base for rng in self.ranges)
