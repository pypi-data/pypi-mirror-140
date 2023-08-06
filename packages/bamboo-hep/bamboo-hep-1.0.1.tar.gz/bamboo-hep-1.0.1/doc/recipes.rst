Recipes for common tasks
========================

.. _recipescalefactors:

Using scalefactors
------------------

Scalefactors |---| CMS jargon for efficiency corrections for MC, typically
binned in lepton or jet kinematic variables |---| can be generalized to
functions that take some properties of a physics object and return a single
floating-point number.
The :py:mod:`bamboo.scalefactors` module provides support for constructing
such callable objects from two different JSON formats, the CMS correctionlib_
format, and the one used in the `CP3-llbb framework`_, and the CMS BTV CSV
format.

CMS correctionlib JSON format
'''''''''''''''''''''''''''''

The :py:meth:`bamboo.scalefactors.get_correction` method loads a ``Correction``
from the ``CorrectionSet`` stored in a JSON file, and constructs a helper object
to use it in bamboo.
Since corrections are usually parameterised as function of e.g. kineamtic
properties of a reconstructed object, callables can be passed as parameters,
and the helper object called with a reconstructed object, e.g.

.. code-block:: python

 from bamboo.scalefactors import get_correction
 sf = get_correction(..., params={"pt": lambda obj : obj.pt, ...})
 mySel = noSel.refine(..., weight=sf(el))

Many of the arguments to :py:meth:`bamboo.scalefactors.get_correction` are
related to automatic systematic uncertainties: the name of a category axis in
the ``Correction``, the mapping between its categories and systematic variations
in bamboo, and the name of the nominal category |---| more details and
a complete example can be found in the reference documentation.
Please note that this needs the correctionlib package to be installed, see
:ref:`the installation guide<installbase>` for more details.

CP3-llbb JSON format
''''''''''''''''''''

The :py:mod:`bamboo.scalefactors` module provides support for constructing
such callable objects from the JSON format used in the `CP3-llbb framework`_,
see some examples
`here <https://github.com/cp3-llbb/Framework/tree/CMSSW_8_0_6p/data/ScaleFactors>`_
(these JSON files are produced from the txt or ROOT files provided by the POGs
using simple python
`scripts <https://github.com/cp3-llbb/Framework/tree/CMSSW_8_0_6p/scripts>`_).
Like their inputs, the JSON files contain the nominal scale factor as well as
its up and down systematic variations, so the
:py:class:`~bamboo.scalefactors.ScaleFactor` behaves as a callable that takes
a physics object and an optional ``variation`` keyword argument (technically,
it wraps a C++ object that gets the correct value from the JSON file).

The :py:meth:`~bamboo.scalefactors.get_scalefactor` method constructs such
objects from a nested dictionary:
the first key is a tag (as an example: "electron_2015_76", for electrons in
2015 data, analysed with a ``CMSSW_7_6_X`` release) and the second key is an
identifier of the selection they correspond to (e.g. ``id_Loose``).
The value inside this dictionary can be either a single path to a JSON file,
or a list of ``(periods, path)`` pairs, where ``periods`` is a list of run periods, in case scalefactors for different
running periods need to be combined (the ``periods`` keyword argument to
:py:meth:`~bamboo.scalefactors.get_scalefactor` can be used to select only
a certain set of these periods).
The combination is done by either weighting or randomly sampling from the
different periods, according to the fraction of the integrated luminosity in
each (by passing ``combine="weight"`` or ``combine="sample"``, respectively).
Jet flavour tagging and dilepton (e.g. trigger) scalefactors can also be
specified by passing tuples of the light, c-jet and b-jet scalefactor paths,
and tuples of first-if-leading, first-if-subleading, second-if-leading,
and second-if-subleading (to be reviewed for NanoAOD) scalefactor paths,
respectively, instead of a single path.

Histogram variations representing the shape systematic uncertainty due to an
uncertainty on the scalefactor values can be automatically produced by passing
a name to the ``systName`` keyword argument of the
:py:meth:`~bamboo.scalefactors.get_scalefactor` method.

As an example, some basic lepton ID and jet tagging scalefactors could be
included in an analysis on NanoAOD by defining

.. code-block:: python

 import bamboo.scalefactors
 from itertools import chain
 import os.path

 # scalefactor JSON files are in ScaleFactors/<era>/ alongside the module
 def localize_myanalysis(aPath, era="2016legacy"):
     return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ScaleFactors", era, aPath)

 # nested dictionary with path names of scalefactor JSON files
 # { tag : { selection : absole-json-path } }
 myScalefactors = {
     "electron_2016_94" : {
         "id_Loose"  : localize_myanalysis("Electron_EGamma_SF2D_Loose.json")
         "id_Medium" : localize_myanalysis("Electron_EGamma_SF2D_Medium.json")
         "id_Tight"  : localize_myanalysis("Electron_EGamma_SF2D_Tight.json")
     },
     "btag_2016_94" : dict((k, (tuple(localize_myanalysis(fv) for fv in v))) for k,v in dict(
         ( "{algo}_{wp}".format(algo=algo, wp=wp),
           tuple("BTagging_{wp}_{flav}_{calib}_{algo}.json".format(wp=wp, flav=flav, calib=calib, algo=algo)
               for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))
         ) for wp in ("loose", "medium", "tight") for algo in ("DeepCSV", "DeepJet") ).items())
     }

 # fill in some defaults: myScalefactors and bamboo.scalefactors.binningVariables_nano
 def get_scalefactor(objType, key, periods=None, combine=None, additionalVariables=None, systName=None):
     return bamboo.scalefactors.get_scalefactor(objType, key, periods=periods, combine=combine,
         additionalVariables=(additionalVariables if additionalVariables else dict()),
         sfLib=myScalefactors, paramDefs=bamboo.scalefactors.binningVariables_nano, systName=systName)

and adding the weights to the appropriate :py:class:`~bamboo.plots.Selection`
instances with

.. code-block:: python

 electrons = op.select(t.Electron, lambda ele : op.AND(ele.cutBased >= 2, ele.p4.Pt() > 20., op.abs(ele.p4.Eta()) < 2.5))
 elLooseIDSF = get_scalefactor("lepton", ("electron_2016_94", "id_Loose"), systName="elID")
 hasTwoEl = noSel.refine("hasTwoEl", cut=[ op.rng_len(electrons) > 1 ],
               weight=[ elLooseIDSF(electrons[0]), elLooseIDSF(electrons[1]) ])

 jets = op.select(t.Jet, lambda j : j.p4.Pt() > 30.)
 bJets = op.select(jets, lambda j : j.btagDeepFlavB > 0.2217) ## DeepFlavour loose b-tag working point
 deepFlavB_discriVar = { "BTagDiscri": lambda j : j.btagDeepFlavB }
 deepBLooseSF = get_scalefactor("jet", ("btag_2016_94", "DeepJet_loose"), additionalVariables=deepFlavB_discriVar, systName="bTag")
 hasTwoElTwoB = hasTwoEl.refine("hasTwoElTwoB", cut=[ op.rng_len(bJets) > 1 ],
                  weight=[ deepBLooseSF(bJets[0]), deepBLooseSF(bJets[1]) ])

Note that the user is responsible for making sure that the weights are only applied to simulated events, and not to real data!

CMS BTV CSV format
''''''''''''''''''

The :py:class:`bamboo.scalefactors.BtagSF` class wraps the
``BTagCalibrationReader`` provided by the BTV POG to read the custom CSV
format for b-tagging scalefactors (more details usage instructions can be
found in the reference documentation).
Please note that this will only read the scalefactors, which for most
`methods for applying b-tagging scalefactors <https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagSFMethods>`_
need to be combined with efficiency and mistag probability maps measured
in simulation in the analysis phase space.

.. _recipepureweighting:

Pileup reweighting
------------------

Pileup reweighting to make the pileup distribution in simulation match the one
in data is very similar to applying a scalefactor, except that the efficiency
correction is for the whole event or per-object |---| so the same code can be
used.
The ``makePUReWeightJSON`` script included in bamboo can be used to make
a JSON file with weights out of a data pileup profile obtained by running
``pileupcalc.py``
(inside CMSSW, see the `pileupcalc documentation`_ for details), e.g. with
something like

.. code-block:: bash

   pileupCalc.py -i ~/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt --inputLumiJSON /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt --calcMode true --minBiasXsec 69200 --maxPileupBin 80 --numPileupBins 80 ./2016PUHist_nominal.root

and a MC pileup profile.
Data pileup distributions corresponding to the golden JSON files for Run 2 are
provided by the luminosity POG, see
`this hypernews annoncement <https://hypernews.cern.ch/HyperNews/CMS/get/physics-validation/3374/2.html>`_.
The MC pileup profiles for used official CMSSW productions are
currently hardcoded inside the ``makePUReWeightJSON``, and can be specified
by their tag or name in that list; the available tags can be listed by
specifying the ``--listmcprofiles`` option. The full command then becomes
something like

.. code-block:: bash

   makePUReWeightJSON --mcprofile "Moriond17_25ns" --nominal=2016PUHist.root --up=2016PUHist_up.root --down=2016PUHist_down.root --makePlot

To include the weight when filling plots, it is sufficient to add the weight to
a selection (usually one of the topmost in the analysis, e.g. in the
``prepareTree`` method of the analysis module).
The :py:func:`bamboo.analysisutils.makePileupWeight` method can be used to build
an expression for the weight, starting from the path of the JSON file with
weights from above, and an expression for the true number of interactions in the
event (mean of the Poissonian used), e.g. ``tree.Pileup_nTrueInt`` for NanoAOD.


.. _recipetaucleaning:

Cleaning collections
--------------------

The CMS reconstruction sometimes ends up double-counting some objects.
This can be because of the different quality criteria used to identify each
object or because of the different performance and inner working of
the reconstruction algorithms.
Tau reconstruction for example operates on clusters that are usually
reconstructed as jets, and on top of that it can easily pick up even isolated
muons or electrons as taus (i.e. as clusters of energy with one, two, or three
tracks).

It is oftentimes necessary therefore to clean a collection of objects by
excluding any object that is spatially in the sample place of another object
whose reconstruction we trust more.

We trust more muon and electron reconstrution than tau reconstruction,
after all the quality cuts (ID efficiencies for muons and electrons are around
99.X%, whereas tau ID efficiencies are of the order of 70%.
Misidentification rates are similarly quite different), and therefore we exclude
from the tau collection any tau that happens to include within its
reconstruction cone a muon or an electron.

Bamboo provides a handy syntax for that, resulting in something like

.. code-block:: python

   cleanedTaus = op.select(taus, lambda it : op.AND(
         op.NOT(op.rng_any(electrons, lambda ie : op.deltaR(it.p4, ie.p4) < 0.3 )),
         op.NOT(op.rng_any(muons, lambda im : op.deltaR(it.p4, im.p4) < 0.3 ))
         ))

In this example, we assume that the collections ``taus``, ``electrons``, and
``muons``, have already been defined via
``taus = op.select(t.Tau, lambda tau : ...)``, and we move on to use the method
``op.rng_any()`` to filter all taus that are within a cone of a given size
(0.3, in the example) from any selected electron or muon.


.. _recipejetsystematics:

Jet and MET systematics
-----------------------

For propagating uncertainties related to the jet energy calibration, and the
difference in jet energy resolution between data and simulation, each jet in
the reconstructed jet collection should be modified, the collection sorted,
and any derived quantity re-evaluated.

How to do this depends on the input trees: in production NanoAOD the modified
momenta need to be calculated using the jet energy correction parameters; it is
also possible to add them when post-processing with the
`jetmetUncertainties module`_ of the NanoAODTools_ package.
In the latter case the NanoAOD decoration method will pick up the modified
branches if an appropriate
:py:class:`~bamboo.treececorators.NanoSystematicVarSpec` entry (e.g.
:py:data:`~bamboo.treedecorators.nanoReadJetMETVar` or
:py:data:`~bamboo.treedecorators.nanoReadJetMETVar_METFixEE2017`) is added to
the :py:attr:`~.systVariations` attribute of the
:py:class:`~bamboo.treedecorators.NanoAODDescription` that is passed to the
:py:meth:`~bamboo.analysismodules.NanoAODModule.prepareTree` (or
:py:func:`~bamboo.treedecorators.decorateNanoAOD`) method.

To calculate the variations on the fly, two things are needed: when decorating
the tree, some redirections should be set up to pick up the variations from a
calculator module, and then this module needs to be configured with the correct
JEC and resolution parameters.
The first step can be done by adding
:py:data:`~bamboo.treedecorators.nanoJetMETCalc` (or
:py:data:`~bamboo.treedecorators.nanoJetMETCalc_METFixEE2017`) to the
:py:attr:`~.systVariations` attribute of the
:py:class:`~bamboo.treedecorators.NanoAODDescription` that is passed to the
:py:meth:`~bamboo.analysismodules.NanoAODModule.prepareTree` method (which will
pass this to the :py:func:`~bamboo.treedecorators.decorateNanoAOD` method);
these will also make sure that all these variations are propagated to the
missing transverse momentum.
Next, a calculator must be added and configured.
This can be done with the :py:meth:`bamboo.analysisutils.configureJets` and
:py:meth:`bamboo.analysisutils.configureType1MET` methods, which provide a
convenient way to correct the jet resolution in MC, apply a different JEC, and
add variations due to different sources of uncertainty in the jet energy scale,
for the jet collection and MET, respectively (the arguments should be the same
in most cases).

.. note:: The jet and MET calculators were moved to a separate package.
   Since these calculators are C++ classes with an RDF-friendly interface and
   minimal dependencies, they are not only useful from bamboo, but also from
   other (RDF-based or similar) frameworks.
   Therefore they were moved to a separate repository
   `cp3-cms/CMSJMECalculators <https://gitlab.cern.ch/cp3-cms/CMSJMECalculators.git>`_.
   They can be installed with e.g.
   ``pip install git+https://gitlab.cern.ch/cp3-cms/CMSJMECalculators.git``.

As an example, the relevant code of a NanoAOD analysis module could
look like this to apply a newer JEC to 2016 data and perform smearing, add
uncertainties to 2016 MC, and the same for the MET:

.. code-block:: python

   class MyAnalysisModule(NanoAODHistoModule):
       def prepareTree(self, tree, sample=None, sampleCfg=None):
           tree,noSel,be,lumiArgs = super(MyAnalysisModule, self).prepareTree(tree, sample=sample, sampleCfg=sampleCfg
             , NanoAODDescription.get("v5", year="2016", isMC=self.isMC(sample), systVariations=[nanoJetMETCalc]))
           from bamboo.analysisutils import configureJets, configureType1MET
           isNotWorker = (self.args.distributed != "worker")
           era = sampleCfg["era"]
           if era == "2016":
               if self.isMC(sample): # can be inferred from sample name
                   configureJets(tree._Jet, "AK4PFchs",
                       jec="Summer16_07Aug2017_V20_MC",
                       smear="Summer16_25nsV1_MC",
                       jesUncertaintySources=["Total"],
                       mayWriteCache=isNotWorker,
                       isMC=self.isMC(sample), backend=be)
                   configureType1MET(tree._MET,
                       jec="Summer16_07Aug2017_V20_MC",
                       smear="Summer16_25nsV1_MC",
                       jesUncertaintySources=["Total"],
                       mayWriteCache=isNotWorker,
                       isMC=self.isMC(sample), backend=be)
               else:
                   if "2016G" in sample or "2016H" in sample:
                       configureJets(tree._Jet, "AK4PFchs",
                           jec="Summer16_07Aug2017GH_V11_DATA",
                           mayWriteCache=isNotWorker,
                           isMC=self.isMC(sample), backend=be)
                       configureType1MET(tree._MET,
                           jec="Summer16_07Aug2017GH_V11_DATA",
                           mayWriteCache=isNotWorker,
                           isMC=self.isMC(sample), backend=be)
                   elif ...: ## other 2016 periods
                       pass

           return tree,noSel,be,lumiArgs

Both with variations read from a postprocessed NanoAOD and calculated on the
fly, the different jet collections are available from ``t._Jet``, e.g.
``t._Jet["nom"]`` (postprocessed) or ``t._Jet["nominal"]`` (calculated),
``t._Jet["jerup"]``, ``t._Jet["jerdown"]``, ``t._Jet["jesTotalUp"]``,
``t._Jet["jesTotalDown"]`` etc. depending on the configured variations
(when accessing these directly, ``t._Jet[variation][j.idx]`` should be used
to retrieve the entry corresponding to a specific jet ``j``, if the latter is
obtained from a selected and/or sorted version of the original collection |---|
``object.idx`` is always the index in the collection as found in the tree).

``t.Jet`` will be changed for one of the above for each systematic variation,
if it affects a plot, in case automatically producing the systematic variations
is enabled (the collections from ``t._Jet`` will not be changed).
The automatic calculation of systematic variations can be disabled globally
or on a per-selection basis (see above), and for on the fly calculation also by
passing ``enableSystematics=[]`` to
:py:meth:`bamboo.analysisutils.configureJets`).
The jet collection as stored on the input file, finally, can be retrieved as
``t._Jet.orig``.

.. important:: Sorting the jets
   No sorting is done as part of the above procedure, so if relevant this
   should be added by the user (e.g. using
   ``jets = op.sort(t.Jet, lambda j : -j.pt)`` for sorting by decreasing
   transverse momentum).
   In a previous version of the code this was included, but since some selection
   is usually applied on the jets anyway, it is simpler (and more efficient) to
   perform the sorting then.

.. important:: Bamboo_ runs outside CMSSW and has no access to the conditions
   database, so it fetches the necessary txt files from the repositories
   on github (they are quite large, so this is more efficient than storing
   a clone locally). They can be automatically updated if the upstream
   repository changes; the ``mayWriteCache`` argument to
   :py:meth:`bamboo.analysisutils.configureJets` (see the example above)
   helps ensure that only one process write to the cache at a time.
   In practice, updating the local cache when the corrections have changed
   can be done by running an analysis module once in non-distributed mode
   using the `--onlyprepare --maxFiles 1` arguments.
   In case of doubt one can use the ``checkCMSJMEDatabaseCaches`` script
   to update or check the cache interactively and, as a last resort, remove
   the cache directories and status files from ``~/.bamboo/cache``:
   they will be recreated automatically at the next use.

.. note:: Isn't it slow to calculate jet corrections on the fly?
   It does take a bit of time, but the calculation is done in one C++ module,
   which should not be executed more than once per event (see the explanation
   of the :py:meth:`bamboo.analysisutils.forceDefine` method in the
   :ref:`section above<ugcutordering>`).
   In most realistic cases, the bottleneck is in reading and decompressing the
   input files, so the performance hit from the jet corrections should usually
   be acceptable.


.. _reciperochester:

Rochester correction for muons
------------------------------

The so-called
`Rochester correction <https://twiki.cern.ch/twiki/bin/viewauth/CMS/RochcorMuon>`_
removes a bias in the muon momentum, and improves the agreement between data
and simulation in the description of the Z boson peak.
As for the jet correction and variations described in the previous section,
this can either be done during postprocessing, with the
`muonScaleResProducer module`_ of the NanoAODTools_ package, or on the fly.
To adjust the decorators, a suitable
:py:class:`~bamboo.treedecorators.NanoSystematicVarSpec` instance to read the
corrected values, or :py:data:`~bamboo.treedecorators.nanoRochesterCalc` to use
the calculated values, should be added to the :py:attr:`~.systVariations`
attribute of the :py:class:`~bamboo.treedecorators.NanoAODDescription` that is
passed to the :py:meth:`~bamboo.analysismodules.NanoAODModule.prepareTree` (or
:py:func:`~bamboo.treedecorators.decorateNanoAOD`) method.

The on the fly calculator should be added and configured with the
:py:meth:`bamboo.analysisutils.configureRochesterCorrection` method,
as in the example below.
``tree._Muon`` keeps track of everything related to the calculator; the
uncorrected muon collection can be found in ``tree._Muon.orig``, and the
corrected muons are in ``tree.Muon``.

.. code-block:: python

   class MyAnalysisModule(NanoAODHistoModule):
       def prepareTree(self, tree, sample=None, sampleCfg=None):
           tree,noSel,be,lumiArgs = NanoAODHistoModule.prepareTree(self, tree, sample=sample, sampleCfg=sampleCfg, calcToAdd=["nMuon"])
           from bamboo.analysisutils import configureRochesterCorrection
           era = sampleCfg["era"]
           if era == "2016":
               configureRochesterCorrection(tree._Muon, "RoccoR2016.txt", isMC=self.isMC(sample), backend=be)
       return tree,noSel,be,lumiArgs

.. _recipecorrelatingsystematics:

Correlating systematic variations
---------------------------------

To understand how systematic variations are implemented in bamboo, and how to
take advantage of that to correlate e.g. a b-tagging scalefactor variation with
a jet and MET kinematic variation, it is useful to remember that your code
creates :ref:`expressions<ugexpressions>` that are converted to C++ code, and
imagine a variable with a systematic uncertainty as a single nominal value with
a dictionary of alternative values: the keys of this dictionary are the
variation names, e.g. ``elIDup`` or ``jerdown``.
This is also how they are represented in the expression objects tree.
When creating a plot or selection, the variable(s), weight(s), and cut(s) are
scanned for such nodes with systematic variations, and additional RDataFrame
nodes are created for all the variations.

There are two interesting consequences of the this dictionary with variations:
all variations are equal, i.e. there is no concept of "uncertainty X with
e.g. up and down variations" |---| although this is very common in practice, and
trivial to reconstruct from the dictionary where needed |---| and all expression
nodes with the same variation change together.
The latter is necessary in many cases, e.g. when passing the MET and some jet
pt's to a multivariate classifier, both should pass the ``jerdown`` variation
to get the corresponding variation of the classifier output.
It also provides a very transparent way to correlate variations: if the name is
the same, they will be simultaneously varied |---| so it is enough that
a b-tagging scalefactor variation is called ``jesAbsup`` to be varied together
with that variation of the jet pt's; turning that around: to be varied
independently, the names must be made different (this is why ``up`` and ``down``
by themselves as variation names lead to an error message being printed).

.. _recipesplitsamplesubcomp:

Splitting a sample into sub-components
--------------------------------------

It is frequently necessary to split a single Monte-Carlo sample into different processes, depending on generator-level information, or simply to add some cuts at generator level (e.g. to stitch binned samples together).
This can be achieved by duplicating that sample in the analysis configuration file for as many splits as are needed, and putting (any) additional information into that sample's entry, e.g. as:

.. code-block:: yaml

     ttbb:
       db: das:/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM
       era: 2018
       group: ttbb
       subprocess: ttbb
       cross-section: 366.
       generated-events: genEventSumw

     ttjj:
       db: das:/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM
       era: 2018
       group: ttjj
       subprocess: ttjj
       cross-section: 366.
       generated-events: genEventSumw

That information can then be retrieved in the analysis module through the ``sampleCfg`` keyword argument, to add additional cuts to the selection when preparing the tree:

.. code-block:: python

   def prepareTree(self, tree, sample=None, sampleCfg=None):
       tree,noSel,be,lumiArgs = super(MyAnalysisModule, self).prepareTree(tree, sample=sample, sampleCfg=sampleCfg)

       if "subprocess" in sampleCfg:
            subProc = sampleCfg["subprocess"]
            if subProc == "ttbb":
                noSel = noSel.refine(subProc, cut=(tree.genTtbarId % 100) >= 52)
            elif subProc == "ttjj":
                noSel = noSel.refine(subProc, cut=(tree.genTtbarId % 100) < 41)

       return tree,noSel,be,lumiArgs


.. _recipecmdlinearg:

Adding command-line arguments
-----------------------------

The base :ref:`analysis module<uganalysismodule>`,
:py:class:`bamboo.analysismodules.AnalysisModule`, calls the
:py:meth:`~bamboo.analysismodules.AnalysisModule.addArgs` method (the default
implementation does nothing) when constructing the command-line arguments
parser (using the `argparse`_ module).
Analysis modules can reimplement this method to specify more arguments, e.g.

.. code-block:: python

    class MyModule(...):

        def addArgs(self, parser):
            super(MyModule, self).addArgs(parser)
            parser.add_argument("--whichPlots", type=str,
                                default="control",
                                help="Set of plots to produce")


The parsed arguments are available under the ``args`` member variable, e.g.
``self.args.whichPlots`` in the example above.
The complete list of command-line options (including those specified in the
analysis module) can be printed with ``bambooRun -h -m myModule.py.MyModule``.
In fact the parser argument is an
`argument group`_,
so they are listed separately from those in the base class.
This is also used to copy all user-defined arguments to the commands that are
passed to the worker tasks, when running in distributed mode.

.. _recipecustomanacfg:

Editing the analysis configuration
----------------------------------

Similarly to the above, it is possible to modify the analysis configuration
(loaded from the YAML file) from a module before the configuration
is used to create jobs (in distributed mode), run on any file (in sequential mode),
or run plotIt (in the postprocessing step).
This allows e.g. to change the samples that are going to be used, change the list
of systematics, etc., without having to edit manually the YAML file or maintaining separate files.
Below is an example of how this works:

.. code-block:: python

    class MyModule(...):

        def customizeAnalysisCfg(self, analysisCfg):
            for smp in list(analysisCfg["samples"]):
                if not analysisCfg["samples"][smp].get("is_signal", False):
                    del analysisCfg["samples"][smp]



.. _recipemvaevaluate:

Evaluate an MVA classifier
--------------------------

Several external libraries can be used to evaluate the response of MVA
classifiers inside expressions.
For convenience, a uniform interface is defined that uses a vector of floats
as input and output, with implementations available for PyTorch_,
Tensorflow_, lwtnn_, TMVA_, and `ONNX Runtime`_.
That works as follows (see the documentation for the
:py:meth:`bamboo.treefunctions.mvaEvaluator` method for a detailed description,
additional options may be needed, depending on the type):

.. code-block:: python

    mu = tree.Muon[0]
    nn1 = mvaEvaluator("nn1.pt", mvaType="Torch")
    Plot.make1D("mu_nn1", nn1(mu.pt, mu.eta, mu.phi), hasMu)

For Tensorflow, PyTorch, and ONNX Runtime multiple inputs (and inputs with
different types) are also supported.
In that case, no automatic conversion is performed, so the inputs should be
passed in the correct format (most of the time the number of inputs per node
is known, so arrays constructed with :py:meth:`bamboo.treefunctions.array`
are a good choice).

.. warning:: Especially for PyTorch_ and Tensorflow_, setting up an
   installation where the necessary C(++) libraries are correctly identified,
   and compatible with the CPU capabilities, is not always trivial. See
   :ref:`this section<installmachinelearning>` in the installation guide for
   more information.

:ref:`Skims<recipeskims>` for training a classifier can also straightforwardly
be produced with bamboo_.

Obtaining a classifier in the right format
''''''''''''''''''''''''''''''''''''''''''

All MVA inference is done through the C(++) APIs provided by the different
machine learning and inference libraries, which means that the model should
be stored in the appropriate format (often with some conversion step).

ONNX_ and lwtnn_ are formats for the exchange and inference of neural networks,
so they need converters from the model building and/or training framework.
Converting Keras_ models to lwtnn_ is described on `the lwtnn wiki`_.
PyTorch_ comes with
`ONNX export <https://pytorch.org/docs/stable/onnx.html>`_ included.
Most Keras_ models can also easily be exporter to ONNX_ with keras2onnx_.

The `PyTorch`_ evaluator uses `TorchScript`_,
`this tutorial <https://pytorch.org/tutorials/advanced/cpp_export.html#step-1-converting-your-pytorch-model-to-torch-script>`_
is a very good starting point if your model is trained with `PyTorch`_.

TMVA_ uses an XML format which probably also just works.
The TMVA reader will work with multi-threading, but the
`reader class <https://root.cern/doc/master/classTMVA_1_1Experimental_1_1RReader.html>`_
uses locking because the internal TMVA classes are not thread-safe,
so performance will be degraded if aggressive multi-threading is used and
the TMVA evaluation dominates the CPU usage.

For Keras_ models Tensorflow_ is the most natural fit. Please note that the
frozen graph is needed, see e.g.
`keras_to_tensorflow <https://github.com/amir-abdi/keras_to_tensorflow>`_,
`this detailed explanation <https://medium.com/@sebastingarcaacosta/how-to-export-a-tensorflow-2-x-keras-model-to-a-frozen-and-optimized-graph-39740846d9eb>`_,
and `this script <https://github.com/FlorianBury/HHbbWWAnalysis/blob/master/MachineLearning/HHMachineLearning/KerasToTensorflowModel.py>`_
for an example of how to do so.

Testing the evaluation outside RDataFrame
'''''''''''''''''''''''''''''''''''''''''

MVA inference with all the libraries described above is done by creating
an instance of an evaluator class, which provides a similar
RDataFrame-friendly interface: the filename of te saved model and additional
options are passed to the constructor, and an evaluate method that takes the
input values and returns the returns the MVA outputs is called from inside the
RDataFrame graph.
It is straightforward to do the same from PyROOT: for each framework there is a
method in the :py:mod:`bamboo.root` to load the necessary shared libraries and
evaluator class.
After calling this method, an evaluator can be instantiated and tested with
some simple arguments.
This is done in the `bamboo tests <https://gitlab.cern.ch/cp3-cms/bamboo/-/blob/master/tests>`_,
so these can serve as an example (links for the the relevant fragments:
`test_tensorflow <https://gitlab.cern.ch/cp3-cms/bamboo/-/blob/master/tests/test_tensorflowceval_nn.py#L16-36>`_,
`test_lwtnn <https://gitlab.cern.ch/cp3-cms/bamboo/-/blob/master/tests/test_lwtnneval_nn.py#L17-38>`_,
`test_libtorch <https://gitlab.cern.ch/cp3-cms/bamboo/-/blob/master/tests/test_libtorcheval_nn.py#L8-23>`_;
TMVA is directly included in ROOT, so it is sufficient to retrieve the
``TMVA::Experimental::RReader`` class).

.. _recipemergedcategoryplots:

Make combined plots for different selections
--------------------------------------------

It is rather common to define categories with e.g. different lepton flavours
and selections, but then make plots with the entries from these (disjoint)
sets of events combined.
Given the structure of the RDataFrame_ graph and the
:py:class:`~bamboo.plots.Selection` tree, the most convenient way to achieve
this is by defining the histograms for each category, and make a merged
histogram later on.
The :py:class:`~bamboo.plots.SummedPlot` class does exactly this, and since it
presents the same interface to the analysis module as a regular
:py:class:`~bamboo.plots.Plot`, it can simply be added to the same plot list
(to produce only the combined plot and not those for the individual
contributions, it is sufficient to not add the latter to the plot list), e.g.

.. code-block:: python

   from bamboo.plots import Plot, SummedPlot, EquidistantBinning
   mjj_mumu = Plot.make1D("Mjj_MuMu", op.invariant_mass(jets[0].p4, jets[1].p4),
                          sel_mumu, EquidistantBinning(50, 20., 120.))
   mjj_elel = Plot.make1D("Mjj_ElEl", op.invariant_mass(jets[0].p4, jets[1].p4),
                          sel_elel, EquidistantBinning(50, 20., 120.))
   mjj_sum = SummedPlot("Mjj", [mjj_mumu, mjj_elel], title="m(jj)")
   plots += [ mjj_mumu, mjj_elel, mjj_sum ] # produce all plots


The other plot properties of a :py:class:`~bamboo.plots.SummedPlot` (titles,
labels etc.) can be specified with keyword arguments to the constructor;
otherwise they are taken from the first component plot.

.. note:: :py:class:`~bamboo.plots.SummedPlot` simply adds up the histograms,
   it is up to the user to make sure an event can only enter one of the
   categories, if this is what it is used for.

.. _recipeskims:

Producing skimmed trees
-----------------------

The :py:class:`bamboo.plots.Skim` class allows to define skimmed trees to save
in the output file.
Since this uses the ``Snapshot`` method from RDataFrame_, there will be an entry
for each event that passes the selection, so in some cases (e.g. MVA training)
additional manipulations may need to be done on these outputs.
A second limitation is that, as for plots, a skim is attached to a selection,
which means that if different categories need to be combined, multiple skims
should be defined, and the stored products merged |---| but multiple skims
can now be produced in the same job, thanks to the lazy Snapshot calls.
The main advantage over the :py:class:`~bamboo.analysismodules.SkimmerModule`
(which still exists for backwards compatibility) is that the same module can
produce plots and skims, with the same selections and definitions (in practice
a :ref:`command-line option<recipeotherhistogrampostprocessing>` would usually
be added to select some products), e.g.

.. code-block:: python

   from bamboo.plots import Plot, Skim

   twoMuSel = noSel.refine("twoMuons", cut=[ op.rng_len(muons) > 1 ])
   mll = op.invariant_mass(muons[0].p4, muons[1].p4)
   if self.args.makeSkim:
       plots.append(Skim("dimuSkim", {
           "run": None,  # copy from input file
           "luminosityBlock": None,
           "event": None,
           "dimu_M": mll,
           "mu1_pt": muons[0].pt,
           "mu2_pt": muons[1].pt,
           }, twoMuSel))
   else:
       plots.append(Plot.make1D("dimu_M", mll, twoMuSel,
                    EquidistantBinning(100, 20., 120.)))

.. _recipeotherhistogrampostprocessing:

Postprocessing beyond plotIt
----------------------------

The :py:class:`~bamboo.analysismodules.HistogramsModule` postprocessing method
calls plotIt_ to make the usual data and simulation stack plots (for the
different eras that are considered), and prints the counter values of cut flow
reports, but since all possible (meta-)information is available there, as well
as the filled histograms, it can be useful to do any further processing there
(e.g. running fits to the distributions, dividing histograms to obtain scale
factors or fake rates, exporting counts and histograms to a different format).

For many simple cases, it should be sufficient to override the
:py:meth:`~bamboo.analysismodules.HistogramsModule.postProcess` method, first
call the base class method, and then do any additional processing.
If the base class method is not called, the plot list should be constructed
by calling the :py:meth:`~bamboo.analysismodules.HistogramsModule.getPlotList`
method.

Most of the other code, e.g. to generate the plotIt_ YAML configuration file,
is factored out in helper methods to allow reuse from user-defined additions
|---| see the :py:func:`bamboo.analysisutils.writePlotIt` and
:py:func:`bamboo.analysisutils.printCutFlowReports` methods, and their
implementation.

.. note:: :py:meth:`~bamboo.analysismodules.HistogramsModule.getPlotList`,
   when called without a specified file and sample, will read a so-called
   skeleton file *for an arbitrary sample* (essentially an empty tree with the
   same format as the input |---| typically for the first sample encountered)
   from the results directory and calls the
   :py:meth:`~bamboo.analysismodules.HistogramsModule.definePlots` method with
   that to obtain the list of defined plots.
   This is also done when running with the ``--onlypost`` option, and works as
   expected when the same plots are defined for all samples.
   If this assumption does not hold, some customisation of the
   :py:meth:`~bamboo.analysismodules.HistogramsModule.definePlots` method will
   be necessary.

It is also possible to skip the writing of a plotIt_ YAML file, and directly
load the configuration as it would be parsed by plotIt with its partial python
reimplementation `pyplotit <https://gitlab.cern.ch/cp3-cms/pyplotit>`_, which
makes it easy to access the scaled grouped and stacked histograms.

As an example, a simple visualisation of 2D histograms could be obtained with

.. code-block:: python

   def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
       super(MyModule, self).postProcess(taskList, config=config, workdir=workdir, resultsdir=resultsdir)
       from bamboo.plots import Plot, DerivedPlot
       plotList_2D = [ ap for ap in self.plotList if ( isinstance(ap, Plot) or isinstance(ap, DerivedPlot) ) and len(ap.binnings) == 2 ]
       from bamboo.analysisutils import loadPlotIt
       p_config, samples, plots_2D, systematics, legend = loadPlotIt(config, plotList_2D, eras=self.args.eras[1], workdir=workdir, resultsdir=resultsdir, readCounters=self.readCounters, vetoFileAttributes=self.__class__.CustomSampleAttributes, plotDefaults=self.plotDefaults)
       from plotit.plotit import Stack
       from bamboo.root import gbl
       for plot in plots_2D:
           obsStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "DATA")
           expStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "MC")
           cv = gbl.TCanvas(f"c{plot.name}")
           cv.Divide(2)
           cv.cd(1)
           expStack.obj.Draw("COLZ")
           cv.cd(2)
           obsStack.obj.Draw("COLZ")
           cv.Update()
           cv.SaveAs(os.path.join(resultsdir, f"{plot.name}.png"))

.. _recipedatadrivenbackgrounds:

Data-driven backgrounds and subprocesses
----------------------------------------

In many analyses, some backgrounds are estimated from a data control region,
with some per-event weight that depends on the physics objects found etc.
This can be largely automatised: besides the main
:py:class:`~bamboo.plots.Selection`, one or more instances with alternative
cuts (the control region instead of the signal region) and weights (the
mis-ID, fake, or transfer factors). That is exactly what is done by the
:py:class:`~bamboo.plots.SelectionWithDataDriven` class: its
:py:meth:`~bamboo.plots.SelectionWithDataDriven.create` method is like
:py:meth:`bamboo.plots.Selection.refine`, but with alternative cuts and weights
to construct the correctly reweighted control region besides the signal region.
Since it supports the same interface as :py:class:`~bamboo.plots.Selection`,
further selections can be applied to both regions at the same time, and every
:py:class:`~bamboo.plots.Plot` will declare the histograms for both.
The additional code for configuring which data-driven contributions to use,
and to make sure that histograms for backgrounds end up in a separate file
(such that they can transparently be used e.g. in plotIt_), the analysis module
should inherit from
:py:class:`~bamboo.analysismoduldes.DataDrivenBackgroundHistogramsModule` (or
:py:class:`~bamboo.analysismoduldes.DataDrivenBackgroundAnalysisModule` if the
histogram-specific functionality is not required).

Data-driven contributions should be declared in the YAML configuration file
with the lists of samples or groups from which the background estimate should
be obtained, those that are replaced by it, e.g.

.. code-block:: yaml

 datadriven:
   chargeMisID:
     uses: [ data ]
     replaces: [ DY ]
   nonprompt:
     uses: [ data ]
     replaces: [ TTbar ]

The ``--datadriven`` command-line argument can then be used to specify which of
these should be used (``all``, ``none``, or an explicit list).
Several can be specified in the same run: different sets will then be produced.
The parsed versions are available as the ``datadrivenScenarios`` attribute of
the module (and the contributions as ``datadrivenContributions``).
The third argument passed to the
:py:meth:`~bamboo.plots.SelectionWithDataDriven.create` method should
correspond to one of the contribution names in the YAML file, e.g. (continuing
the example above):

.. code-block:: python

 hasSameSignElEl = SelectionWithDataDriven.create(hasElElZ, "hasSSDiElZ", "chargeMisID",
     cut=(diel[0].Charge == diel[1].Charge),
     ddCut=(diel[0].Charge != diel[1].Charge),
     ddWeight=p_chargeMisID(diel[0])+p_chargeMisID(diel[1]),
     enable=any("chargeMisID" in self.datadrivenContributions and self.datadrivenContributions["chargeMisID"].usesSample(sample, sampleCfg))
     )

The generation of modified sample configuration dictionaries in the plotIt_
YAML file can be customised by replacing the corresponding entry in the
:py:attr:`~bamboo.analysismodules.DataDrivenBackgroundAnalysisModule.datadrivenContributions`
dictionary with a variation of a :py:class:`~bamboo.analysismodules.DataDrivenContribution`
instance.

A very similar problem is the splitting of a sample into different
contributions based on some generator-level quantities, e.g. the number of
(heavy-flavour) partons in the matrix element.
In this case, splitting the RDF graph early on, such that each event is
processed by a nearly identical branch of it, would not be very efficient.
The :py:class:`bamboo.plots.LateSplittingSelection` class, a variation of
:py:class:`bamboo.plots.SelectionWithDataDriven`, may help in such cases:
it will branch the RDF graph only when attaching plots to a selection, so it
can be constructed earlier, but the RDF graph branching will be minimal.
By default the combined plot is also saved because it helps avoid
duplication in the graph, but this may be disabled by passing
``keepInclusive=False`` to the
:py:meth:`~bamboo.plots.LateSplittingSelection.create` method.
To make sure the resulting histograms are saved, an analysis module that makes
use of :py:class:`~bamboo.plots.SelectionWithDataDriven` should inherit from
:py:class:`bamboo.analysismodules.HistogramsModuleWithSub`; since the use case
is rather specific, no customisation to the postprocessing method is done,
but in most cases it should be straightforward to manipulate the ``samples``
dictionary in the configuration before calling the superclass' postprocessing
method, see e.g. :ref:`this recipe<recipeotherhistogrampostprocessing>`.

.. _recipebatchjobmanagement:

Dealing with (failed) batch jobs
--------------------------------

When splitting the work over a set of batch jobs using the
``--distributed=driver`` option (see the :ref:`bambooRun options <ugbambooRun>`
reference), some may fail for various reasons: CPU time or memory limits
that are too tight, environment or hardware issues on the worker node,
or bugs in the analysis or bamboo code.
The monitoring loop will check the status of the running jobs every two
minutes, print information when some fail, merge outputs if all jobs for
a sample complete, and finally run the postprocessing when all samples are
processed, or exit when no running jobs remain.
Currently (improvements and additions are being discussed in
`issue #87 <https://gitlab.cern.ch/cp3-cms/bamboo/-/issues/87>`_) resubmission
of the failed jobs and monitoring of the recovery jobs, after identifying the
reason why they fail, needs to be done using the tools provided by the batch
system (``sbatch --array=X,Y,Z ...`` for slurm; for HTCondor a helper script
``bambooHTCondorResubmit`` is provided that takes a very similar set of options
|---| the commands are also printed by the monitoring loop).

When the outputs for all jobs that initially failed have been produced,
``bambooRun`` can be used with the  ``--distributed=finalize`` option (and
otherwise all the same options as for the original submission) to do any
remaining merging of outputs, and run the postprocessing step.
If some outputs are missing it will suggest a resubmission command and exit.
This only looks at the output files that are found to decide what still needs
to be done, so if a file in the ``results/`` subdirectory of the output is
present, it will assume that is valid |---| this can be exploited in two ways:
if anything goes wrong in the merging, removing the ``results/<<sample>>.root``
and running with ``--distributed=finalize`` will try that again (similarly,
removing a corrupt job output file will add it to the resubmission command),
and if a sample is processed with a different splitting it is sufficient to put
the merged output file in the ``results/`` directory.

.. note:: Understanding why batch jobs fail is not always easy,
   and the specifics depend on the batch system and the environment
   Bamboo collects all possible log files (standard output and error,
   submission log) in the ``batch/logs`` directory, and per-job inputs and
   output in ``batch/input`` and ``batch/output``, respectively.

   In principle the worker jobs run in the same environment as where they are
   submitted, and typically take all software is installed from CVMFS, so most
   problems with batch jobs are related to data access, e.g. overloaded storage
   or permissions to access some resources.
   When reading files through XRootD a grid proxy is needed, at CERN the easiest
   is to `create it in an AFS directory and pass that to the job <https://batchdocs.web.cern.ch/tutorial/exercise2e_proxy.html#using-x509-proxy-without-shipping-it-with-the-job>`_.

.. _recipereproduciblegit:

Reproducible analysis: keep track of the version that produced some results
---------------------------------------------------------------------------

While bamboo_ does not by default force you to adopt a specific workflow,
it can help with adopting some best practices for reproducible analysis.
The most important thing is to keep the analysis code under version control:
git_ is widely used for this (see the `Pro Git book`_ for an introduction).
The idea is to keep the analysis code and configurations in a separate
directory, which is tracked by git_, from the bamboo_ outputs (plots, results
etc.) |---| this can also be a subdirectory that is ignored by git_, if you
prefer.

``bambooRun`` will write a file with the git_ version of the repository where
the module and configuration file are found to the output directory: the
``version.yml`` file.
This will also contain the list of command-line arguments that were passed,
and the bamboo_ version.
In order for this to work, the analysis repository must at least have all local
changes committed, but it is even better to create a tag for versions that are
used to produce results, and push it to GitHub or GitLab (see e.g.
`this overview <https://git-scm.com/book/en/v2/Git-Basics-Tagging>`_; it is
also worth noting that tags in git can be *annotated*, which means that they
can have a descriptive message, just like a commit).
If the ``--git-policy`` switch, or the ``policy`` key in the ``git`` section in
the ``~/.config/bamboorc`` file, gets a different value than the default
(``testing``), ``bambooRun`` will check that the analysis code is committed,
tagged, or tagged and pushed, based on the specified value
(``committed``, ``tagged``, and ``pushed``, respectively).
It is recommended to use at least ``committed`` (which will print warnings
if the commit has not been pushed, or is not tagged).

Tip: use git worktrees
''''''''''''''''''''''

An interesting solution to have several checkouts of the same repository, e.g.
to run jobs with one version of the analysis code, and edit it at the same time,
are git worktrees (see `git-worktree manual page`_ for a reference, or
`this article <https://opensource.com/article/21/4/git-worktree>`_ for some
examples).
They may also help with making sure that everything is committed and tracked by
git_: if you use the main clone to edit the code, and checkout a commit or tag
in a worktree to produce plots on the full dataset, committing all necessary
files is the best way to keep them synchronized (the "production" directory
should not contain any untracked files then).

Git worktrees were introduced in version 2.5, so it will not work with older
versions.
The LCG distribution includes git since LCG_99, so if you use that method of
installing bamboo it will be included automatically.

Tip: make a python package out of your analysis
'''''''''''''''''''''''''''''''''''''''''''''''

For small analyses and projects, all that is needed are a YAML configuration
file and a python module, or a few of each.
When code needs to be shared between different modules, a simple solution is to
make it a python package: move the shared modules to a subdirectory, called
e.g. ``myanalysis``, add an empty ``__init__.py`` to it, and write a
``setup.py`` file (still required for editable installs) like this one:

.. code-block:: py

   from setuptools import setup, find_packages

   setup(
       name="myexperiment-myanalysis",
       description="Hunt for new physics (implemented with bamboo)",
       url="https://gitlab.cern.ch/.../...",
       author="...",
       author_email="...",

       packages=find_packages("."),

       setup_requires=["setuptools_scm"],
       use_scm_version=True
   )

It can then be installed in the virtual environment with

.. code-block:: bash

   pip install -e .

and the shared modules imported as ``myanalysis.mymodule``.
The ``-e`` flag actually puts only a link in the virtual environment, such that
any changes in the source files are immediately available, without updating the
installed version (then it does not spoil the change tracking above).

More information on packaging python packages can be found in the
`PyPA packaging tutorial <https://python-packaging-user-guide.readthedocs.io/tutorials/packaging-projects/>`_,
the `setuptools documentation <https://setuptools.readthedocs.io/en/latest/userguide/declarative_config.html>`_,
the `PyPA setuptools guide <https://python-packaging-user-guide.readthedocs.io/guides/distributing-packages-using-setuptools/>`_
and the `Scikit-HEP packaging guidelines <https://scikit-hep.org/developer/packaging>`_.
For packages that include C++ components `scikit-build <https://scikit-build.readthedocs.io/en/latest/>`_
allows to combine setuptools and CMake (it is also used by bamboo_ and correctionlib_).

.. _bamboo: https://cp3.irmp.ucl.ac.be/~pdavid/bamboo/index.html

.. _CP3-llbb framework: https://github.com/cp3-llbb/Framework

.. _correctionlib: https://github.com/cms-nanoAOD/correctionlib/

.. _pileupcalc documentation: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData#Pileup_JSON_Files_For_Run_II

.. _NanoAODTools: https://github.com/cms-nanoAOD/nanoAOD-tools

.. _jetmetUncertainties module: https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/jme/jetmetUncertainties.py

.. _muonScaleResProducer module: https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/common/muonScaleResProducer.py

.. _argparse: https://docs.python.org/3/library/argparse.html

.. _argument group: https://docs.python.org/3/library/argparse.html#argument-groups

.. _RDataFrame: https://root.cern.ch/doc/master/classROOT_1_1RDataFrame.html

.. _plotIt: https://github.com/cp3-llbb/plotIt

.. _PyTorch: https://pytorch.org/

.. _Tensorflow: https://www.tensorflow.org/

.. _lwtnn: https://github.com/lwtnn/lwtnn

.. _TMVA: https://root.cern/manual/tmva/

.. _ONNX: https://onnx.ai

.. _ONNX Runtime: https://www.onnxruntime.ai

.. _Keras: https://keras.io

.. _the lwtnn wiki: https://github.com/lwtnn/lwtnn/wiki/Keras-Converter

.. _TorchScript: https://pytorch.org/docs/stable/jit.html

.. _keras2onnx: https://github.com/onnx/keras-onnx

.. _git: https://git-scm.com/

.. _Pro Git book: https://git-scm.com/book/en/v2

.. _git-worktree manual page: https://git-scm.com/docs/git-worktree

.. |---| unicode:: U+2014
   :trim:
