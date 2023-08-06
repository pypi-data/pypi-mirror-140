"""
Expressions are constructed by executing python code on decorated versions of
decorated trees. The :py:mod:`bamboo.treedecorators` module contains helper
methods to do so for commonly used formats, e.g. :py:func:`~.decorateNanoAOD`
for CMS NanoAOD.
"""

import logging
from collections import defaultdict
from functools import partial
from itertools import chain

from . import treefunctions as tf
from . import treeoperations as top
from . import treeproxies as tpx

logger = logging.getLogger(__name__)


def allLeafs(branch):
    # Recursively collect TTree leaves (TLeaf and TBranchElement)
    from .root import gbl
    for br in branch.GetListOfBranches():
        if isinstance(br, gbl.TBranchElement):
            yield br
        else:
            yield from br.GetListOfLeaves()


def normVarName(varName):
    # Normalize variation name: if ending in up or down, make sure this part has no capitals (for plotIt)
    if len(varName) >= 2 and varName[-2:].upper() == "UP":
        return f"{varName[:-2]}up"
    elif len(varName) >= 4 and varName[-4:].upper() == "DOWN":
        return f"{varName[:-4]}down"
    else:
        return varName

# Attribute classes (like property) to customize the proxy classes


class proxy:  # the default one
    def __init__(self, op):
        self.op = op

    def __get__(self, inst, cls):
        return self.op.result


class funProxy:  # the generic one
    def __init__(self, fun):
        self.fun = fun

    def __get__(self, inst, cls):
        return self.fun(inst)


class itemProxy:
    def __init__(self, op):
        self.op = op

    def __get__(self, inst, cls):
        return self.op[inst._idx]


class itemRefProxy:
    def __init__(self, op, getTarget):
        self.op = op
        self.getTarget = getTarget

    def __get__(self, inst, cls):
        return self.getTarget(inst)[self.op[inst._idx]]


class itemObjProxy:  # re-construct an object that was split in arrays
    def __init__(self, typeName, args):
        self.typeName = typeName
        self.args = args

    def __get__(self, inst, cls):
        return top.Construct(self.typeName, tuple(arg[inst._idx] for arg in self.args)).result


class altProxy:  # grouped: instance has the branch map
    def __init__(self, name, op):
        self.name = name
        self.op = op

    def __get__(self, inst, cls):
        return inst.brMap.get(self.name, self.op).result


class altItemProxy:  # collection carries branch map (instance comes from collection.__getitem__)
    def __init__(self, name, op):
        self.name = name
        self.op = op

    def __get__(self, inst, cls):
        return inst._parent.brMap.get(self.name, self.op).result[inst._idx]


# internal, leaf/group/collection
def _makeAltClassAndMaps(name, dict_orig, vari, getCol=lambda op: op, attCls=None, altBases=None):
    # vari.getVarName should return the variable and variation name (nomName for the nominal one)
    # if this is a systematic variation branch - otherwise None
    dict_alt = dict(dict_orig)
    # collect ops of kinematic variables that change (nominal as well as varied)
    var_atts = defaultdict(dict)
    for nm, nmAtt in dict_orig.items():
        test = vari.getVarName(nm, collgrpname=name)
        if test is not None:
            attNm, varNm = test
            if normVarName(varNm) in var_atts[attNm]:
                raise RuntimeError(
                    f"Variation {normVarName(varNm)} deduced for {nm} (group {name}), "
                    "but already present")
            var_atts[attNm][normVarName(varNm)] = nmAtt.op
            del dict_alt[nm]
    # redirect in altProxy
    for attNm in var_atts.keys():
        dict_alt[attNm] = attCls(attNm, dict_orig[attNm].op)
    cls_alt = type(f"Alt{name}Proxy", altBases, dict_alt)
    # construct the map of maps of redirections { variation: { varName: op } }
    brMapMap = {}
    for attNm, vAtts in var_atts.items():
        for var, vop in vAtts.items():
            if var not in brMapMap:
                brMapMap[var] = {}
            brMapMap[var][attNm] = getCol(vop)
    # nominal: with systematic variations (all are valid, but not all need to modify)
    nomName = vari.origName if vari.isCalc else vari.nomName(name)
    exclVars = list(normVarName(var) for var in vari.exclVars(name))
    allVars = list(k for k in brMapMap.keys() if k not in exclVars and k != nomName)
    for attNm, vAtts in var_atts.items():
        if nomName not in vAtts:
            raise RuntimeError(f"Nominal variation {nomName} not found for {attNm} (in {vAtts.keys()})")
    brMapMap["nomWithSyst"] = {
        attNm: top.SystAltOp(
            getCol(vAtts[nomName]),
            {var: getCol(vop) for var, vop in vAtts.items() if var not in exclVars and var != nomName},
            valid=tuple(var for var in allVars if var in vAtts),
        ) for attNm, vAtts in var_atts.items()}
    return cls_alt, brMapMap


# Helper classes
class NanoSystematicVarSpec:
    """
    Interface for classes that specify how to incorporate systematics
        or on-the-fly corrections in the decorated tree

    See :py:class:`~.NanoAODDescription` and :py:func:`~.decorateNanoAOD`
    """
    def __init__(self, nomName=None, origName=None, exclVars=None, isCalc=False):
        """ Base class constructor

        :param nomName: nominal variation name (for non-calculated variations;
            can be customised in subclasses by overriding the :py:meth:`~.nomName` method)
        :param origName: original variation name (for calculated variations)
        :param exclVars: variations that are found but should not be used in automatic systematics
            (can be customised through :py:meth:`~.nomName`)
        :param isCalc: boolean indicating whether variations are calculated or read from alternative branches
        """
        self._nomName = nomName
        self.origName = origName
        self._exclVars = exclVars if exclVars is not None else tuple()
        self.isCalc = isCalc

    def appliesTo(self, name):
        """
        Return true if this systematic variation requires action
            for this variable, group, or collection
        """
        return False

    def changesTo(self, name):
        """ Return the new name(s) for a collection or group (assuming appliesTo(name) is True) """
        return (name,)

    def getVarName(self, branchName, collgrpname=None):
        """
        Get the variable name and variation corresponding to an
            (unprefixed, in case of groups or collections) branch name """
        pass

    def nomName(self, name):
        """ Nominal systematic variation name for a group/collection """
        return self._nomName

    def exclVars(self, name):
        """ Systematic variations to exclude for a group/collection """
        return self._exclVars


class ReadVariableVarWithSuffix(NanoSystematicVarSpec):
    """ Read variations of a single branch from branches with the same name with a suffix """
    def __init__(self, commonName, sep="_", nomName="nominal", exclVars=None):
        super().__init__(nomName=nomName, exclVars=exclVars, isCalc=False)
        self.prefix = commonName
        self.sep = sep

    def appliesTo(self, name):
        """ True if name starts with the prefix """
        return name.startswith(self.prefix)

    def getVarName(self, branchName, collgrpname=None):
        """ Split into prefix and variation (if present, else nominal) """
        variNm = normVarName(branchName[len(self.prefix):].lstrip(self.sep))
        return self.prefix, variNm if variNm else self.nomName(collgrpname)


nanoPUWeightVar = ReadVariableVarWithSuffix("puWeight")


class ReadJetMETVar(NanoSystematicVarSpec):
    """
    Read jet and MET kinematic variations from different branches for automatic systematic uncertainties

    :param jetsName: jet collection prefix (e.g. ``"Jet"``)
    :param metName: MET prefix (e.g. ``"MET"``)
    :param jetsNomName: name of the nominal jet variation (``"nom"`` by default)
    :param jetsOrigName: name of the original jet variation (``"raw"`` by default)
    :param metNomName: name of the nominal jet variation (``"nom"`` by default)
    :param metOrigName: name of the original jet variation (``"raw"`` by default)
    :param jetsExclVars: jet variations that are present but should be ignored
        (if not specified, only ``jetsOrigName`` is taken, so if specified
        this should usually be added explicitly)
    :param metExclVars: MET variations that are present but should be ignored
        (if not specified, only ``metOrigName`` is taken, so if specified
        this should usually be added explicitly)
    :param bTaggers: list of b-tagging algorithms, for scale factors stored in a branch
    :param bTagWPs: list of b-tagging working points, for scale factors stored in a branch
        (``shape`` should be included here, if wanted)

    .. note:: The implementation of automatic systematic variations treats
       "xyzup" and "xyzdown" independently (since this is the most flexible).
       If a source of systematic uncertainty should be excluded, both the "up"
       and "down" variation should then be added to the list of variations to
       exclude (``jetsExclVars`` or ``metExclVars``).
    """
    def __init__(
            self, jetsName, metName, jetsNomName="nom", jetsOrigName="raw",
            metNomName="", metOrigName="raw", jetsExclVars=None, metExclVars=None,
            bTaggers=None, bTagWPs=None):
        super().__init__(
            nomName=jetsNomName, origName=jetsOrigName, isCalc=False,
            exclVars=(jetsExclVars if jetsExclVars is not None else (jetsOrigName,)))
        self.jetsName = jetsName
        self.metName = metName
        self.metOrigname = metOrigName
        self.bTaggers = bTaggers if bTaggers is not None else []
        self.bTagWPs = bTagWPs if bTagWPs is not None else []
        self.metNomName = metNomName
        self.metExclVars = (metExclVars if metExclVars is not None else (metOrigName,))

    def appliesTo(self, name):
        return name in (self.jetsName, self.metName)

    def nomName(self, name):
        if name == self.metName:
            return self.metNomName
        else:
            return self._nomName

    def exclVars(self, name):
        if name == self.metName:
            return self.metExclVars
        else:
            return self._exclVars

    def getVarName(self, nm, collgrpname=None):
        if nm.split("_")[0] in ("pt", "eta", "phi", "mass"):
            if len(nm.split("_")) >= 2:
                return (nm.split("_")[0], "_".join(nm.split("_")[1:]))
            # Drop no-suffix (stored) variations if configured to do so
            elif collgrpname == self.jetsName:
                if nm in ("eta", "phi") or self._nomName == "":
                    return nm, self._nomName
                else:  # skip
                    return None
            elif collgrpname == self.metName:
                if self.metNomName == "":
                    return nm, ""
                else:  # skip
                    return None
            else:
                raise RuntimeError(f"Cannot interpret {nm} as a variation of a jet or MET kinematic quantity")
        elif nm.startswith("btagSF"):
            for tagger in self.bTaggers:
                for wp in self.bTagWPs:
                    sfName = f"btagSF_{tagger}_{wp}"
                    if not nm.startswith(sfName):
                        continue
                    if nm == sfName:
                        return nm, "nom"
                    upOrDown = "up" if "up" in nm else "down"
                    if wp != "shape":  # b-tag SF systematics
                        return sfName, f"{sfName}{upOrDown}"
                    else:
                        syst = nm.split(f"{sfName}_{upOrDown}_")[1]
                        if "jes" not in syst:  # b-tag shape systematics
                            return sfName, f"{sfName}_{syst}{upOrDown}"
                        else:  # jes systematics
                            if syst == "jes":
                                syst = "jesTotal"
                            return sfName, f"{syst}{upOrDown}"


nanoReadJetMETVar = ReadJetMETVar(
    "Jet", "MET",
    bTaggers=["csvv2", "deepcsv", "deepjet", "cmva"], bTagWPs=["L", "M", "T", "shape"])
nanoReadJetMETVar_METFixEE2017 = ReadJetMETVar(
    "Jet", "METFixEE2017",
    bTaggers=["csvv2", "deepcsv", "deepjet", "cmva"], bTagWPs=["L", "M", "T", "shape"])


class NanoReadRochesterVar(NanoSystematicVarSpec):
    """
    Read precalculated Rochester correction variations

    :param systName: name of the systematic uncertainty, if variations should be enabled
    """
    def __init__(self, systName=None):
        super().__init__(nomName="nom", origName="orig",
                         exclVars=("orig",), isCalc=False)
        self.systName = systName

    def appliesTo(self, name):
        return name == "Muon"

    def getVarName(self, nm, collgrpname=None):
        if nm.endswith("_pt") and nm.startswith("corrected"):
            var = nm.split("_")[0][len("corrected"):]
            if var == "":
                return "pt", self._nomName
            elif self.systName is not None:
                return "pt", "".join(self.systName, var.lower())
        elif nm == "pt":
            return nm, "orig"


class CalcCollectionsGroups(NanoSystematicVarSpec):
    """
    :py:class:`~.NanoSystematicVarSpec` for on-the-fly corrections
        and systematic variation calculation
    """
    def __init__(self, nomName="nominal", origName="raw", exclVars=None, changes=None, **colsAndAttrs):
        super().__init__(
            nomName=nomName, origName=origName, isCalc=True,
            exclVars=(exclVars if exclVars is not None else (origName,)))
        self.colsAndAttrs = dict()
        for colgrp, attrs in colsAndAttrs.items():
            if isinstance(attrs, str):
                attrs = (attrs,)
            self.colsAndAttrs[colgrp] = attrs
        self.changes = (changes if changes is not None else dict())

    def appliesTo(self, name):
        return name in self.colsAndAttrs

    def changesTo(self, name):
        if name in self.changes:
            return self.changes[name]
        else:
            return super().changesTo(name)

    def getVarName(self, nm, collgrpname=None):
        if collgrpname in self.colsAndAttrs and nm in self.colsAndAttrs[collgrpname]:
            return nm, self.origName


nanoRochesterCalc = CalcCollectionsGroups(Muon="pt")
nanoJetMETCalc = CalcCollectionsGroups(Jet=("pt", "mass"), MET=("pt", "phi"))
nanoJetMETCalc_METFixEE2017 = CalcCollectionsGroups(Jet=("pt", "mass"), METFixEE2017=("pt", "phi"))
nanoFatJetCalc = CalcCollectionsGroups(FatJet=("pt", "mass", "msoftdrop"))


class NanoAODDescription:
    """ Description of the expected NanoAOD structure, and configuration for systematics and corrections

    Essentially, a collection of three containers:
       - :py:attr:`~.collections` a list of collections (by the name of the length leaf)
       - :py:attr:`~.groups` a list of non-collection groups (by prefix, e.g. ``HLT_``)
       - :py:attr:`~.systVariations` a list of :py:class:`~.NanoSystematicVarSpec` instances,
            to configure reading systematics variations from branches, or calculating them on the fly

    The recommended way to obtain a configuration is from the factory method :py:meth:`~.get`
    """
    ProductionVersions = dict()

    def __init__(self, groups=None, collections=None, systVariations=None):
        self.groups = list(groups) if groups is not None else []
        self.collections = list(collections) if collections is not None else []
        self.systVariations = list(systVariations) if systVariations is not None else []

    def clone(self, addGroups=None, removeGroups=None,
              addCollections=None, removeCollections=None, systVariations=None):
        groups = self.groups
        if removeGroups:
            groups = [grp for grp in groups if grp not in removeGroups]
        if addGroups:
            groups = groups + [grp for grp in addGroups if grp not in groups]
        collections = self.collections
        if removeCollections:
            collections = [grp for grp in collections if grp not in removeCollections]
        if addCollections:
            collections = collections + [grp for grp in addCollections if grp not in collections]
        return self.__class__(groups=groups, collections=collections, systVariations=systVariations)

    @staticmethod
    def get(tag, year="2016", isMC=False, addGroups=None, removeGroups=None,
            addCollections=None, removeCollections=None, systVariations=None):
        """ Create a suitable NanoAODDescription instance based on a production version

        A production version is defined by a tag, data-taking year, and a flag
        to distinguish data from simulation.
        Any number of groups or collections can be added or removed from this.
        The ``systVariations`` option

        :Example:

        >>> decorateNanoAOD(tree, NanoAODDescription.get(
        >>>     "v5", year="2016", isMC=True,
        >>>     systVariations=[nanoRochesterCalc, nanoJetMETCalc]))
        >>> decorateNanoAOD(tree, NanoAODDescription.get(
        >>>     "v5", year="2017", isMC=True,
        >>>     systVariations=[nanoPUWeightVar, nanoReadJetMETVar_METFixEE2017]))

        :param tag: production version (e.g. "v5")
        :param year: data-taking year
        :param isMC: simulation or not
        :param addGroups: (optional) list of groups of leaves to add
            (e.g. ``["L1_", "HLT_"]``, if not present)
        :param removeGroups: (optional) list of groups of leaves to remove
            (e.g. ``["L1_"]``, if skimmed)
        :param addCollections: (optional) list of containers to add
            (e.g. ``["nMyJets"]``)
        :param removeCollections: (optional) list of containers to remove
            (e.g. ``["nPhoton", "nTau"]``)
        :param systVariations: list of correction or systematic variation on-the-fly calculators
            or configurations to add (:py:class:`~.NanoSystematicVarSpec` instances)

        See also :py:func:`~.decorateNanoAOD`
        """
        return NanoAODDescription.ProductionVersions[(tag, year, isMC)].clone(
            addGroups=addGroups, removeGroups=removeGroups,
            addCollections=addCollections, removeCollections=removeCollections,
            systVariations=systVariations)


_ndpv = NanoAODDescription.ProductionVersions
_ndpv[("v5", "2016", False)] = NanoAODDescription(
    groups=["CaloMET_", "ChsMET_", "MET_", "PV_", "PuppiMET_", "RawMET_", "TkMET_", "Flag_", "HLT_", "L1_"],
    collections=["nElectron", "nFatJet", "nIsoTrack", "nJet", "nMuon", "nOtherPV", "nPhoton", "nSV",
                 "nSoftActivityJet", "nSubJet", "nTau", "nTrigObj", "nCorrT1METJet"])
_ndpv[("v5", "2016", True)] = _ndpv[("v5", "2016", False)].clone(
    addGroups=["GenMET_", "Generator_", "LHE_", "HTXS_"],
    addCollections=["nGenDressedLepton", "nGenJet", "nGenJetAK8", "nGenPart", "nGenVisTau", "nSubGenJetAK8"])
_ndpv[("v5", "2017", False)] = _ndpv[("v5", "2016", False)].clone(addGroups=["METFixEE2017_"])
_ndpv[("v5", "2017", True)] = _ndpv[("v5", "2016", True)].clone(addGroups=["METFixEE2017_"])
_ndpv[("v5", "2018", False)] = _ndpv[("v5", "2016", False)]
_ndpv[("v5", "2018", True)] = _ndpv[("v5", "2016", True)]
# v6 and v7 have the same structure as v5
for nano_v in ("v6", "v7"):
    for year in ("2016", "2017", "2018"):
        for isMC in (True, False):
            _ndpv[(nano_v, year, isMC)] = _ndpv[("v5", year, isMC)]

nanoGenDescription = NanoAODDescription(
    groups=["Generator_", "MET_", "GenMET_", "LHE_", "HTXS_", "GenVtx_"],
    collections=["nGenPart", "nGenJet", "nGenJetAK8", "nGenVisTau",
                 "nGenDressedLepton", "nGenIsolatedPhoton", "nLHEPart"]
)


def decorateNanoAOD(aTree, description=None):
    """ Decorate a CMS NanoAOD Events tree

    Variation branches following the NanoAODTools conventions (e.g. Jet_pt_nom)
    are automatically used (but calculators for the same collection take
    precendence, if requested).

    :param aTree: TTree to decorate
    :param description: description of the tree format, and configuration for reading
        or calculating systematic variations and corrections,
        a :py:class:`~.NanoAODDescription` instance
        (see also :py:meth:`.NanoAODDescription.get`)
    """
    if description is None:
        raise ValueError(
            'A description is needed to correctly decorate a NanoAOD '
            '(but it may be as simple as ``description=NanoAODDescription.get("v5")``)')

    class GetItemRefCollection:
        def __init__(self, name):
            self.name = name
            self._parent = None

        def __call__(self, me):
            return getattr(self._parent, self.name)

    class GetItemRefCollection_toVar:
        def __init__(self, name):
            self.name = name
            self._parent = None

        def __call__(self, me):
            return getattr(self._parent, self.name).orig

    def addP4ToObj(prefix, lvNms):
        return funProxy(partial((
            lambda getEta, getM, inst: top.Construct(
                "ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >",
                (inst.pt, getEta(inst), inst.phi, getM(inst))).result),
            ((lambda inst: inst.eta) if f"{prefix}eta" in lvNms else (lambda inst: 0.)),
            ((lambda inst: inst.mass) if f"{prefix}mass" in lvNms else (lambda inst: 0.))))

    allTreeLeafs = {lv.GetName(): lv for lv in allLeafs(aTree)}
    tree_dict = {"__doc__": f"{aTree.GetName()} tree proxy class"}
    from .root import gbl
    for lvNm, lv in allTreeLeafs.items():
        lvOp = None
        if isinstance(lv, gbl.TBranchElement):  # only RVec (from Snapshot), guess length from name
            if "_" in lvNm:
                guess = f'n{lvNm.split("_")[0]}'
                if guess in allTreeLeafs:
                    tpNm = lv.GetTypeName()
                    m = tpx.vecPat.match(tpNm)
                    if m:  # read as RVec
                        tpNm = f"ROOT::VecOps::RVec<{m.group('item')}>"
                    lvOp = top.GetColumn(tpNm, lvNm)
                else:
                    raise RuntimeError(f"Could not guess the size branch for {lvNm}")
            else:
                raise RuntimeError(f"Not supported")
        else:  # all branches in original NanoAOD
            if not lv.GetLeafCount():  # not an array
                lvOp = top.GetColumn(lv.GetTypeName(), lvNm)
            else:  # count leaf -> array
                cntName = lv.GetLeafCount().GetName()
                lvOp = top.GetArrayColumn(
                    lv.GetTypeName(), lvNm,
                    top.GetColumn(allTreeLeafs[cntName].GetTypeName(), cntName))
        tree_dict[lvNm] = proxy(lvOp)
    tree_children = list()

    def setTreeAtt(name, proxy, setParent=True):
        tree_dict[name] = proxy
        if setParent:
            tree_children.append(proxy)

    # variables with variations
    for vari in description.systVariations:
        toRem = []
        brMap = {}
        attNm = None
        for nm, nmAtt in tree_dict.items():
            if vari.appliesTo(nm):  # only for single-variable variations
                attNm, varNm = vari.getVarName(nm)
                if varNm in brMap:
                    raise RuntimeError(f"Variation {varNm} deduced for {nm}, but already present")
                brMap[varNm] = nmAtt.op
                toRem.append(nm)
        if brMap and (len(brMap) > 1 or vari.isCalc):
            for nm in toRem:
                del tree_dict[nm]
            logger.debug(
                f"Detected systematic variations for variable {attNm} "
                f"(variations: {list(brMap.keys())!r}")
            brMap["nomWithSyst"] = top.SystAltOp(
                brMap[vari.nomName(attNm)], dict(brMap),
                valid=tuple(var for var in brMap.keys() if var != vari.nomName(attNm))
            )
            varsProxy = tpx.AltLeafVariations(None, brMap)
            setTreeAtt(f"_{attNm}", varsProxy)
            setTreeAtt(attNm, varsProxy["nomWithSyst"], False)

    # non-collection branches to group
    grp_found = []
    for prefix in description.groups:
        if not any(lvNm.startswith(prefix) for lvNm in allTreeLeafs):
            logger.warning(f"No branch name starting with {prefix} in the tree - skipping group")
        else:
            grp_found.append(prefix)
    for prefix in grp_found:
        grpNm = prefix.rstrip("_")
        grp_dict = {"__doc__": f"{grpNm} leaf group proxy class"}
        grp_lvNms = {lvNm for lvNm in allTreeLeafs.keys() if lvNm.startswith(prefix)}
        grp_dict.update({
            lvNm[len(prefix):]: proxy(top.GetColumn(allTreeLeafs[lvNm].GetTypeName(), lvNm))
            for lvNm in grp_lvNms})
        if f"{prefix}pt" in grp_lvNms and f"{prefix}phi" in grp_lvNms:
            grp_dict["p4"] = addP4ToObj(prefix, grp_lvNms)
        grpcls = type(f"{grpNm}LeafGroupProxy", (tpx.LeafGroupProxy,), grp_dict)
        for lvNm in grp_lvNms:
            del tree_dict[lvNm]
        # default group proxy, replaced below if needed
        grp_proxy = grpcls(grpNm, None)
        setTreeAtt(grpNm, grp_proxy)
        for vari in description.systVariations:
            if vari.appliesTo(grpNm):
                for newNm in vari.changesTo(grpNm):
                    grpcls_alt, brMapMap = _makeAltClassAndMaps(
                        grpNm, grp_dict, vari, attCls=altProxy,
                        altBases=(tpx.AltLeafGroupProxy,))
                    withSyst = "nomWithSyst"
                    if vari.isCalc:
                        varsProxy = tpx.CalcLeafGroupVariations(
                            None, grp_proxy, brMapMap, grpcls_alt, withSystName=withSyst)
                    else:
                        varsProxy = tpx.AltLeafGroupVariations(None, grp_proxy, brMapMap, grpcls_alt)
                        allVars = list(set(chain.from_iterable(op.variations
                                           for op in varsProxy[withSyst].brMap.values())))
                        if allVars:
                            logger.debug(f"{newNm} variations read from branches: {allVars}")
                    setTreeAtt(f"_{newNm}", varsProxy)
                    setTreeAtt(newNm, varsProxy[withSyst])

    class NanoAODGenRanges:
        @property
        def parent(self):
            return self.genPartMother

        @property
        def ancestors(self):
            return tpx.SelectionProxy(
                self._parent,
                top.Construct(
                    "rdfhelpers::gen::ancestors<-1,ROOT::VecOps::RVec<Int_t>>",
                    (tf.static_cast("int", self.genPartMother._idx), self.genPartMother._idx.arg)),
                type(self))

    # SOA, nanoAOD style (LeafCount, shared)
    cnt_found = []
    for sizeNm in description.collections:
        if sizeNm not in allTreeLeafs:
            logger.warning(f"{sizeNm} is not a branch in the tree - skipping collection")
        else:
            cnt_found.append(sizeNm)

    for sizeNm in cnt_found:
        grpNm = sizeNm[1:]
        prefix = f"{grpNm}_"
        itm_dict = {"__doc__": f"{grpNm} proxy class"}
        itm_lvs = {lvNm for lvNm, lv in allTreeLeafs.items()
                   if lvNm.startswith(prefix) and (isinstance(lv, gbl.TBranchElement)
                                                   or lv.GetLeafCount().GetName() == sizeNm)}
        sizeOp = top.GetColumn(allTreeLeafs[sizeNm].GetTypeName(), sizeNm)
        for lvNm in itm_lvs:
            lvNm_short = lvNm[len(prefix):]
            if isinstance(allTreeLeafs[lvNm], gbl.TBranchElement):
                col = tree_dict[lvNm].op.result
            else:
                col = top.GetArrayColumn(allTreeLeafs[lvNm].GetTypeName(), lvNm, sizeOp).result
            if "Idx" not in lvNm:
                itm_dict[lvNm_short] = itemProxy(col)
            else:
                coll, i = lvNm_short.split("Idx")
                collPrefix = coll[0].capitalize() + coll[1:]
                collGetter = (
                    GetItemRefCollection_toVar(f"_{collPrefix}")
                    if any(vari.appliesTo(collPrefix) for vari in description.systVariations)
                    else GetItemRefCollection(collPrefix))
                tree_children.append(collGetter)
                itm_dict["".join((coll, i))] = itemRefProxy(col, collGetter)
        # create p4 branches (naive, but will be reused for variation case)
        if f"{prefix}pt" in itm_lvs and f"{prefix}phi" in itm_lvs:
            itm_dict["p4"] = addP4ToObj(prefix, itm_lvs)
        itm_bases = [tpx.ContainerGroupItemProxy]
        if sizeNm == "nGenPart":
            itm_bases.append(NanoAODGenRanges)
        itmcls = type(f"{grpNm}GroupItemProxy", tuple(itm_bases), itm_dict)
        # default collection proxy, replaced below if needed
        coll_orig = tpx.ContainerGroupProxy(prefix, None, sizeOp, itmcls)
        setTreeAtt(grpNm, coll_orig)
        # insert variations using kinematic calculator, from branches, or not
        for vari in description.systVariations:
            if vari.appliesTo(grpNm):
                altItemType, brMapMap = _makeAltClassAndMaps(
                    grpNm, itm_dict, vari, getCol=(lambda att: att.op),
                    attCls=altItemProxy, altBases=(tpx.ContainerGroupItemProxy,))
                withSyst = "nomWithSyst"
                for newNm in vari.changesTo(grpNm):
                    if vari.isCalc:
                        varsProxy = tpx.CalcCollectionVariations(
                            None, coll_orig, brMapMap, altItemType=altItemType, withSystName=withSyst)
                    else:
                        varsProxy = tpx.AltCollectionVariations(
                            None, coll_orig, brMapMap, altItemType=altItemType)
                        allVars = list(set(chain.from_iterable(
                            op.variations for op in varsProxy[withSyst].brMap.values())))
                        if allVars:
                            logger.debug(f"{newNm} variations read from branches: {allVars}")
                    setTreeAtt(f"_{newNm}", varsProxy)
                    setTreeAtt(newNm, varsProxy[withSyst])

        for lvNm in itm_lvs:
            del tree_dict[lvNm]
        del tree_dict[sizeNm]  # go through tf.rng_len

    TreeProxy = type(f"{aTree.GetName()}Proxy", (tpx.TreeBaseProxy,), tree_dict)
    treeProxy = TreeProxy(aTree)
    for pc in tree_children:
        pc._parent = treeProxy

    return treeProxy


def decorateCMSPhase2SimTree(aTree, isMC=True):
    """ Decorate a flat tree as used for CMS Phase2 physics studies """

    class Phase2GenRanges:
        @property
        def parent(self):
            return self._parent[self.m1]

        @property
        def ancestors(self):
            return tpx.SelectionProxy(
                self._parent,
                top.Construct(
                    "rdfhelpers::gen::ancestors<-99>",
                    (tf.static_cast("int", self.parent._idx), self.parent._idx.arg)),
                type(self))

        @property
        def children(self):
            return self._parent[self.d1:tf.switch(self.d2 > 0, self.d2 + 1, self.d1)]

        @property
        def descendants(self):
            return tpx.SelectionProxy(
                self._parent,
                top.Construct(
                    "rdfhelpers::gen::descendants_firstlast<-99,ROOT::VecOps::RVec<Int_t>>",
                    (tf.static_cast("int", self._idx), self.d1._parent.arg, self.d2._parent.arg)),
                type(self))

    allTreeLeafs = {lv.GetName(): lv for lv in allLeafs(aTree)}
    tree_dict = {"__doc__": f"{aTree.GetName()} tree proxy class"}
    # fill all, take some out later
    tree_dict.update({lvNm: proxy(top.GetColumn(lv.GetTypeName(), lvNm))
                      for lvNm, lv in allTreeLeafs.items()})
    tree_children = []
    cnt_lvs = {lv.GetLeafCount().GetName()
               for lv in allTreeLeafs.values() if lv.GetLeafCount()}
    for sizeNm in cnt_lvs:
        grpNm = sizeNm.split("_")[0]
        prefix = f"{grpNm}_"
        itm_dict = {"__doc__": f"{grpNm} proxy class"}
        itm_lvs = {lvNm for lvNm, lv in allTreeLeafs.items()
                   if lvNm.startswith(prefix) and lvNm != sizeNm
                   and lv.GetLeafCount().GetName() == sizeNm}
        sizeOp = top.GetColumn(allTreeLeafs[sizeNm].GetTypeName(), sizeNm)
        if allTreeLeafs[sizeNm].GetTypeName() != top.SizeType:
            sizeOp = top.adaptArg(tf.static_cast(top.SizeType, sizeOp))
        for lvNm in itm_lvs:
            lvNm_short = lvNm[len(prefix):]
            col = top.GetArrayColumn(allTreeLeafs[lvNm].GetTypeName(), lvNm, sizeOp).result
            itm_dict[lvNm_short] = itemProxy(col)
        # create p4 branches
        p4AttNames = ("pt", "eta", "phi", "mass")
        if all(("".join((prefix, att)) in itm_lvs) for att in p4AttNames):
            itm_dict["p4"] = funProxy(lambda inst: top.Construct(
                "ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >",
                (inst.pt, inst.eta, inst.phi, inst.mass)).result)
            # mother/daughter references
        itm_bases = [tpx.ContainerGroupItemProxy]
        if grpNm == "genpart":
            itm_bases.append(Phase2GenRanges)
        itmcls = type(f"{grpNm.capitalize()}GroupItemProxy", tuple(itm_bases), itm_dict)
        coll = tpx.ContainerGroupProxy(prefix, None, sizeOp, itmcls)
        tree_dict[grpNm] = coll
        tree_children.append(coll)

        for lvNm in itm_lvs:
            del tree_dict[lvNm]
        del tree_dict[sizeNm]  # go through tf.rng_len

    TreeProxy = type(f"{aTree.GetName().capitalize()}Proxy", (tpx.TreeBaseProxy,), tree_dict)
    treeProxy = TreeProxy(aTree)

    for pc in tree_children:
        pc._parent = treeProxy

    return treeProxy
