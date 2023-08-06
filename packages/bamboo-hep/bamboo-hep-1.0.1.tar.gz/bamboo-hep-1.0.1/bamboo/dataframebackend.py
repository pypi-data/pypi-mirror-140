"""
ROOT::RDataFrame backend classes
"""
import logging
import os.path
import shutil
import subprocess
import tempfile
from collections import defaultdict
from functools import partial
from itertools import chain
from timeit import default_timer as timer

import numpy as np
import pkg_resources

import bamboo.plots

from . import root
from . import treeoperations as top
from .plots import FactoryBackend, Selection, SelectionWithSub, Skim

# copied from https://docs.python.org/3/howto/logging-cookbook.html#use-of-alternative-formatting-styles


class Message:
    def __init__(self, fmt, args):
        self.fmt = fmt
        self.args = args

    def __str__(self):
        return self.fmt.format(*self.args)


class StyleAdapter(logging.LoggerAdapter):
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})

    def log(self, level, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger._log(level, Message(msg, args), (), **kwargs)


logger = StyleAdapter(logging.getLogger(__name__))

_RDFNodeStats = defaultdict(int)
_RDFHistoNDStats = defaultdict(int)
_RDFHistoND_methods = dict()
# _RDFHistoND_methods[kyTypes] = getattr(gbl.rdfhelpers.rdfhistofactory,
#                                        f"Histo{nVars:d}D")[tuple(templTypes)]


def _printStats():
    logger.info(
        "Number of uses per node type: {}".format(
            ", ".join(f"{num:d} {ndTp}" for ndTp, num in _RDFNodeStats.items())))
    if _RDFHistoNDStats:
        logger.debug(
            "HistoND calls per column type: {}".format(
                ", ".join("{1:d} {0} -> {2};{3}".format(
                    kyTypes[0], num, ",".join(kyTypes[1]),
                    (kyTypes[2] if len(kyTypes) > 2 else ""))
                    for kyTypes, num in _RDFHistoNDStats.items())))
    if _RDFHistoND_methods:
        logger.debug(
            "HistoND helper instantiations: {}".format(
                ", ".join("{0}::Histo{2:d}D<{1}>".format(
                    kyTypes[0],
                    ",".join(list(kyTypes[1]) + ([kyTypes[2]] if len(kyTypes) > 2 else [])),
                    len(kyTypes[1]))
                    for kyTypes in _RDFHistoND_methods.keys())))


def _resetStats():
    global _RDFNodeStats
    global _RDFHistoNDStats
    global _RDFHistoND_methods
    _RDFNodeStats = defaultdict(int)
    _RDFHistoNDStats = defaultdict(int)
    _RDFHistoND_methods = dict()


class ExprWithName:
    """ Small helper to keep track of already-defined columns (with their name) """
    __slots__ = ("name", "op")

    def __init__(self, name, op):
        self.name = name
        self.op = op


class FilterWithDefines(top.CppStrRedir):
    """
    Branching point in the RDF graph: a Filter and the Define nodes attached to it

    Only when cuts are added, branching is done (may be multiple, if systematics-dependent).
    A proto-RDF-graph of FilterWithDefines nodes is built up by the backend as selections
    and plots are construction, but construction of the actual RDF nodes can be delayed
    (explicitly defined columns are also kept track of, while other 'shouldDefine' columns
    are still defined on-demand).
    """
    def __init__(self, parent, cut=None):
        self.explDefines = dict()
        self.var = None  # nodes for related systematic variations (if different by more than the weight)
        self.children = dict()
        if isinstance(parent, FilterWithDefines):
            self.parent = parent
            self.backend = parent.backend
            self.cut = cut
            self.digest = parent.digest  # updated if there are cuts (see below)
        elif isinstance(parent, DataframeBackend):
            self.parent = None
            self.backend = parent
            self.digest = top.op_digest("RDF::Filter")
        else:
            raise RuntimeError(
                "Can only define FilterWithDefines with a DataframeBackend "
                "or another FilterWithDefines")
        self._df = None
        self._definedColumns = dict()
        top.CppStrRedir.__init__(self)

    @property
    def df(self):
        if self._df is None:
            if self.parent is None:
                self._df = self.backend.rootDF
            else:
                self.parent.df  # construct parent RDF nodes first (if still needed)
                # trick: by doing this *before* constructing the nominal node, any definitions
                # end up in the node above, and are in principle available for other sub-selections too
                cutStr = self.cut.get_cppStr(defCache=self.parent)
                logger.debug(
                    f"FilterWithDefines with digest {top.hexStr_digest(self.digest)}: "
                    f"filtering with {cutStr}")
                self._df = self.backend.df_filter(self.parent.df, cutStr, self.cut, self.parent)
                # important - columns defined later with the parent will be invisible to the children
                self._definedColumns = dict(self.parent._definedColumns)
            for expr, nm in self.explDefines.items():
                if not self.getColName(expr):
                    self.define(expr, name=nm)
        return self._df

    @df.setter
    def df(self, arg):
        self._df = arg

    def childWithCuts(self, cuts):
        cutExpr = Selection._makeExprAnd(cuts)
        if cutExpr not in self.children:
            # branching the RDataFrame graph here (lazily)
            newNd = FilterWithDefines(self, cutExpr)
            newNd.digest = top.op_digest(self.digest, cutExpr)
            self.children[cutExpr] = newNd
            logger.debug(f"Created child FilterWithDefines  with digest {top.hexStr_digest(newNd.digest)}")
        else:
            logger.debug(f"Re-using child FilterWithDefines with digest {top.hexStr_digest(self.digest)}")
        return self.children[cutExpr]

    def getColName(self, op):
        if op in self._definedColumns:
            return self._definedColumns[op]
    stop = getColName  # column depedendencies

    def expl_define(self, expr, name=None):
        """ explicitly define column for expression """
        if self._df is not None and not self.getColName(expr):
            self.define(expr, name)
        elif expr not in self.explDefines:
            self.explDefines[expr] = name

    def shouldDefine(self, arg):
        return self.backend.shouldDefine(arg, defCache=self)

    def define(self, expr, name=None):
        """ Define as a new column (not checked, use getColName first) """
        if name is None:
            name = self.backend.getUColName()
        if expr in self._definedColumns:
            cppStr = self(expr)  # corner case: define with a new name
        else:
            cppStr = expr.get_cppStr(defCache=self)
        self.df = self.backend.df_define(self.df, name, cppStr, expr, self)
        self._definedColumns[expr] = name
        return name

    def symbol(self, decl, **kwargs):
        return self.backend.symbol(decl, **kwargs)

    def __call__(self, arg):
        """ Get the C++ string corresponding to an op """
        if not self._df:
            self.df  # need to be constructed here
        nm = self.getColName(arg)
        if not nm:
            if not self.shouldDefine(arg):
                try:
                    nm = arg.get_cppStr(defCache=self)
                except Exception as ex:
                    logger.exception("Could not get cpp string for {0!r}: {1!r}", arg, ex)
                    nm = "NONE"
            else:
                nm = self.define(arg)
        return nm

    def makeWeight(self, weights, wName=None, parentWeight=None):
        if parentWeight is not None:
            weights = [parentWeight] + list(weights)
        weight = Selection._makeExprProduct(weights)
        if not (isinstance(weight, top.GetColumn) or (isinstance(weight, top.ForwardingOp)
                                                      and isinstance(weight.wrapped, top.GetColumn))):
            self.expl_define(weight, name=wName)
        return weight


class SelectionHelper:
    # for lack of a better name... will keep the weight(s) for a selection and
    # the FilterWithDefines ref (can be the same for different Selections and SelectionHelpers)
    def __init__(self, fdnd):
        self.fdnd = fdnd  # FilterWithDefines-node reference
        self.weight = dict()


# NOTE these are global (for the current process&interpreter)
# otherwise they would be overwritten in sequential mode (this even allows reuse)
_gSymbols = dict()
_giFun = 0


def _normFunArgs(expr, args, argNames):
    newExpr = expr
    newArgs = args
    for i, argN in sorted(list(enumerate(argNames)), key=(lambda elm: len(elm[1])), reverse=True):
        newName = f"myArg{i:d}"
        if " " in argN:  # parameter-like, with a comment
            if sum(1 for ia in newArgs if argN in ia) != 1:  # should be in one and only one argument
                raise RuntimeError(f"{argN} is in more than one (or none) of {newArgs}")
            newArgs = [(ia.replace(argN, newName) if argN in ia else ia) for ia in newArgs]
        else:  # just a column name
            newArgs = [(" ".join((newName if tk == argN else tk) for tk in ia.split())
                        if argN in ia else ia) for ia in newArgs]
        newExpr = newExpr.replace(argN, newName)
    return newExpr, newArgs


def makeHistoName(plot, variation="nominal"):
    name = plot.name
    if variation != "nominal":
        name = "__".join((name, variation))
    return name


def _adjustBinnings(binnings):
    # high-dimensional histo models require either all or none of the binnings to be uniform
    if len(binnings) > 1:
        from .plots import EquidistantBinning, VariableBinning
        if any(isinstance(b, VariableBinning) for b in binnings):
            import numpy as np
            binnings = [VariableBinning(np.linspace(b.minimum, b.maximum, b.N + 1))
                        if isinstance(b, EquidistantBinning) else b for b in binnings]
    return binnings


class ProductHandle:
    NoResult = object()  # sentinel

    __slots__ = ("fdnd", "product")

    def __init__(self, filterWithDefNode):
        self.fdnd = filterWithDefNode
        self.product = None

    @property
    def digest(self):
        pass

    def makeProduct(self):
        pass

    def load(self, tFile):
        pass


class HistoND(ProductHandle):
    """ Lazy HistoND node: keep all information, but only build the RDF graph later """

    __slots__ = ("name", "fdnd", "allVars", "plot")

    def __init__(self, filterWithDefNode, name, axVars, plot, weight=None):
        super().__init__(filterWithDefNode)
        self.name = name
        self.allVars = list(axVars)
        if weight is not None:
            self.allVars.append(weight)
        self.plot = plot

    @property
    def digest(self):
        return top.op_digest(
            "RDF::Histo{nAx:d}D",
            self.fdnd.digest,
            *self.allVars,
            *(repr(bn) for bn in self.plot.binnings)
        )

    def _makeNamedVars(self):
        namedVars = []
        for i, var in enumerate(self.allVars):
            if isinstance(var, top.GetColumn):
                namedVars.append(ExprWithName(var.name, var))
            elif isinstance(var, top.ForwardingOp) and isinstance(var.wrapped, top.GetColumn):
                namedVars.append(ExprWithName(var.wrapped.name, var.wrapped))
            else:
                if self.fdnd.getColName(var):
                    varNm = self.fdnd.getColName(var)
                else:
                    varNm = f"v{i:d}_{self.name}"
                    self.fdnd.define(var, name=varNm)
                namedVars.append(ExprWithName(varNm, var))
        return namedVars

    def makeProduct(self):
        # define the necessary variables
        self.fdnd.df  # create Filter and (forced) Define nodes, if not done so yet
        namedVars = self._makeNamedVars()
        nAx = len(self.plot.variables)
        digest = self.digest
        logger.debug(
            "Adding histogram {0} with variables {1}{2} (digest: {3})",
            self.name, ", ".join(iv.name for iv in namedVars[:nAx]),
            (f" and weight {namedVars[-1].name}" if len(self.allVars) != nAx else ""),
            top.hexStr_digest(digest)
        )
        # reduce JITting inside RDF
        axTypes = [self.fdnd.df.GetColumnType(iv.name) for iv in namedVars]
        # TODO check & warn with allVars[:,1]
        useExplicit = True
        from .root import gbl
        for iv in namedVars:
            try:
                tp = getattr(gbl, iv.op.typeName)
                if hasattr(tp, "value_type"):
                    useExplicit = False
            except AttributeError:
                pass
        if useExplicit and nAx < 3:  # only have templates for those
            ndCppName = self.fdnd.df.__class__.__cpp_name__
            if nAx != len(axTypes):
                kyTypes = (ndCppName, tuple(axTypes[:-1]), axTypes[-1])
            else:
                kyTypes = (ndCppName, tuple(axTypes))
            _RDFHistoNDStats[kyTypes] += 1
            if kyTypes not in _RDFHistoND_methods:
                templTypes = [ndCppName] + axTypes
                logger.debug(f"Declaring Histo{nAx:d}D helper for types {templTypes}")
                _RDFHistoND_methods[kyTypes] = getattr(gbl.rdfhelpers.rdfhistofactory,
                                                       f"Histo{nAx:d}D")[tuple(templTypes)]
            plotFun = partial(_RDFHistoND_methods[kyTypes], self.fdnd.df)
        else:
            logger.debug(f"Using Histo{nAx:d}D with type inference")
            plotFun = getattr(self.fdnd.df, f"Histo{nAx:d}D")
        _RDFNodeStats[f"Histo{nAx:d}D"] += 1
        plotModel = self.fdnd.backend.__class__.makePlotModel(self.plot, self.name)
        self.product = plotFun(plotModel, *(iv.name for iv in namedVars))

    def load(self, tFile):
        self.product = tFile.Get(self.name)


class SkimTreeHandle(ProductHandle):

    __slots__ = ("colNToKeep", "skim", "tmpDir", "outFile")

    def __init__(self, filterWithDefNode, colNToKeep, skim):
        super().__init__(filterWithDefNode)
        self.colNToKeep = colNToKeep
        self.skim = skim
        self.tmpDir = tempfile.TemporaryDirectory()
        self.outFile = os.path.join(
            self.tmpDir.name,
            (f"skim_{self.skim.name}.root" if self.skim.key == self.skim.name
                else f"skim_{'_'.join(self.key)}.root"))

    @property
    def digest(self):
        return top.op_digest(
            "RDF::Snapshot",
            self.fdnd.digest,
            *chain(self.colNToKeep, chain.from_iterable(
                [k, top.adaptArg(v)] for k, v in self.skim.definedBranches.items()))
        )

    class Product:
        def __init__(self, parent, result=None, obj=None):
            self.parent = parent
            self.result = result
            self.obj = obj

        def Write(self):
            if self.GetEntries() != 0:
                newTree = self.obj.CloneTree(-1, "fast")
                newTree.Write()

        def GetEntries(self):
            if self.result and not self.obj:
                self._load(fromResult=True)
            return self.obj.GetEntries()

        def _load(self, fromResult=False):
            from .root import gbl
            pwd = gbl.gDirectory.GetPath()
            if fromResult:
                self.result.GetValue()  # trigger event loop if needed
            self._f = gbl.TFile.Open(self.parent.outFile)
            self.obj = self._f.Get(self.parent.skim.treeName)
            gbl.gDirectory.cd(pwd)  # move back

    def _getColNamesToKeep(self):
        self.fdnd.df  # create Filter and (forced) Define nodes, if not done so yet
        defcolN = list(self.fdnd._definedColumns.values())
        if hasattr(self.fdnd.df, "GetDefinedColumnNames"):  # only for non-compiled
            s_df = {str(nm) for nm in self.fdnd.df.GetDefinedColumnNames()
                    if str(nm) != "_zero_for_stats"}
            dfnotba = s_df - set(defcolN)
            if dfnotba:
                logger.error(f"In dataframe but not bamboo: {', '.join(dfnotba)}")
                raise RuntimeError("Mismatch in defined columns, see above")

        for cn in self.colNToKeep:
            if cn in defcolN:
                raise RuntimeError(f"Requested column '{cn}' from input is a defined column")
        colNToKeep = list(self.colNToKeep)

        for dN, dExpr in self.skim.definedBranches.items():
            if dN not in colNToKeep and dN not in defcolN:
                self.fdnd.define(top.adaptArg(dExpr), name=dN)
                colNToKeep.append(dN)
        return colNToKeep

    def makeProduct(self):
        from .root import gbl
        colNToKeep_v = gbl.std.vector["std::string"]()
        for cn in self._getColNamesToKeep():
            colNToKeep_v.push_back(cn)

        df = self.fdnd.df  # with the columns defined
        if self.skim.maxSelected > 0:
            df = df.Range(self.skim.maxSelected)
        snapOpts = gbl.ROOT.RDF.RSnapshotOptions()
        snapOpts.fLazy = True
        _RDFNodeStats["Snapshot"] += 1
        self.product = SkimTreeHandle.Product(
            self, result=df.Snapshot(self.skim.treeName, self.outFile, colNToKeep_v, snapOpts))

    def load(self, _tFile):
        self.product = SkimTreeHandle.Product(self)
        self.product._load(fromResult=False)


class CFRCounter(bamboo.plots.Product):
    def __init__(self, name, title=None):
        super().__init__(name)
        self.variables = (None,)
        self.binnings = (bamboo.plots.EquidistantBinning(1, 0., 1.),)
        self.title = title if title else name


class DataframeBackend(FactoryBackend):
    def __init__(self, tree, nThreads=None):
        from .root import gbl
        if nThreads and ((not gbl.ROOT.IsImplicitMTEnabled())
                         or nThreads != gbl.ROOT.GetThreadPoolSize()):
            logger.info(f"Enabling implicit MT for {nThreads:d} threads")
            gbl.ROOT.EnableImplicitMT(nThreads)
        self._tree = tree  # avoid going out of scope
        self.rootDF = gbl.ROOT.RDataFrame(tree).Define("_zero_for_stats", "0")
        self.selDFs = dict()       # (selection name, variation) -> SelWithDefines
        self.products = dict()     # product name -> list of product handles
        self.allSysts = set()      # all systematic uncertainties and variations impacting any plot
        self._cfrMemo = defaultdict(dict)
        super().__init__()
        self._iCol = 0

    def _getUSymbName(self):
        global _giFun
        _giFun += 1
        return f"myFun{_giFun:d}"

    def getUColName(self):
        self._iCol += 1
        return f"myCol{self._iCol:06d}"

    def shouldDefine(self, op, defCache=None):
        return op.canDefine and (isinstance(op, top.RangeOp) or isinstance(op, top.DefineOnFirstUse))

    def define(self, op, selection):  # for forceDefine
        self.selDFs[selection.name].fdnd.expl_define(op)

    def symbol(self, decl, resultType=None, args=None, nameHint=None):
        isFunction = (resultType and args)
        if isFunction:  # then it needs to be wrapped in a function
            decl = "{result} <<name>>({args})\n{{\n  return {0};\n}};\n".format(
                decl, result=resultType, args=args)
        global _gSymbols
        if decl in _gSymbols:
            return _gSymbols[decl]
        else:
            if nameHint and nameHint not in _gSymbols.values():
                name = nameHint
            else:
                name = self._getUSymbName()
            _gSymbols[decl] = name
            self.int_declare(decl.replace("<<name>>", name), isFunction=isFunction)
            return name

    def makeHelperFunction(self, cppStr, expr, defCache, asLambda=False):
        depList = top._collectDeps(expr, defCache=defCache)
        _, paramDecl, paramNames, paramCall = top._convertFunArgs(depList, defCache=defCache)
        expr_n, paramDecl_n = _normFunArgs(cppStr, paramDecl, paramNames)
        if defCache.getColName(expr) or any(isinstance(expr, tp)
                                            for tp in (top.GetColumn, top.GetArrayColumn)):
            _, paramDecl, paramNames, paramCall = top._convertFunArgs([expr], defCache=defCache)
            expr_n, paramDecl_n = _normFunArgs(cppStr, paramDecl, paramNames)
            funDecl = "[] ( {0} ) {{ return {1}; }}".format(
                ", ".join(paramDecl_n), expr_n)
            return funDecl, paramCall
        elif not asLambda:
            funName = defCache.symbol(expr_n, resultType=expr.typeName, args=", ".join(paramDecl_n))
            return funName, paramCall
        else:
            funDecl = "[] ( {0} ) {{ return {1}; }}".format(
                ", ".join(paramDecl_n), expr_n)
            return funDecl, paramCall

    # wrappers for gInterpreter::Declare, RDF::Define and RDF::Filter
    def int_declare(self, code, isFunction=False):
        logger.debug("Defining new symbol with interpreter: {0}", code)
        from .root import gbl
        gbl.gInterpreter.Declare(code)
        _RDFNodeStats["gInterpreter_Declare"] += 1

    def df_define(self, df, name, cppStr, expr, defCache):
        if isinstance(expr, top.RangeOp) and not defCache.getColName(expr):
            funName, param = self.makeHelperFunction(cppStr, expr, defCache)
            cppStr = f"{funName}({', '.join(param)})"
        logger.debug("Defining {0} as {1}", name, cppStr)
        _RDFNodeStats["Define"] += 1
        return df.Define(name, cppStr)

    def df_filter(self, df, cppStr, expr, defCache):
        if isinstance(expr, top.RangeOp) and not defCache.getColName(expr):
            funName, param = self.makeHelperFunction(cppStr, expr, defCache)
            cppStr = f"{funName}({', '.join(param)})"
        logger.debug("Filtering with {0}", cppStr)
        _RDFNodeStats["Filter"] += 1
        return df.Filter(cppStr)

    def df_origColNames(self):
        return [str(cN) for cN in self.rootDF.GetColumnNames() if str(cN) != "_zero_for_stats"]

    @classmethod
    def create(cls, decoTree, **kwargs):
        inst = cls(decoTree._tree, **kwargs)
        rootSel = Selection(inst, "none")
        return inst, rootSel

    def addSelection(self, sele):
        """ Define ROOT::RDataFrame objects needed for this selection """
        if sele.name in self.selDFs:
            raise RuntimeError(f"A Selection with name '{sele.name}' already exists")
        nomParentNd, parentHelper = None, None
        if sele.parent is None:  # root no-op selection
            assert not sele._cuts  # this one cannot have cuts
            logger.debug("Constructing FilterWithDefines for the root selection")
            nomNd = FilterWithDefines(self)
            nomNd.var = dict()  # will stay empty
            helper = SelectionHelper(nomNd)
        else:
            parentHelper = self.selDFs[sele.parent.name]
            nomParentNd = parentHelper.fdnd
            if sele._cuts:
                nomNd = nomParentNd.childWithCuts(sele._cuts)
                nomNd.var = dict()  # only for nominal non-root
            else:
                nomNd = nomParentNd
            helper = SelectionHelper(nomNd)
        nomParWeight = None
        if parentHelper and parentHelper.weight:
            nomParWeight = parentHelper.weight["nominal"]
        if sele._weights:
            helper.weight["nominal"] = nomNd.makeWeight(
                sele._weights,
                wName=f"w_{sele.name}",
                parentWeight=nomParWeight
            )
        elif nomParWeight:
            helper.weight["nominal"] = nomParWeight
        self.selDFs[sele.name] = helper

        if sele.autoSyst:
            # construct variation nodes (if necessary)
            seleSysts = sele.systematics
            logger.debug("Adding systematic variations {0}", ", ".join(seleSysts))
            for varn in seleSysts:  # all (cut and weight) variations
                # _cSysts and _wSysts are { variation : { cut/weight : [ nodes to change ] } }
                # add cuts to the appropriate node, if affected by systematics (here or up)
                varParentNd = None  # set parent node if not the nominal one
                if nomParentNd and varn in nomParentNd.var:  # -> continue on branch
                    logger.debug("{0} systematic variation {1}: continue on branch", sele.name, varn)
                    varParentNd = nomParentNd.var[varn]
                elif varn in sele._cSysts:  # -> branch off now
                    logger.debug("{0} systematic variation {1}: create branch", sele.name, varn)
                    varParentNd = nomParentNd
                if not varParentNd:  # cuts unaffected (here and in parent), can stick with nominal
                    varNd = nomNd
                else:  # on branch, so add cuts (if any)
                    if len(sele._cuts) == 0:  # no cuts, reuse parent
                        varNd = varParentNd
                    else:
                        ctMod = []
                        for ct in sele._cuts:
                            if ct in sele._cSysts[varn]:
                                clNds = list()
                                newct = ct.clone(select=sele._cSysts[varn][ct].__contains__,
                                                 selClones=clNds)
                                assert len(clNds) >= len(sele._cSysts[varn][ct])  # should clone all
                                for nd in clNds:
                                    nd.changeVariation(varn)
                                ctMod.append(newct)
                            else:
                                ctMod.append(ct)
                        varNd = varParentNd.childWithCuts(ctMod)
                    nomNd.var[varn] = varNd
                # next: attach weights (modified if needed) to varNd
                parw = parentHelper.weight.get(varn, parentHelper.weight.get("nominal"))
                if not sele._weights:
                    logger.debug("{0} systematic variation {1}: reusing {2}", sele.name, varn,
                                 ("parent weight" if parw is not None else "none"))
                    helper.weight[varn] = parw
                else:
                    if (varn in sele._wSysts or varNd != nomNd
                            or (parentHelper and varn in parentHelper.weight)):
                        wfMod = []
                        for wf in sele._weights:
                            if wf in sele._wSysts[varn]:
                                clNds = list()
                                newf = wf.clone(select=sele._wSysts[varn][wf].__contains__,
                                                selClones=clNds)
                                assert len(clNds) >= len(sele._wSysts[varn][wf])  # should clone all
                                for nd in clNds:
                                    nd.changeVariation(varn)
                                wfMod.append(newf)
                            else:
                                wfMod.append(wf)
                        logger.debug(
                            "{0} systematic variation {1}: defining new weight based on {2}",
                            sele.name, varn, parw)
                        helper.weight[varn] = varNd.makeWeight(
                            wfMod,
                            wName=(f"w_{sele.name}__{varn}" if sele._weights else None),
                            parentWeight=parw)
                    else:  # varNd == nomNd, not branched, and parent does not have weight variation
                        logger.debug(
                            "{0} systematic variation {1}: reusing nominal {2}",
                            sele.name, varn,
                            (varNd.weight["nominal"][0] if varNd.weight["nominal"] is not None
                             else "none"))
                        helper.weight[varn] = helper.weight["nominal"]

    def addPlot(self, plot, autoSyst=True):
        """
        Define ROOT::RDataFrame objects needed for this plot (and keep track of the result pointer)
        """
        if plot.key in self.products:
            raise ValueError(f"A Plot with key '{plot.key}' has already been added")

        selHelper = self.selDFs[plot.selection.name]
        nomNd = selHelper.fdnd
        plotRes = []
        # Add nominal plot
        nomWeight = selHelper.weight.get("nominal")
        if plot._weights:
            logger.debug(
                "Plot {0}: defining new nominal weight based on {1}",
                plot.name, ("selection nominal" if nomWeight is not None else "none"))
            nomWeight = nomNd.makeWeight(
                plot._weights, parentWeight=nomWeight,
                wName=f"w_{plot.selection.name}_{plot.name}")
        plotRes.append(HistoND(nomNd, makeHistoName(plot), plot.variables, plot, weight=nomWeight))

        if plot.selection.autoSyst and autoSyst:
            # Same for all the systematics
            varSysts = top.collectSystVars(plot.variables)
            pwSysts = top.collectSystVars(plot._weights)
            # plotSysts, selSysts and allSysts are just {varName}, without the nodes to change
            plotSysts = set(varSysts)
            plotSysts.update(pwSysts)
            selSysts = plot.selection.systematics
            allSysts = set(selSysts)
            allSysts.update(plotSysts)
            self.allSysts.update(allSysts)
            for varn in allSysts:
                if varn in varSysts or varn in nomNd.var:
                    varNd = nomNd.var.get(varn, nomNd)
                    vVars = []
                    for xVar in plot.variables:
                        if xVar in varSysts[varn]:
                            clNds = list()
                            newVar = xVar.clone(select=varSysts[varn][xVar].__contains__,
                                                selClones=clNds)
                            assert len(clNds) >= len(varSysts[varn][xVar])  # should clone all
                            for nd in clNds:
                                nd.changeVariation(varn)
                            vVars.append(newVar)
                        else:
                            vVars.append(xVar)
                else:  # can reuse variables, but need to take care of weight
                    varNd = nomNd
                    vVars = plot.variables
                weight = selHelper.weight[varn if varn in selSysts and varn in selHelper.weight
                                          else "nominal"]
                if plot._weights:
                    wfMod = []
                    if varn in pwSysts:
                        # plot weights have variation, vary
                        for wf in plot._weights:
                            if wf in pwSysts[varn]:
                                clNds = list()
                                newf = wf.clone(select=pwSysts[varn][wf].__contains__,
                                                selClones=clNds)
                                assert len(clNds) >= len(pwSysts[varn][wf])  # should clone all
                                for nd in clNds:
                                    nd.changeVariation(varn)
                                wfMod.append(newf)
                            else:
                                wfMod.append(wf)
                    elif varn in selSysts and varn in selHelper.weight:
                        # variation in selection weight
                        wfMod = plot._weights
                    if wfMod:  # need a weight for this variation
                        logger.debug(
                            "Plot {0} systematic variation {1}: defining new weight based on {2}",
                            plot.name, varn, ("parent weight" if weight is not None else "none"))
                        weight = varNd.makeWeight(
                            wfMod, parentWeight=weight,
                            wName=f"w_{plot.selection.name}_{plot.name}__{varn}")
                    else:  # no systematic that affects the weight
                        weight = nomWeight
                plotRes.append(HistoND(varNd, makeHistoName(plot, variation=varn), vVars,
                                       plot, weight=weight))

        self.products[plot.key] = plotRes

    @classmethod
    def makePlotModel(cls, plot, hName):
        from .root import gbl
        modCls = getattr(gbl.ROOT.RDF, f"TH{len(plot.binnings):d}DModel")
        return modCls(hName, plot.title, *chain.from_iterable(
            cls.makeBinArgs(binning) for binning in _adjustBinnings(plot.binnings)))

    @classmethod
    def makeBinArgs(cls, binning):
        from .plots import EquidistantBinning, VariableBinning
        if isinstance(binning, EquidistantBinning):
            return (binning.N, binning.mn, binning.mx)
        elif isinstance(binning, VariableBinning):
            return (binning.N, np.array(binning.binEdges, dtype=np.float64))
        else:
            raise ValueError(f"Binning of unsupported type: {binning!r}")

    def getProducts(self, key):
        return self.products.get(key, [])

    def getResults(self, plot, key=None):
        bareResults = []
        for res in self.getProducts(key if key is not None else plot.key):
            if isinstance(res, ProductHandle):
                prod = res.product
                if prod is not ProductHandle.NoResult:
                    bareResults.append(prod)
            else:  # TODO get rid of this check when everything follows the above
                logger.warning(
                    f"getProducts: Adding result {res!r} for "
                    f"{key if key is not None else plot.key} directly")
                bareResults.append(res)
        return plot.produceResults(bareResults, self, key=key)

    def addSkim(self, skim):
        if skim.key in self.products:
            raise ValueError(f"A Skim with key '{skim.key}' has already been added")

        colNToKeep = list()
        origcolN = self.df_origColNames()
        for toKeep in skim.originalBranches:
            if toKeep is Skim.KeepAll:  # keep all if not defined
                for cN in origcolN:
                    if cN not in colNToKeep:
                        colNToKeep.append(cN)
            elif isinstance(toKeep, Skim.KeepRegex):
                import re
                pat = re.compile(toKeep.pattern)
                for cN in origcolN:
                    if pat.match(cN) and cN not in colNToKeep:
                        colNToKeep.append(cN)
            elif isinstance(toKeep, str):
                if toKeep not in origcolN:
                    raise RuntimeError(f"Requested column '{toKeep}' from input not found")
                if toKeep not in colNToKeep:
                    colNToKeep.append(toKeep)
            else:
                raise RuntimeError(f"Cannot interpret {toKeep!r} as column list to keep")

        for dN in skim.definedBranches.keys():
            if dN in origcolN:
                logger.warning(
                    f"Requested to add column {dN} with expression, but a column with the same "
                    "name on the input tree exists. The latter will be copied instead")

        selND = self.selDFs[skim.selection.name].fdnd

        self.products[skim.key] = [SkimTreeHandle(selND, colNToKeep, skim)]

    def addCutFlowReport(self, report, selections, key=None, autoSyst=True):
        logger.debug(
            "Adding cutflow report {} for selection(s) {}".format(
                report.name, ", ".join(sele.name for sele in selections.values())))
        memo = self._cfrMemo[report.name]
        cfres, results = [], []
        for name, sele in selections.items():
            if sele.name in memo:
                cfr = memo[sele.name]
            else:
                cfrNom, cfrSys = self._makeCutFlowReport(sele, name, autoSyst=autoSyst,
                                                         prefix=report.name)
                cfr = report.__class__.Entry(name, cfrNom, cfrSys)
                memo[sele.name] = cfr
            cfres.append(cfr)
            results.append(cfr.nominal)
            results += list(cfr.systVars.values())
        if key is None:
            key = report.name
        report.cfres[key] += cfres
        self.products[key] = self.getProducts(key) + results

    def _makeCutFlowReport(self, selection, name, autoSyst=True, prefix=None):
        selH = self.selDFs[selection.name]
        selND = selH.fdnd
        nomWeight = selH.weight.get("nominal")
        nomName = f"{prefix}_{name}"
        zVar = [top.GetColumn("int", "_zero_for_stats")]
        cfrNom = HistoND(
            selND, nomName, zVar + ([nomWeight] if nomWeight is not None else []),
            CFRCounter(nomName, f"CutFlowReport {prefix} nominal counter for {selection.name}"))
        cfrSys = {}
        if autoSyst:
            for varNm in selection.systematics:
                if varNm in selND.var or selH.weight[varNm] != nomWeight:
                    cfrSys[varNm] = HistoND(
                        selND.var.get(varNm, selND),
                        f"{nomName}__{varNm}", zVar + [selH.weight[varNm]],
                        CFRCounter(
                            f"{nomName}__{varNm}",
                            f"CutFlowReport {prefix} {varNm} counter for {selection.name}"))
        return cfrNom, cfrSys

    def buildGraph(self, plotList):
        self._plotList = plotList  # store for runGraph
        # gather products
        products = defaultdict(list)
        for p in plotList:
            products[None] += self.getProducts(p.name)
            for suff in SelectionWithSub.getSubsForPlot(p, requireActive=True, silent=True):
                products[suff] += self.getProducts((p.name, suff))
        # Collect FilterWithDefines that need to be built, and products for each
        products_by_fdndId = dict()
        fdnds = dict()
        for sProducts in products.values():
            for prod in sProducts:
                # (later) figure out which are there, and which need to be produced
                assert prod.product is None  # need to be all
                fdndId = id(prod.fdnd)
                cId, cNd = fdndId, prod.fdnd
                while cId not in fdnds and isinstance(cNd, FilterWithDefines):
                    fdnds[cId] = cNd
                    products_by_fdndId[cId] = []
                    cNd = cNd.parent
                    cId = id(cNd)
                products_by_fdndId[fdndId].append(prod)

        # strategy from old lazy backend: start from top, build products before children
        def buildFilterWithDefines(iId, iNd):
            for prod in products_by_fdndId[iId]:
                prod.makeProduct()  # RDF graph construction
            del products_by_fdndId[iId]
            for cNd in fdnds[iId].children.values():
                cId = id(cNd)
                if cId in products_by_fdndId:
                    buildFilterWithDefines(cId, cNd)
            del fdnds[iId]

        buildFilterWithDefines(*next((k, v) for k, v in fdnds.items() if v.parent is None))
        assert not products_by_fdndId

        _printStats()
        _resetStats()
        # NOTE could return results

    def runGraph(self):
        from .root import gbl
        triggered = False
        for p in self._plotList:
            for h in self.getResults(p):
                if not triggered and not isinstance(h, gbl.TH1):
                    h.GetEntries()  # trigger event loop
                    triggered = True
            for suff in SelectionWithSub.getSubsForPlot(p, requireActive=True, silent=False):
                for h in self.getResults(p, key=(p.name, suff)):
                    if not triggered and not isinstance(h, gbl.TH1):
                        h.GetEntries()  # trigger event loop
                        triggered = True

    def writeResults(self, plotList, outputFile, mergeCounters):
        numHistos = 0
        numSkims = 0
        numDDHistos = 0
        from .root import gbl
        outF = gbl.TFile.Open(outputFile, "RECREATE")
        outF.cd()
        for p in plotList:
            for h in self.getResults(p):
                h.Write()
                if isinstance(h, SkimTreeHandle.Product):
                    numSkims += 1
                else:
                    numHistos += 1
        mergeCounters(outF)
        outF.Close()
        subFiles = dict()
        for p in plotList:
            for suff in SelectionWithSub.getSubsForPlot(p, requireActive=True, silent=True):
                if suff not in subFiles:
                    subFiles[suff] = gbl.TFile.Open(
                        "{1}{0}{2}".format(suff, *os.path.splitext(outputFile)),
                        "RECREATE")
                subFiles[suff].cd()
                for h in self.getResults(p, key=(p.name, suff)):
                    h.Write()
                    numDDHistos += 1
        for subF in subFiles.values():
            mergeCounters(subF)
            subF.Close()
        return {
            "nHistos": numHistos,
            "nSkims": numSkims,
            "nDDHistos": numDDHistos
        }

    def addDependency(self, **kwargs):
        from .root import loadDependency
        for ky in ("package", "cmakeArgs"):  # only for fully compiled
            if ky in kwargs:
                kwargs.pop(ky)
        return loadDependency(**kwargs)


class DebugDataframeBackend(DataframeBackend):
    """ Build the full RDF graph immediately, as plots and selections are being defined """

    def addSelection(self, selection):
        super().addSelection(selection)
        self.selDFs[selection.name].fdnd.df  # construct RDF graph until Filter node(s)

    def addPlot(self, plot, autoSyst=True):
        super().addPlot(plot, autoSyst=autoSyst)
        for p in self.getProducts(plot.key):
            p.makeProduct()

    def addSkim(self, skim):
        super().addSkim(skim)
        for p in self.getProducts(skim.key):
            p.makeProduct()

    def addCutFlowReport(self, report, selections, key=None, autoSyst=True):
        super().addCutFlowReport(report, selections, key=key, autoSyst=autoSyst)
        for prod in self.getProducts(key if key is not None else report.name):
            if prod.product is None:
                prod.makeProduct()

    def buildGraph(self, plotList):
        self._plotList = plotList  # store for runGraph
        _printStats()
        _resetStats()


class FullyCompiledBackend(DataframeBackend):
    """ Another experiment: compile a standalone executable to avoid any JITting in RDF """
    skeleton_cmake = pkg_resources.resource_filename("bamboo", os.path.join("data", "CMakeLists.txt"))
    skeleton_cpp = pkg_resources.resource_filename("bamboo", os.path.join("data", "main.cc"))

    def __del__(self):
        if (self.cleanupTmp and self.tmpDir and os.path.isdir(self.tmpDir)
                and self.tmpDir.startswith(tempfile.gettempdir())):
            logger.debug(f"Cleaning up temporary directory {self.tmpDir}")
            shutil.rmtree(self.tmpDir)
        else:
            logger.info(f"Leaving all generated code and cmake outputs in {self.tmpDir}")

    _genCode = {
        # cmake
        "findpackages": [],
        "bamboocomponents": list(root._defaultBambooLibs),
        "libdependencies": list(root._defaultDependencies) + list(root._defaultBambooLibs),
        "includedirs": [],
        "linkdirs": [],
        # cc
        "includes": [f'#include "hdr"' for hdr in root._defaultHeaders],
        "helpermethods": [],
        "initialisation": [],
    }

    gen_entriesFmt = {
        "includes": (list(root._defaultHeaders), lambda hdrs: [f'#include "{hdr}"' for hdr in hdrs]),
        "includedirs": ([], lambda dirs: [
            "target_include_directories(bambooExecutor PRIVATE {})".format(" ".join(
                f"$<BUILD_INTERFACE:{idr}>" for idr in dirs))]),
        "linkdirs": ([], lambda dirs: [
            "target_link_directories(bambooExecutor PUBLIC {})".format(" ".join(dirs))])
    }

    @staticmethod
    def _addGenEntries(key, entries):
        if key in FullyCompiledBackend.gen_entriesFmt:
            gEnt, fmt = FullyCompiledBackend.gen_entriesFmt[key]
            gEnt.extend(entries)
            FullyCompiledBackend._genCode[key] = fmt(gEnt)
        else:
            FullyCompiledBackend._genCode[key] += entries

    def __init__(self, tree, nThreads=None):
        super().__init__(tree)
        self.tTree = tree
        self.rootDF = "df0"
        self._iDF = 0
        self.nThreads = (nThreads if nThreads else 1)
        self.cmakeConfigOptions = ["-DCMAKE_BUILD_TYPE=Release"]
        self.cmakeBuildOptions = []
        self.cleanupTmp = True
        self.tmpDir = tempfile.mkdtemp()
        logger.debug(f"Temporary directory for compilation: {self.tmpDir}")
        self.tmpOutF = None
        self.resultDefinitions = ['auto df0 = df.Define("_zero_for_stats", []() { return 0; }, {});']
        self.inputFileLists = None

    @property
    def genCode(self):
        gc = dict(FullyCompiledBackend._genCode)
        gc["resultdefinitions"] = self.resultDefinitions
        return gc

    def getUDFName(self):
        self._iDF += 1
        return f"df{self._iDF:d}"

    def shouldDefine(self, op, defCache=None):
        return (op.canDefine and (isinstance(op, top.RangeOp)
                                  or isinstance(op, top.DefineOnFirstUse)
                                  or isinstance(op, top.Parameter)))

    def int_declare(self, code, isFunction=False):
        if not isFunction:  # no need to have helper functions dynamically
            super().int_declare(code, isFunction=isFunction)
        FullyCompiledBackend._genCode["helpermethods"].append(code)

    def df_define(self, df, name, cppStr, expr, defCache):
        funNameOrDef, param = self.makeHelperFunction(
            cppStr, expr, defCache, asLambda=(not isinstance(expr, top.RangeOp)))
        newdf = self.getUDFName()
        self.resultDefinitions.append(
            f'auto {newdf} = {df}.Define("{name}", {funNameOrDef}, '
            + "{{ {0} }});".format(", ".join(f'"{p}"' for p in param)))
        _RDFNodeStats["Define"] += 1
        return newdf

    def df_filter(self, df, cppStr, expr, defCache):
        funNameOrDef, param = self.makeHelperFunction(
            cppStr, expr, defCache,
            asLambda=((not isinstance(expr, top.RangeOp)) or defCache.getColName(expr)))
        newdf = self.getUDFName()
        self.resultDefinitions.append(
            f"auto {newdf} = {df}.Filter({funNameOrDef},"
            + "{{ {0} }});".format(", ".join(f'"{p}"' for p in param)))
        _RDFNodeStats["Filter"] += 1
        return newdf

    def df_origColNames(self):
        from .root import gbl
        return list(str(cN) for cN in gbl.ROOT.RDataFrame(self.tTree).GetColumnNames())

    @classmethod
    def makePlotModel(cls, plot, hName):
        binArgs = ", ".join(cls.makeBinArgs(bn) for bn in _adjustBinnings(plot.binnings))
        return f'ROOT::RDF::TH{len(plot.binnings):d}DModel("{hName}", "{plot.title}", {binArgs})'

    @classmethod
    def makeBinArgs(cls, binning):
        from .plots import EquidistantBinning, VariableBinning
        if isinstance(binning, EquidistantBinning):
            return f"{binning.N:d}, {binning.mn:f}, {binning.mx:f}"
        elif isinstance(binning, VariableBinning):
            return "{0:d}, {{ {1} }}".format(
                len(binning.N), ", ".join(str(be) for be in binning.binEdges))
        else:
            raise ValueError(f"Binning of unsupported type: {binning!r}")

    def _writeWithSubstitution(self, skeletonFile, placeholder):
        with open(skeletonFile) as skF:
            srcLines = []
            for skLn in skF:
                if skLn.lstrip().startswith(placeholder):
                    ind, ky = skLn.split(placeholder)
                    srcLines += [f"{ind}{ln}" for ln in self.genCode[ky.strip()]]
                else:
                    srcLines.append(skLn.rstrip("\n"))
        with open(os.path.join(self.tmpDir, os.path.basename(skeletonFile)), "w") as srcF:
            fullSrc = "\n".join(srcLines)
            logger.debug("Full source: \n{0}", fullSrc)
            srcF.write(fullSrc)

    def buildGraph(self, plotList):
        self._plotList = plotList  # store for runGraph
        # gather products
        products = defaultdict(list)
        for p in plotList:
            products[None] += self.getProducts(p.name)
            for suff in SelectionWithSub.getSubsForPlot(p, requireActive=True):
                products[suff] += self.getProducts((p.name, suff))
        # figure out which are there, and which need to be produced
        nToProduce, nFromCache = 0, 0
        for sProducts in products.values():
            for prod in sProducts:
                assert prod.product is None
                prod.fdnd.df  # create Filter and (forced) Define nodes, if not done so yet
                if isinstance(prod, HistoND):
                    namedVars = prod._makeNamedVars()
                    self.resultDefinitions.append(
                        f"results.add({prod.fdnd.df}.Histo{len(prod.plot.variables):d}D"
                        + "<{}>({}, {}));".format(
                            ", ".join(v.op.typeName for v in namedVars),
                            self.__class__.makePlotModel(prod.plot, prod.name),
                            ", ".join(f'"{v.name}"' for v in namedVars)))
                    _RDFNodeStats[f"Histo{len(prod.plot.variables):d}D"] += 1
                elif isinstance(prod, SkimTreeHandle):
                    colNToKeep = prod._getColNamesToKeep()  # also trigger column defines
                    self.resultDefinitions.append(
                        "results.add({}{}".format(
                            prod.fdnd.df,
                            (f".Range({prod.skim.maxSelected})"
                             if prod.skim.maxSelected > 0 else ""))
                        + f'.Snapshot("{prod.skim.treeName}", "{prod.outFile}", {{ '
                        + ", ".join(f'"{cN}"' for cN in colNToKeep)
                        + " }, snapshotOptions));"
                    )
                    _RDFNodeStats["Snapshot"] += 1
                else:
                    raise RuntimeError(f"Unsupported product type: {prod!r}")
                nToProduce += 1
        logger.info(
            f"{nFromCache:d}/{nToProduce+nFromCache:d} histograms from cache, "
            f"{nToProduce:d}/{nToProduce+nFromCache:d} to produce")
        _printStats()
        _resetStats()
        # write code and compile
        self._writeWithSubstitution(FullyCompiledBackend.skeleton_cmake, "# BAMBOO_INSERT")
        self._writeWithSubstitution(FullyCompiledBackend.skeleton_cpp, "// BAMBOO_INSERT")
        logger.info("Compiling executable")
        start = timer()
        try:
            configCmd = ["cmake"] + self.cmakeConfigOptions + [
                f'-Dbamboo_DIR={pkg_resources.resource_filename("bamboo", "cmake")}',
                f'-DCMAKE_MODULE_PATH={pkg_resources.resource_filename("bamboo", "data")}',
                self.tmpDir]
            out = subprocess.check_output(configCmd, cwd=self.tmpDir, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            self.cleanupTmp = False
            logger.error("Problem while running cmake, full output of '{0}':\n{1}",
                         " ".join(configCmd), ex.output.decode().strip())
            raise ex
        else:
            logger.debug("Full output of '{0}:\n{1}", " ".join(configCmd), out.decode().strip())
        try:
            buildCmd = ["cmake", "--build", self.tmpDir] + self.cmakeBuildOptions
            out = subprocess.check_output(buildCmd, cwd=self.tmpDir, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            self.cleanupTmp = False
            logger.error("Problem while building, full output of '{0}':\n{1}",
                         " ".join(buildCmd), ex.output.decode().strip())
            raise ex
        else:
            logger.debug("Full output of '{0}':\n{1}", " ".join(buildCmd), out.decode().strip())
        end = timer()
        logger.info(f"Executable compilation finished in {end - start:.2f}s")

    def runGraph(self):
        tmpOutFileName = os.path.join(self.tmpDir, "out.root")
        inFileArr = self.tTree.GetListOfFiles()  # assumes TChain
        inFileNames = [inFileArr.At(i).GetTitle() for i in range(inFileArr.GetEntries())]
        threadsMsg = (f" ({self.nThreads:d} threads)"
                      if self.nThreads is not None and self.nThreads > 1
                      else "")
        logger.info(f"Processing {len(inFileNames):d} files with standalone executable{threadsMsg}")
        try:
            cmd = [
                os.path.join(self.tmpDir, "bambooExecutor"),
                f"--output={tmpOutFileName}",
                f"--tree={self.tTree.GetName()}",
            ] + ([f"--threads={self.nThreads:d}"]
                 if self.nThreads is not None and self.nThreads > 1 else []
                 ) + ([f"--input-files={inFN}" for inFN in self.inputFileLists]
                      if self.inputFileLists is not None else
                      [f"--input={inFN}" for inFN in inFileNames])
            logger.info(f"Full command: {' '.join(cmd)}")
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            self.cleanupTmp = False
            logger.error("Problem while running standalone executable, full output:\n{0}",
                         ex.output.decode())
            raise ex
        # then load them in the results dictionary to make the res work
        from .root import gbl, returnToDirectory
        with returnToDirectory():
            # keep a ref to the file because it owns the histograms
            # (and use to detect this part has run)
            self.tmpOutF = gbl.TFile.Open(tmpOutFileName)
            loadedRes = dict()
            for pNm, pResults in self.products.items():
                for res in pResults:
                    res.load(self.tmpOutF)
                loadedRes[pNm] = list(pResults)
            self.products = loadedRes

    def addDependency(self, bambooLib=None,
                      includePath=None, headers=None,
                      dynamicPath=None, libraries=None,
                      package=None, components=None,
                      cmakeArgs=None):
        # start with loading them as usual
        super().addDependency(
            bambooLib=bambooLib, includePath=includePath, headers=headers,
            dynamicPath=dynamicPath, libraries=libraries)

        def asList(arg):
            if isinstance(arg, str):
                return [arg]
            else:
                return list(arg)

        if includePath:
            FullyCompiledBackend._addGenEntries("includedirs", asList(includePath))
        if headers:
            FullyCompiledBackend._addGenEntries("includes", asList(headers))
        if dynamicPath:
            FullyCompiledBackend._addGenEntries("linkdirs", asList(dynamicPath))
        if libraries:
            FullyCompiledBackend._genCode["libdependencies"] += asList(libraries)
        if bambooLib:
            FullyCompiledBackend._genCode["bamboocomponents"] += asList(bambooLib)
            FullyCompiledBackend._genCode["libdependencies"] += asList(bambooLib)
        if package:
            FullyCompiledBackend._genCode["findpackages"].append("find_package({} REQUIRED{})".format(
                package, (
                    "" if not components else " COMPONENTS {}".format(", ".join(asList(components))))))
        if cmakeArgs:
            if isinstance(cmakeArgs, str):
                self.cmakeConfigOptions.append(cmakeArgs)
            else:
                self.cmakeConfigOptions += list(cmakeArgs)


def getBackend(decoTree, name=None, **kwargs):
    if name == "debug":
        cls = DebugDataframeBackend
    elif name == "compiled":
        cls = FullyCompiledBackend
    else:
        cls = DataframeBackend
    return cls.create(decoTree, **kwargs)
