"""
The :py:mod:`bamboo.plots` module provides high-level classes to represent
and manipulate selections and plots.
"""
__all__ = (
    "Plot", "EquidistantBinning", "VariableBinning", "Selection", "Product", "DerivedPlot",
    "SummedPlot", "CutFlowReport", "SelectionWithSub", "SelectionWithDataDriven",
    "LateSplittingSelection", "CategorizedSelection", "FactoryBackend", "Skim"
)

import logging
from collections import defaultdict
from itertools import chain

from . import treefunctions as op
from . import treeoperations as top
from .treeproxies import adaptArg

logger = logging.getLogger(__name__)


class FactoryBackend:
    """ Interface for factory backend (to separate Plots classes from ROOT::RDataFrame part) """
    def __init__(self):
        pass

    def addSelection(self, selection):
        pass

    def addPlot(self, plot):
        pass

    def addDerived(self, product):
        pass

    def addSkim(self, skim):  # TODO move towards addProduct
        pass

    def addCutFlowReport(self, report, selections=None, autoSyst=True):
        pass

    def define(self, op, selection):
        """ explicitly define column for expression """
        pass

    def buildGraph(self, plotList):
        """ Called after adding all products, but before retrieving the results """
        pass

    def getResults(self, plot):
        pass

    def setNThreads(self, nThreads):
        pass

    def addDependency(self, **kwargs):
        pass

    @classmethod
    def create(cls, tree, nThreads=None):
        """ Factory method, should return a pair of the backend and root selection """
        return (None, None)


class Product:
    """ Interface for output products (plots, counters etc.) """
    def __init__(self, name, key=None):
        self.name = name
        self.key = key if key is not None else name

    def produceResults(self, bareResults, fbe, key=None):
        """
        Main interface method, called by the backend

        :param bareResults: iterable of histograms for this plot produced by the backend
        :param fbe: reference to the backend
        :param key: key under which the backend stores the results (if any)

        :returns: an iterable with ROOT objects to save to the output file
        """
        pass


class EquidistantBinning:
    """ Equidistant binning """
    __slots__ = ("__weakref__", "N", "mn", "mx")

    def __init__(self, N, mn, mx):
        """
        :param N: number of bins
        :param mn: minimum axis value
        :param mx: maximum axis value
        """
        self.N = N
        self.mn = mn
        self.mx = mx

    @property
    def minimum(self):
        return self.mn

    @property
    def maximum(self):
        return self.mx

    def __repr__(self):
        return f"{self.__class__.__name__}({self.N}, {self.mn:f}, {self.mx:f})"


class VariableBinning:
    """ Variable-sized binning """
    __slots__ = ("__weakref__", "binEdges")

    def __init__(self, binEdges):
        """
        :param binEdges: iterable with the edges. There will be ``len(binEges)-1`` bins
        """
        self.binEdges = list(binEdges)

    @property
    def N(self):
        return len(self.binEdges) - 1

    @property
    def minimum(self):
        return self.binEdges[0]

    @property
    def maximum(self):
        return self.binEdges[-1]

    def __repr__(self):
        return f"{self.__class__.__name__}([', '.join(str(xi) for xi in self.binEdges)])"


class Plot(Product):
    """ A :py:class:`~bamboo.plots.Plot` object contains all information needed
    to produce a histogram: the variable(s) to plot, binnings and options
    (axis titles, optionally some style information), and a reference to
    a :py:class:`~bamboo.plots.Selection` (which holds all cuts and weights to apply for the plot).

    .. note::

        All :py:class:`~bamboo.plots.Plot` (and :py:class:`~bamboo.plots.Selection`) instances
        need to have a unique name. This name is used to construct output filenames, and internally
        to define DataFrame columns with readable names.
        The constructor will raise an exception if an existing name is used.
    """
    def __init__(
            self, name, variables, selection, binnings, weight=None, title="", axisTitles=tuple(),
            axisBinLabels=tuple(), plotopts=None, autoSyst=True, key=None):
        """ Generic constructor. Please use the static :py:meth:`~bamboo.plots.Plot.make1D`,
        :py:meth:`~bamboo.plots.Plot.make2D` and :py:meth:`~bamboo.plots.Plot.make3D` methods,
        which provide a more convenient interface to construct histograms
        (filling in some defaults requires knowing the dimensionality).
        """
        if len(variables) != len(binnings):
            raise ValueError(
                f"Unequal number of variables ({len(variables):d}) and binnings ({len(binnings):d})")
        super().__init__(name, key=key)
        self.variables = variables
        self.selection = selection
        self._weights = [adaptArg(wgt, typeHint=top.floatType)
                         for wgt in Selection._optionalToIterable(weight)]
        self.binnings = binnings
        self.title = title
        self.axisTitles = axisTitles
        self.axisBinLabels = axisBinLabels
        self.plotopts = plotopts if plotopts else dict()
        # register with backend
        selection.registerPlot(self, autoSyst=autoSyst)

    def clone(
            self, name=None, variables=None, selection=None, binnings=None, weight=None, title=None,
            axisTitles=None, axisBinLabels=None, plotopts=None, autoSyst=True, key=None):
        """ Helper method: create a copy with optional re-setting of attributes """
        return Plot((name if name is not None else self.name),
                    (variables if variables is not None else self.variables),
                    (selection if selection is not None else self.selection),
                    (binnings if binnings is not None else self.binnings),
                    weight=(weight if weight is not None else self._weights),
                    title=(title if title is not None else self.title),
                    axisTitles=(axisTitles if axisTitles is not None else self.axisTitles),
                    axisBinLabels=(axisBinLabels if axisBinLabels is not None else self.axisBinLabels),
                    plotopts=(plotopts if plotopts is not None else self.plotopts),
                    autoSyst=autoSyst,
                    key=key  # default is name
                    )

    def produceResults(self, bareResults, fbe, key=None):
        """
        Trivial implementation of :py:meth:`~bamboo.plots.Product.produceResults`

        Subclasses can e.g. calculate additional systematic variation histograms from the existing ones

        :param bareResults: list of nominal and systematic variation histograms
            for this :py:class:`~bamboo.plots.Plot`
        :param fbe: reference to the backend
        :param key: key under which the backend stores the results (if any)

        :returns: ``bareResults``
        """
        return bareResults

    @property
    def cut(self):
        return self.selection.cut

    @property
    def weights(self):
        return self.selection.weights + self._weights

    @property
    def longTitle(self):
        return ";".join(chain([self.title], self.axisTitles))

    def __repr__(self):
        return (
            f"Plot({self.name!r}, {self.variables!r}, {self.selection!r}, {self.binnings!r}, "
            f"title={self.title!r}, axisTitles={self.axisTitles!r})")

    @classmethod
    def make1D(plotCls, name, variable, selection, binning, **kwargs):
        """ Construct a 1-dimensional histogram plot

        :param name: unique plot name
        :param variable: x-axis variable expression
        :param selection: the :py:class:`~bamboo.plots.Selection` with cuts and weights to apply
        :param binning: x-axis binning
        :param weight: per-entry weight (optional, multiplied with the selection weight)
        :param title: plot title
        :param xTitle: x-axis title (optional, taken from plot title by default)
        :param xBinLabels: x-axis bin labels (optional)
        :param plotopts: dictionary of options to pass directly to plotIt (optional)
        :param autoSyst: automatically add systematic variations (True by default - set to False to turn off)

        :returns: the new :py:class:`~bamboo.plots.Plot` instance with a 1-dimensional histogram

        :Example:

        >>> hasTwoEl = noSel.refine(cut=(op.rng_len(t.Electron) >= 2))
        >>> mElElPlot = Plot.make1D(
        >>>     "mElEl", op.invariant_mass(t.Electron[0].p4, t.Electron[1].p4), hasTwoEl,
        >>>     EquidistantBinning(80, 50., 130.), title="Invariant mass of the leading-PT electrons")
        """
        title = kwargs.pop("title", "")
        kwargs["axisTitles"] = (kwargs.pop("xTitle", title),)
        kwargs["axisBinLabels"] = (kwargs.pop("xBinLabels", None),)
        return plotCls(name, (adaptArg(variable),), selection, (binning,), **kwargs)

    @classmethod
    def make2D(plotCls, name, variables, selection, binnings, **kwargs):
        """ Construct a 2-dimensional histogram plot

        :param name: unique plot name
        :param variables: x- and y-axis variable expression (iterable, e.g. tuple or list)
        :param selection: the :py:class:`~bamboo.plots.Selection` with cuts and weights to apply
        :param binnings: x- and y-axis binnings (iterable, e.g. tuple or list)
        :param weight: per-entry weight (optional, multiplied with the selection weight)
        :param title: plot title
        :param xTitle: x-axis title (optional, empty by default)
        :param yTitle: y-axis title (optional, empty by default)
        :param xBinLabels: x-axis bin labels (optional)
        :param yBinLabels: y-axis bin labels (optional)
        :param plotopts: dictionary of options to pass directly to plotIt (optional)
        :param autoSyst: automatically add systematic variations (True by default - set to False to turn off)

        :returns: the new :py:class:`~bamboo.plots.Plot` instance with a 2-dimensional histogram
        """
        kwargs["axisTitles"] = (kwargs.pop("xTitle", ""), kwargs.pop("yTitle", ""))
        kwargs["axisBinLabels"] = (kwargs.pop("xBinLabels", None), kwargs.pop("yBinLabels", None))
        return plotCls(name, tuple(adaptArg(v) for v in variables), selection, binnings, **kwargs)

    @classmethod
    def make3D(plotCls, name, variables, selection, binnings, **kwargs):
        """ Construct a 3-dimensional histogram

        :param name: unique plot name
        :param variables: x-, y- and z-axis variable expression (iterable, e.g. tuple or list)
        :param selection: the :py:class:`~bamboo.plots.Selection` with cuts and weights to apply
        :param binnings: x-, y-, and z-axis binnings (iterable, e.g. tuple or list)
        :param weight: per-entry weight (optional, multiplied with the selection weight)
        :param title: plot title
        :param xTitle: x-axis title (optional, empty by default)
        :param yTitle: y-axis title (optional, empty by default)
        :param zTitle: z-axis title (optional, empty by default)
        :param xBinLabels: x-axis bin labels (optional)
        :param yBinLabels: y-axis bin labels (optional)
        :param zBinLabels: z-axis bin labels (optional)
        :param plotopts: dictionary of options to pass directly to plotIt (optional)
        :param autoSyst: automatically add systematic variations (True by default - set to False to turn off)

        :returns: the new :py:class:`~bamboo.plots.Plot` instance with a 3-dimensional histogram
        """
        kwargs["axisTitles"] = (
            kwargs.pop("xTitle", ""),
            kwargs.pop("yTitle", ""),
            kwargs.pop("zTitle", "")
        )
        kwargs["axisBinLabels"] = (
            kwargs.pop("xBinLabels", None),
            kwargs.pop("yBinLabels", None),
            kwargs.pop("zBinLabels", None)
        )
        return plotCls(name, tuple(adaptArg(v) for v in variables), selection, binnings, **kwargs)


class Selection:
    """ A :py:class:`~bamboo.plots.Selection` object groups a set of selection criteria
    (cuts) and weight factors that belong to a specific stage of the selection and analysis.
    Selections should be constructed by calling the :py:meth:`~bamboo.plots.Selection.refine`
    method on a 'root' selection (which may include overall selections and weights, e.g.
    a lumi mask for data and pileup reweighting for MC).

    .. note::

        All :py:class:`~bamboo.plots.Selection` (and :py:class:`~bamboo.plots.Plot`) instances
        need to have a unique name. This name is used internally to define DataFrame columns
        with readable names.
        The constructor will raise an exception if an existing name is used.
    """
    def __init__(self, parent, name, cuts=None, weights=None, autoSyst=True):
        """
        Constructor. Prefer using :py:meth:`~bamboo.plots.Selection.refine` instead
            (except for the 'root' selection)

        :param parent: backend or parent selection
        :param name: (unique) name of the selection
        :param cuts: iterable of selection criterion expressions (optional)
        :param weights: iterable of weight factors (optional)
        """
        self.name = name
        self.parent = None
        self._cuts = [adaptArg(cut, typeHint=top.boolType)
                      for cut in Selection._optionalToIterable(cuts)]
        self._weights = [adaptArg(wgt, typeHint=top.floatType)
                         for wgt in Selection._optionalToIterable(weights)]
        self._cSysts = {}
        self._wSysts = {}
        # register with backend
        if isinstance(parent, Selection):
            self.autoSyst = parent.autoSyst and autoSyst
            self.parent = parent
            self._fbe = parent._fbe
        else:
            self.autoSyst = autoSyst
            assert isinstance(parent, FactoryBackend)
            self._fbe = parent
        if self.autoSyst:
            # { varName : { expr : [ nodes to change ] } }
            self._cSysts = top.collectSystVars(self._cuts)
            self._wSysts = top.collectSystVars(self._weights)
        self._fbe.addSelection(self)

    def registerPlot(self, plot, **kwargs):
        self._fbe.addPlot(plot, **kwargs)

    def registerSkim(self, skim, **kwargs):
        self._fbe.addSkim(skim, **kwargs)

    def registerDerived(self, product, **kwargs):
        self._fbe.addDerived(product, **kwargs)

    def registerCutFlowReport(self, product, selections, **kwargs):
        self._fbe.addCutFlowReport(product, selections, **kwargs)

    # helper: convert None, single item, or iterable arg to iterable
    @staticmethod
    def _optionalToIterable(arg):
        if arg is None:
            return []
        else:
            if (isinstance(arg, top.TupleOp) or isinstance(arg, top.TupleBaseProxy)
                    or not hasattr(arg, "__iter__")):
                return [arg]
            else:
                return arg

    @property
    def cuts(self):
        if self.parent:
            return self.parent.cuts + self._cuts
        else:
            return self._cuts

    @property
    def weights(self):
        if self.parent:
            return self.parent.weights + self._weights
        else:
            return self._weights

    @property
    def weightSystematics(self):
        if self.parent:
            ret = self.parent.weightSystematics  # new set
            ret.update(self._wSysts)
            return ret
        else:
            return set(self._wSysts)

    @property
    def cutSystematics(self):
        if self.parent:
            ret = self.parent.cutSystematics  # new set
            ret.update(self._cSysts)
            return ret
        else:
            return set(self._cSysts)

    @property
    def systematics(self):
        ret = self.weightSystematics  # new set
        ret.update(self.cutSystematics)
        return ret
    # for debugging/monitoring: full cut and weight expression ## TODO review
    @property
    def cut(self):
        return Selection._makeExprAnd(self.cuts)

    @property
    def weight(self):
        return Selection._makeExprProduct(self.weights)

    def __repr__(self):  # TODO maybe change to refer to parent
        return f"{self.__class__.__name__}({self.name!r}, {self.cut!r}, {self.weight!r})"

    def __eq__(self, other):
        #  FIXME do we even still need this?
        return (
            (len(self.cuts) == len(other.cuts))
            and all(sc == oc for sc, oc in zip(self.cuts, other.cuts))
            and (len(self.weights) == len(other.weights))
            and all(sw == ow for sw, ow in zip(self.weights, other.weights)))

    def refine(self, name, cut=None, weight=None, autoSyst=True):
        """ Create a new selection by adding cuts and/or weight factors

        :param name: unique name of the new selection
        :param cut: expression (or list of expressions) with additional selection criteria
            (combined using logical AND)
        :param weight: expression (or list of expressions) with additional weight factors
        :param autoSyst: automatically add systematic variations
            (True by default - set to False to turn off; note that this would also turn off
            automatic systematic variations for any selections and plots
            that derive from the one created by this method)

        :returns: the new :py:class:`~bamboo.plots.Selection`
        """
        return self.__class__(self, name, cuts=cut, weights=weight, autoSyst=autoSyst)

    @staticmethod
    def _makeExprAnd(listOfReqs):
        # op.AND for expressions (helper for histfactory etc.)
        if len(listOfReqs) > 1:
            return adaptArg(op.AND(*listOfReqs))
        elif len(listOfReqs) == 1:
            return listOfReqs[0]
        else:
            return adaptArg("true", typeHint=top.boolType)

    @staticmethod
    def _makeExprProduct(listOfFactors):
        # op.product for expressions (helper for histfactory etc.)
        if len(listOfFactors) > 1:
            return adaptArg(op.product(*listOfFactors))
        elif len(listOfFactors) == 1:
            return listOfFactors[0]
        else:
            return adaptArg(1., typeHint=top.floatType)


class DerivedPlot(Product):
    """
    Base class for a plot with results based on other plots' results

    The :py:attr:`~bamboo.plots.DerivedPlot.dependencies` attribute that lists
    the :py:class:`~bamboo.plots.Plot`-like objects this one depends on (which
    may be used e.g. to order operations).
    The other necessary properties (binnings, titles, labels, etc.) are taken
    from the keyword arguments to the constructor, or the first dependency.
    The :py:meth:`~bamboo.plots.DerivedPlot.produceResults` method,
    which is called by the backend to retrieve the derived results,
    should be overridden with the desired calculation.

    Typical use cases are summed histograms, background subtraction, etc.
    (the results are combined for different subjobs with hadd, so derived
    quantities that require the full statistics should be calculated from
    the postprocessing step; alternative or additional systematic variations
    calculated from the existing ones can be added by subclassing
    :py:class:`~bamboo.plots.Plot`).
    """
    def __init__(self, name, dependencies, **kwargs):
        super().__init__(name)
        if "__" in name:
            raise RuntimeError(
                "No '__' should be present in the name of a derived plot: "
                "it is reserved for separating the name from systematic variations")
        self.dependencies = dependencies
        self.binnings = kwargs.get("binnings", dependencies[0].binnings)
        self.axisTitles = kwargs.get(
            "axisTitles", tuple(
                kwargs.get(f"{ax}Title", dependencies[0].axisTitles[i])
                for i, ax in enumerate("xyzuvw"[:len(self.variables)])))
        self.axisBinLabels = kwargs.get(
            "axisBinLabels", tuple(
                kwargs.get(f"{ax}BinLabels", dependencies[0].axisBinLabels[i])
                for i, ax in enumerate("xyzuvw"[:len(self.variables)])))
        self.plotopts = kwargs.get("plotopts", dependencies[0].plotopts)
        # register with backend
        dependencies[0].selection.registerDerived(self)

    @property
    def variables(self):
        return [None for x in self.binnings]

    def produceResults(self, bareResults, fbe, key=None):
        """
        Main interface method, called by the backend

        :param bareResults: iterable of histograms for this plot produced by the backend (none)
        :param fbe: reference to the backend, can be used to retrieve the histograms for the dependencies,
            e.g. with :py:meth:`~bamboo.plots.DerivedPlot.collectDependencyResults`
        :param key: key under which the backend stores the results (if any)

        :returns: an iterable with ROOT objects to save to the output file
        """
        return []

    def collectDependencyResults(self, fbe, key=None):
        """ helper method: collect all results of the dependencies

        :returns: ``[ (nominalResult, {"variation" : variationResult}) ]``
        """
        res_dep = []
        for dep in self.dependencies:
            resNom = None
            resPerVar = {}
            depResults = fbe.getResults(dep, key=(
                (dep.name, key[1]) if key is not None and len(key) == 2 else None))
            if depResults:
                for res in depResults:
                    if "__" not in res.GetName():
                        assert resNom is None
                        resNom = res
                    else:
                        resVar = res.GetName().split("__")[1]
                        resPerVar[resVar] = res
                res_dep.append((resNom, resPerVar))
        return res_dep


class SummedPlot(DerivedPlot):
    """ A :py:class:`~bamboo.plots.DerivedPlot` implementation that sums histograms """
    def __init__(self, name, termPlots, **kwargs):
        super().__init__(name, termPlots, **kwargs)

    def produceResults(self, bareResults, fbe, key=None):
        from .root import gbl
        res_dep = self.collectDependencyResults(fbe, key=key)
        if not res_dep:
            return []
        # list all variations (some may not be there for all)
        allVars = set()
        for _, resVar in res_dep:
            allVars.update(resVar.keys())
        # sum nominal
        hNom = res_dep[0][0].Clone(self.name)
        for ihn, _ in res_dep[1:]:
            if not isinstance(ihn, gbl.TH1):
                ihn = ihn.GetPtr()
            hNom.Add(ihn)
        results = [hNom]
        # sum variations (using nominal if not present for some)
        for vn in allVars:
            hVar = res_dep[0][1].get(vn, res_dep[0][0]).Clone("__".join((self.name, vn)))
            for ihn, ihv in res_dep[1:]:
                hvi = ihv.get(vn, ihn)
                if not isinstance(hvi, gbl.TH1):
                    hvi = hvi.GetPtr()
                hVar.Add(hvi)
            results.append(hVar)
        return results


class CutFlowReport(Product):
    """
    Collect and print yields at different selection stages, and cut efficiencies

    The simplest way to use this, just to get an overview of the number of events
    passing each selection stage in the log file, is by adding a
    ``CutFlowReport("yields", selections=<list of selections>, recursive=True, printInLog=True)``
    to the list of plots.
    ``recursive=True`` will add all parent selections recursively,
    so only the final selection categories need to be passed to the ``selections``
    keyword argument.

    It is also possible to output a LaTeX yields table, and specify exactly which
    selections and row or column headers are used.
    Then the :py:class:`~bamboo.plots.CutFlowReport` should be constructed like this:

    .. code-block:: python

       yields = CutFlowReport("yields")
       plots.append(yields)
       yields.add(<selection1-or-list-of-selections1>, title=title1)
       yields.add(<selection2-or-list-of-selections2>, title=title2)
       ...

    Each ``yields.add`` call will then add one entry in the yields table,
    with the yield the one of the corresponding selection, or the sum over
    the list (e.g. different categories that should be taken together);
    the other dimension are the samples (or sample groups).
    The sample (group) titles and formatting of the table can be
    customised in the same way as in plotIt, see
    :py:func:`~bamboo.analysisutils.printCutFlowReports`
    for a detailed description of the different options.
    """
    class Entry:  # counters for one selection
        def __init__(self, name, nominal=None, systVars=None, parent=None, children=None):
            self.name = name
            self.nominal = nominal
            self.systVars = systVars or dict()
            self.parent = parent
            self.children = list(children) if children is not None else []

        def _load(self, tmpF):
            if isinstance(self.nominal, str):
                self.nominal = tmpF.Get(self.nominal)
                self.systVars = {svNm: tmpF.Get(svV) for svNm, svV in self.systVars}
            return self

        def setParent(self, parent):
            self.parent = parent
            if self not in parent.children:
                parent.children.append(self)

    def __init__(
            self, name, selections=None, recursive=False, titles=None, autoSyst=False,
            cfres=None, printInLog=False):
        """
        Constructor. ``name`` is mandatory, all other are optional; for full control
        the :py:meth:`~bamboo.plots.CutFlowReport.add` should be used to add entries.

        Using the constructor with a list of :py:class:`~bamboo.plots.Selection`
        instances passed to the ``selections`` keyword argument, and ``recursive=True, printInLog=True``
        is the easiest way to get debugging printout of the numbers of passing events.
        """
        super().__init__(name)
        self.recursive = recursive
        if selections is None:
            self.selections = []
        else:
            self.selections = list(selections) if hasattr(selections, "__iter__") else [selections]
        self.titles = defaultdict(list)
        if titles is not None:
            self.titles = titles
        elif self.selections:
            self.titles.update({sel.name: sel.name for sel in self.selections})
        self.autoSyst = autoSyst
        self.cfres = cfres if cfres is not None else defaultdict(list)
        if self.selections and cfres is None:
            self._register()
        self.printInLog = printInLog

    def _register(self, selections=None):
        if selections is None:
            selections = self.selections
        aSelection = selections[0]
        selections = {sel.name: sel for sel in selections}
        if self.recursive:
            for sel in list(selections.values()):
                isel = sel.parent
                while isel is not None and isel.name not in selections:
                    selections[isel.name] = isel
        aSelection.registerCutFlowReport(self, selections, autoSyst=self.autoSyst)
        sels_per_sub = defaultdict(dict)
        for selName, sel in selections.items():
            if isinstance(sel, SelectionWithSub):
                sel.initSub()
                for suffix, subSel in sel.sub.items():
                    if subSel is not None:
                        sels_per_sub[suffix][selName] = subSel
        for suffix, subSels in sels_per_sub.items():
            logger.debug(f"Registering counters for {suffix} part of {', '.join(subSels.keys())}")
            aSelection.registerCutFlowReport(
                self, subSels, key=(self.name, suffix), autoSyst=self.autoSyst)

    def add(self, selections, title=None):
        """ Add an entry to the yields table, with a title (optional) """
        if not hasattr(selections, "__iter__"):
            selections = [selections]
        selections = [sel for sel in selections if sel not in self.selections]
        if title is not None:
            self.titles[title] += [sel.name for sel in selections]
        else:
            self.titles.update({sel.name: sel.name for sel in selections})
        if selections:
            self.selections += selections
            self._register(selections)

    def produceResults(self, bareResults, fbe, key=None):
        entries = list()
        for iEn in self.cfres[key if key else self.name]:  # self.cfres was set by addCutFlowReport
            while iEn is not None and iEn not in entries:
                entries.append(iEn)
                iEn = iEn.parent
        return ([res.nominal.product for res in entries]
                + [v.product for res in entries for v in res.systVars.values()])

    def rootEntries(self):
        # helper: traverse reports tree up
        def travUp(entry):
            yield entry
            yield from travUp(entry.parent)
        return {next(en for en in travUp(res) if en.parent is None)
                for lres in self.cfres.values() for res in lres}

    def readFromResults(self, resultsFile):
        """ Reconstruct the :py:class:`~bamboo.plots.CutFlowReport`, reading counters from a results file """
        cfres = []
        entries = {}  # by selection name
        for sel in self.selections:
            if sel.name not in entries:
                entries[sel.name] = CutFlowReport.Entry(sel.name)
                if self.recursive:
                    isel = sel.parent
                    entry_d = entries[sel.name]
                    while isel is not None:
                        if isel.name in entries:
                            entry_p = entries[isel.name]
                            entry_d.setParent(entry_p)
                            break
                        entry_p = CutFlowReport.Entry(isel.name)
                        entries[isel.name] = entry_p
                        entry_d.setParent(entry_p)
                        entry_d = entry_p
                        isel = isel.parent
            cfres.append(entries[sel.name])
        # retrieve nominal
        for selName, entry in entries.items():
            kyNm = f"{self.name}_{selName}"
            obj = resultsFile.Get(kyNm)
            if obj:
                entry.nominal = obj
        # and systematic variations
        prefix = f"{self.name}_"
        for ky in resultsFile.GetListOfKeys():
            if ky.GetName().startswith(prefix):
                selName = ky.GetName().split("__")[0][len(prefix):]
                if selName in entries:
                    entry = entries[selName]
                    cnt = ky.GetName().count("__")
                    if cnt == 1:
                        varNm = ky.GetName().split("__")[1]
                        if varNm in entry.systVars:
                            logger.warning(f"{self.name}: counter for variation {varNm} "
                                           f"already present for selection {selName}")
                        entry.systVars[varNm] = ky.ReadObj()
                    elif cnt > 1:
                        logger.warning("Key {ky.GetName()!r} contains '__' more than once, "
                                       "this will break assumptions")
        return CutFlowReport(
            self.name, self.selections, titles=self.titles, recursive=self.recursive,
            autoSyst=self.autoSyst, cfres={self.name: cfres}, printInLog=self.printInLog)


class SelectionWithSub(Selection):
    """
    A common base class for :py:class:`~bamboo.plots.Selection` subclasses
        with related/alternative/sub-:py:class:`~bamboo.plots.Selection` instances attached

    A dictionary of additional selections is kept in the ``sub`` attribute (could be ``None`` to disable).
    """
    def __init__(self, parent, name, cuts=None, weights=None, autoSyst=True, sub=None):
        super().__init__(parent, name, cuts=cuts, weights=weights, autoSyst=autoSyst)
        self.sub = sub if sub is not None else dict()

    def initSub(self):
        """
        Initialize related selections
            (no-op by default, subclasses can request to call this to enable some functionality)
        """
        pass

    @staticmethod
    def getSubsForPlot(p, requireActive=False, silent=False):
        """ Helper method: gather the sub-selections for which a plot is produced """
        subs = set()
        if isinstance(p, Plot):
            if isinstance(p.selection, SelectionWithSub):
                for suff, subSel in p.selection.sub.items():
                    if (not requireActive) or (subSel is not None):
                        subs.add(suff)
        elif isinstance(p, DerivedPlot):
            for dp in p.dependencies:
                if isinstance(dp.selection, SelectionWithSub):
                    for suff, subSel in dp.selection.sub.items():
                        if (not requireActive) or (subSel is not None):
                            subs.add(suff)
        elif isinstance(p, CutFlowReport):
            for sel in p.selections:
                if isinstance(sel, SelectionWithSub):
                    for suff, subSel in sel.sub.items():
                        if (not requireActive) or (subSel is not None):
                            subs.add(suff)
        elif not silent:
            logger.warning(
                f"Unsupported product type for data-driven: {type(p).__name__}, "
                "additional products will not be stored")
        return subs

    def refine(self, name, cut=None, weight=None, autoSyst=True):
        main = super().refine(name, cut=cut, weight=weight, autoSyst=autoSyst)
        main.sub = {suff: (
            parent.refine("".join((name, suff)), cut=cut, weight=weight, autoSyst=autoSyst)
            if parent is not None else None) for suff, parent in self.sub.items()}
        return main


class SelectionWithDataDriven(SelectionWithSub):
    """
    A main :py:class:`~bamboo.plots.Selection` with the corresponding "shadow"
        :py:class:`~bamboo.plots.Selection` instances for evaluating data-driven backgrounds
        (alternative cuts and/or weights)
    """
    @staticmethod
    def create(
            parent, name, ddSuffix, cut=None, weight=None, autoSyst=True,
            ddCut=None, ddWeight=None, ddAutoSyst=True, enable=True):
        """
        Create a selection with a data-driven shadow selection

        Drop-in replacement for a :py:meth:`bamboo.plots.Selection.refine` call:
        the main selection is made from the parent with ``cut`` and ``weight``,
        the shadow selection is made from the parent with ``ddCut`` and ``ddWeight``.
        With ``enable=False`` no shadow selection is made (this may help to avoid
        duplication in the calling code).
        """
        ddName = "".join((name, ddSuffix))
        ddSel = None
        if isinstance(parent, SelectionWithSub):
            if cut is None and weight is None and autoSyst == parent.autoSyst:
                main = parent
            else:
                main = parent.refine(name, cut=cut, weight=weight, autoSyst=autoSyst)
            if enable:
                ddSel = Selection.refine(
                    parent, ddName, cut=ddCut, weight=ddWeight, autoSyst=ddAutoSyst)
        else:  # create from regular Selection
            main = SelectionWithDataDriven(parent, name, cuts=cut, weights=weight, autoSyst=autoSyst)
            if enable:
                ddSel = parent.refine(ddName, cut=ddCut, weight=ddWeight, autoSyst=ddAutoSyst)
        if ddSel is not None:
            logger.debug(f"Adding the data-driven counterpart of {name} for the {ddSuffix} contribution")
        main.sub[ddSuffix] = ddSel
        return main

    def registerPlot(self, plot, **kwargs):
        super().registerPlot(plot, **kwargs)
        for ddSuffix, ddSel in self.sub.items():
            if ddSel is not None:
                # will register and go out of scope
                # (the module has all necessary information to retrieve and process the results;
                # everything by reference, so cheap)
                plot.clone(selection=ddSel, key=(plot.name, ddSuffix), **kwargs)
    # NOTE registerDerived not overridden, since none of the current backends need it


class CategorizedSelection:
    """
    Helper class to represent a group of similar selections on different categories

    The interface is similar, but not identical to that of :py:class:`~bamboo.plots.Selection`
    (constructing :py:class:`~bamboo.plots.Plot` objects is done through the
    :py:meth:`~bamboo.plots.CategorizedSelection.makePlots` method,
    which takes additional arguments).
    Each category selection can have a candidate, typically the object
    or group of object that differs between the categories.
    The axis variables can then either be expressions, or callables
    that will be passed this per-category object.

    :Example:

    >>> muonSel = noSel.refine("hasMuon", cut=(
    >>>     op.rng_len(muons) > 0, op.OR(op.rng_len(electrons) == 0,
    >>>     muons[0].pt > electrons[0].pt)))
    >>> electronSel = noSel.refine("hasElectron", cut=(
    >>>     op.rng_len(electrons) > 0, op.OR(op.rng_len(muons) == 0,
    >>>     electrons[0].pt > muons[0].pt)))
    >>> oneLeptonSel = CategorizedSelection(categories={
    ...     "Mu" : (muonSel, muons[0]),
    ...     "El" : (electronSel, electrons[0])
    ...     })
    >>> oneLep2JSel = onLeptonSel.refine("hasLep2J", cut=(op.rng_len(jets) >= 2))
    >>> plots += oneLep2JSel.makePlots("J1PT", jets[0].pt, EqB(50, 0., 150.))
    >>> plots += oneLep2JSel.makePlots("LJ1Mass",
    ...     (lambda l : op.invariant_mass(jets[0].p4, l.p4)), EqB(50, 0., 200.))
    """
    def __init__(self, parent=None, categories=None, name=None):
        """
        Construct a group of related selections

        :param name: name (optional)
        :param parent: parent CategorizedSelection (optional)
        :param categories: dictionary of a :py:class:`~bamboo.plots.Selection` and candidate
            (any python object) per category (key is category name),
            see the :py:meth:`~CategorizedSelection.addCategory` method below
        """
        self.name = name
        self.categories = categories
        self.parent = parent

    def addCategory(self, catName, selection, candidate=None):
        """
        Add a category

        :param catName: category name
        :param selection: :py:class:`~bamboo.plots.Selection` for this category
        :param candidate: any python object with event-level quantities specific to this category
        """
        if catName in self.categories:
            raise ValueError(f"A category with name {catName} is already present")
        self.categories[catName] = (selection, candidate)

    def refine(self, name, cut=None, weight=None, autoSyst=True):
        """
        Equivalent of :py:meth:`~bamboo.plots.Selection.refine`, but for all categories at a time

        :param name: common part of the name for the new category selections
            (individual names will be ``"{name}_{category}``)
        :param cut: cut(s) to add. If callable, the category's candidate will be passed
        :param weight: weight(s) to add. If callable, the category's candidate will be passed
        :param autoSyst: automatically add systematic variations
            (True by default - set to False to turn off; note that this would also turn off
            automatic systematic variations for any selections and plots that derive
            from the one created by this method)

        :returns: the new :py:class:`CategorizedSelection`
        """
        if cut is not None and not hasattr(cut, "__iter__"):
            cut = [cut]
        if weight is not None and not hasattr(weight, "__iter__"):
            weight = [weight]
        newCatsAndCands = {}
        for catName, (catSel, catCand) in self.categories.items():
            catCut = cut
            if cut is not None:
                catCut = [(ict if not callable(ict) else ict(catCand)) for ict in cut]
            catWeight = weight
            if weight is not None:
                catWeight = [(iwt if not callable(iwt) else iwt(catCand)) for iwt in weight]
            newCatsAndCands[catName] = (catSel.refine(
                f"{name}_{catName}", cut=catCut, weight=catWeight, autoSyst=autoSyst), catCand)
        return CategorizedSelection(name=name, parent=self, categories=newCatsAndCands)

    def makePlots(
            self, name, axisVariables, binnings, construct=None, savePerCategory=True,
            saveCombined=True, combinedPlotType=SummedPlot, **kwargs):
        """
        Make a plot for all categories, and/or a combined one

        :param name: plot name (per-category plot names will be ``"{name}_{category}"``)
        :param axisVariables: one or more axis variables
        :param binnings: as many binnings as variables
        :param construct: plot factory method, by default the ``make{N}D`` method of
            :py:class:`~bamboo.plots.Plot` (with N the number of axis variables)
        :param savePerCategory: save the individual plots (enabled by default)
        :param saveCombine: save the combined plot (enabled by default)
        :param combinedPlotType: combined plot type, :py:class:`~bamboo.plots.SummedPlot` by default

        :returns: a list of plots
        """
        if (not savePerCategory) and (not saveCombined):
            return []  # no need to make plots then :-)
        if not hasattr(axisVariables, "__iter__"):
            axisVariables = [axisVariables]
        if construct is None:  # default: use `Plot.makeND`
            construct = getattr(Plot, f"make{len(axisVariables):d}D")
        catPlots = []
        for catName, (catSel, catCand) in self.categories.items():
            variables = [(iVar if not callable(iVar) else iVar(catCand)) for iVar in axisVariables]
            if len(variables) == 1:
                variables = variables[0]
            catPlots.append(construct(f"{name}_{catName}", variables, catSel, binnings, **kwargs))
        if not saveCombined:
            return catPlots
        else:
            return catPlots + [combinedPlotType(name, catPlots)]


class LateSplittingSelection(SelectionWithSub):
    """
    A drop-in replacement for :py:class:`~bamboo.plots.Selection` to efficiently split a sample

    The concept is quite similar to :py:class:`~bamboo.plots.SelectionWithDataDriven`,
    but with very different performance trade-offs: the former creates two parallel branches of
    the RDF graph, each for their own set of events (with a typically small performance
    overhead due to dupliation), whereas this is for cases where all events should be processed
    identically until they are filled into histograms (e.g. separating subprocesses based on
    MC truth). It is worth defining columns with these categories early on, such that the splitting
    does not need to do it many times for different selections and categories.
    """
    def __init__(self, parent, name, cuts=None, weights=None, autoSyst=True, keepInclusive=None):
        super().__init__(parent, name, cuts=cuts, weights=weights, autoSyst=autoSyst)
        self.splitCuts = {}
        if isinstance(parent, LateSplittingSelection):
            self.splitCuts = parent.splitCuts
        if keepInclusive is not None:
            self.keepInclusive = keepInclusive
        elif isinstance(parent, LateSplittingSelection):
            self.keepInclusive = parent.keepInclusive
        else:
            self.keepInclusive = True

    @staticmethod
    def create(parent, name, splitCuts=None, keepInclusive=True, cut=None, weight=None, autoSyst=True):
        """
        Create a selection that will lazily split into categories

        :param name: name of the new selection (after applying the cut and weight,
            as in :py:meth:`bamboo.plots.Selection.refine`)
        :param splitCuts: dictionary of regions, the values should be the cuts that define the region
        :param keepInclusive: also produce the plots without splitting
        :param cut: common selection
        :param weight: common weight
        :param autoSyst: automatically propagate systematic uncertainties
        """
        if isinstance(parent, SelectionWithSub):
            raise RuntimeError(
                "LateSplittingSelection must be constructed before any SelectionWithSub, "
                "and extending is not supported")
        lsSel = LateSplittingSelection(
            parent, name, cuts=cut, weights=weight, autoSyst=autoSyst, keepInclusive=keepInclusive)
        lsSel.splitCuts = splitCuts if splitCuts is not None else {}
        return lsSel

    def initSub(self):
        """
        Initialize related selections, should be called before registering non-plot products
            (anything not going through registerPlot)
        """
        if self.splitCuts and any(suff not in self.sub for suff in self.splitCuts):
            self.sub.update({
                suff: Selection(self, f"{self.name}{suff}", cuts=cut)
                for suff, cut in self.splitCuts.items()
                if suff not in self.sub
            })

    def registerPlot(self, plot, **kwargs):
        # always still produce the original one (it helps with having all variables defined)
        if self.keepInclusive:
            super().registerPlot(plot, **kwargs)
        if self.splitCuts:
            # here is the trick: per-category selections are only created once we attach a plot
            self.initSub()
            for suff, sSel in self.sub.items():
                if sSel is not None:
                    plot.clone(selection=sSel, key=(plot.name, suff), **kwargs)


class Skim(Product):
    """
    Save selected branches for events that pass the selection to a skimmed tree
    """
    KeepAll = object()

    class KeepRegex:
        def __init__(self, pattern):
            self.pattern = pattern

    def __init__(
            self, name, branches, selection, keepOriginal=None,
            maxSelected=-1, treeName=None, key=None):
        """
        Skim constructor

        :param name: name of the skim (also default name of the TTree)
        :param branches: dictionary of branches to keep (name and definition for new branches,
            or name and ``None`` for specific branches from the input tree)
        :param selection: :py:class:`~bamboo.plots.Selection` of events to save
        :param keepOriginal: list of branch names to keep, :py:obj:`bamboo.plots.Skim.KeepRegex`
            instances with patterns of branch names to keep, or :py:obj:`bamboo.plots.Skim.KeepAll`
            to keep all branches from the input tree
        :param maxSelected: maximal number of events to keep (default: no limit)

        :Example:

        >>> plots.append(Skim("dimuSkim", {
        >>>     "run": None,  # copy from input
        >>>     "luminosityBlock": None,
        >>>     "event": None,
        >>>     "dimu_m": op.invariant_mass(muons[0].p4, muons[1].p4),
        >>>     "mu1_pt": muons[0].pt,
        >>>     "mu2_pt": muons[1].pt,
        >>>     }, twoMuSel,
        >>>     keepOriginal=[
        >>>         Skim.KeepRegex("PV_.*"),
        >>>         "nOtherPV",
        >>>         Skim.KeepRegex("OtherPV_.*")
        >>>         ])
        """
        super().__init__(name, key=key)
        self.definedBranches = {k: v for k, v in branches.items() if v is not None}
        self.originalBranches = [k for k, v in branches.items() if v is None]
        if keepOriginal:
            from collections.abc import Iterable
            if isinstance(keepOriginal, Iterable) and not isinstance(keepOriginal, str):
                self.originalBranches.extend(keepOriginal)
            else:
                self.originalBranches.append(keepOriginal)
        self.selection = selection
        self.maxSelected = maxSelected
        self.treeName = treeName or name
        selection.registerSkim(self)

    def produceResults(self, bareResults, fbe, key=None):
        return bareResults
