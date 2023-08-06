"""
Example of optionally skimming the inputs and storing precalculated values,
    all with the same module (based on the Run2 TTW analysis TOP-21-011)
"""
import os.path
from functools import partial
from itertools import chain
from logging import getLogger

from bamboo import treedecorators as btd
from bamboo import treefunctions as op
from bamboo.analysismodules import NanoAODHistoModule

logger = getLogger(__name__)


def is_loose_muon_top(mu):
    return op.AND(
        mu.mediumId,
        mu.pt > 10.,
        op.abs(mu.eta) < 2.4,
        op.abs(mu.dxy) < 0.05,
        op.abs(mu.dz) < 0.1,
        mu.sip3d < 8.,
        mu.miniPFRelIso_all < 0.4
    )


def is_loose_electron_top(el, loose_muons=None):
    return op.AND(
        el.pt > 10.,
        op.abs(el.eta) < 2.4,
        el.lostHits <= 1,
        op.abs(el.dxy) < 0.05,
        op.abs(el.dz) < 0.1,
        el.sip3d < 8.,
        el.miniPFRelIso_all < 0.4,
        op.NOT(op.rng_any(
            loose_muons,
            lambda mu: op.deltaR(el.p4, mu.p4) < 0.05
        ))
    )


def interp_deepJet_top_(pt, minpt=25., maxpt=50., wpLo=None, wpHi=None):
    return op.switch(
        pt < minpt,
        op.c_float(wpLo),
        op.switch(
            pt > maxpt,
            op.c_float(wpHi),
            wpLo - ((wpLo - wpHi) / (maxpt - minpt)) * (pt - minpt)
        )
    )


interp_deepJet_top = {
    "el_2016": partial(interp_deepJet_top_, minpt=25., maxpt=50., wpLo=0.5, wpHi=0.05),
    "el_2017": partial(interp_deepJet_top_, minpt=25., maxpt=50., wpLo=0.5, wpHi=0.08),
    "el_2018": partial(interp_deepJet_top_, minpt=25., maxpt=50., wpLo=0.4, wpHi=0.05),
    "mu_2016": partial(interp_deepJet_top_, minpt=20., maxpt=40., wpLo=0.02, wpHi=0.015),
    "mu_2017": partial(interp_deepJet_top_, minpt=20., maxpt=40., wpLo=0.025, wpHi=0.015),
    "mu_2018": partial(interp_deepJet_top_, minpt=20., maxpt=40., wpLo=0.025, wpHi=0.015)
}


def is_fakeable_muon_top(mu, minconept=10., mf=0.67, year=None):
    hasJet = mu.jet.idx != -1
    return op.switch(
        mu.mvaTOP > 0.4, mu.pt > minconept,
        op.AND(
            mf * mu.pt * (1. + mu.jetRelIso) > minconept,
            hasJet,
            mu.jetRelIso < 1.22222,  # R_pt > 0.45
            mu.jet.btagDeepFlavB < interp_deepJet_top[f"mu_{year}"](mu.pt)
        ))


def is_fakeable_electron_top(el, year=None, mf=0.67, minconept=10.):
    # assuming already loose
    isEB = op.abs(el.eta + el.deltaEtaSC) <= 1.497
    hasJet = el.jet.idx != -1
    return op.AND(
        el.sieie < op.switch(isEB, op.c_float(0.011), op.c_float(0.030)),
        el.hoe < 0.10,
        el.eInvMinusPInv > -.04,
        el.convVeto,
        el.tightCharge == 2,  # isGsfCtfScPixChargeConsistent
        op.switch(
            el.mvaTOP > 0.4,
            el.pt > minconept,
            op.AND(
                el.mvaFall17V2noIso_WPL,
                mf * el.pt * (1. + el.jetRelIso) > minconept,
                hasJet,
                el.jetRelIso < 1.,  # R_pt > 0.5
                el.jet.btagDeepFlavB < interp_deepJet_top[f"el_{year}"](el.pt)
            )
        )
    )


class TTWwithSkim(NanoAODHistoModule):
    """
    An example module for an analysis that (optionally) uses skimmed datasets

    There are several possible reasons to do this: running on smaller input files
    to reduce the load on the storage and speed up the analysis, or precalculating
    some expensive variables (here: the topMVA lepton MVA classifier).

    There are three modes, configured through --preselSkim:
    - no: no skimming
    - produce: write out the skim for later use
    - use: run on the skimmed samples

    The code in the module below is organised such that the same plots can be
    produced from the original files and from the intermediate skims.

    Currently missing:
    - a --no-merge option (to be implemented in the base AnalysisModule) to skip
      the merging of the per-job outputs (such that job splitting is still
      possible with the skims)
    - handling the skim/no-skim configurations: the goal is that only the
      original (unskimmed) config needs to be written, and a new one with the
      skims is automatically created
    """
    def addArgs(self, parser):
        super().addArgs(parser)
        parser.add_argument(
            "--backend", type=str, default="dataframe",
            help="Backend to use, 'dataframe' (default), 'lazy', or 'compiled'")
        parser.add_argument(
            "--preselSkim", type=str, choices=["no", "produce", "use"],
            help="Select skim mode: no (use original NanoAODs - default), produce the skim, or use it")

    def customizeAnalysisCfg(self, config):
        if self.args.preselSkim == "use":
            config["tree"] = "TriggerAndge2Fakeable"
            # FIXME quick hack, a new (partial) YAML should probably be generated
            # FIXME from the postprocess method instead
            for smpNm, smpCfg in config["samples"].items():
                smpCfg["files"] = [os.path.join("../tests/out_ttw_skim_2", "results", f"{smpNm}.root")]

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        isMC = self.isMC(sample)
        year = sampleCfg.get("era")
        eraInYear = "" if isMC else next(tok for tok in sample.split("_") if tok.startswith(year))[4:]

        tree, noSel, be, lumiArgs = super().prepareTree(
            tree, sample=sample, sampleCfg=sampleCfg, backend=self.args.backend,
            description=btd.NanoAODDescription.get("v7", year=year, isMC=isMC))

        # in practice: add also on-the-fly calculators of jet/MET variations,
        # pileup reweighting, MET filters

        baseSel = noSel
        if isMC:
            baseSel = baseSel.refine("mcWeight", weight=tree.genWeight)

        pd_trig = getTriggersAndPrimaryDatasets(year, eraInYear, tree, isMC=isMC)
        if isMC:
            trigCut = op.OR(*chain.from_iterable(pd_trig.values()))
        else:
            from bamboo.analysisutils import makeMultiPrimaryDatasetTriggerSelection
            trigCut = makeMultiPrimaryDatasetTriggerSelection(sample, pd_trig)
            logger.info(f"Trigger cut for {sample}: {op._to.adaptArg(trigCut).get_cppStr()}")

        return tree, baseSel, be, lumiArgs

    def definePlots(self, t, baseSel, sample=None, sampleCfg=None):
        from bamboo.plots import Skim, CategorizedSelection
        from bamboo.plots import EquidistantBinning as EqB

        year = sampleCfg.get("era")

        if self.args.preselSkim == "use":  # reading skim
            hasAtLeast2Fakeable = baseSel
            fakeable_muons = op.select(t.Muon, lambda mu: mu.isFakeable)
            fakeable_electrons = op.select(t.Electron, lambda el: el.isFakeable)
        else:  # produce skim, or run on unskimmed input
            loose_muons = op.select(t.Muon, is_loose_muon_top)
            loose_electrons = op.sort(
                op.select(
                    t.Electron,
                    partial(is_loose_electron_top, loose_muons=loose_muons)),
                lambda el: -el.pt  # smeared, need to sort
            )

            has2Loose = baseSel.refine("has2Ll", cut=(
                op.rng_len(loose_electrons) + op.rng_len(loose_muons) >= 2
            ))

            # https://github.com/cms-top/cmssw/raw/topNanoV6_from-CMSSW_10_2_18/PhysicsTools/NanoAOD/data/TMVA_BDTG_TOP_muon_2016.weights.xml  # noqa: 501
            mu_bdt = op.mvaEvaluator(f"TMVA_BDTG_TOP_muon_{year}.weights.xml", mvaType="TMVA")
            muon_mvaTOP = op.map(t.Muon, lambda mu: op.switch(
                op.rng_any(loose_muons, lambda lm: lm == mu),  # must be loose
                mu_bdt(
                    op.log(op.abs(mu.dxy)),
                    mu.miniPFRelIso_chg,
                    mu.miniPFRelIso_all - mu.miniPFRelIso_chg,
                    mu.jetPtRelv2,
                    mu.sip3d,
                    mu.segmentComp,
                    1. / (1. + mu.jetRelIso),  # ptRatio
                    op.switch(
                        mu.jet.isValid,
                        op.max(mu.jet.btagDeepFlavB, 0.),
                        0.),
                    mu.pt,
                    mu.jetNDauCharged,
                    op.abs(mu.eta),
                    op.log(op.abs(mu.dz)),
                    mu.pfRelIso03_all
                )[0],
                -1.
            ))
            # https://github.com/cms-top/cmssw/raw/topNanoV6_from-CMSSW_10_2_18/PhysicsTools/NanoAOD/data/TMVA_BDTG_TOP_elec_2016.weights.xml  # noqa: 501
            el_bdt = op.mvaEvaluator(f"TMVA_BDTG_TOP_elec_{year}.weights.xml", mvaType="TMVA")
            electron_mvaTOP = op.map(t.Electron, lambda el: op.switch(
                op.rng_any(loose_electrons, lambda le: le == el),  # must be loose
                el_bdt(
                    op.log(op.abs(el.dxy)),
                    el.miniPFRelIso_chg,
                    el.miniPFRelIso_all - el.miniPFRelIso_chg,
                    el.jetPtRelv2,
                    el.sip3d,
                    el.mvaFall17V2noIso,
                    1. / (1. + el.jetRelIso),  # ptRatio
                    op.switch(
                        el.jet.isValid,
                        op.max(el.jet.btagDeepFlavB, 0.),
                        0.),
                    el.pt,
                    el.jetNDauCharged,
                    op.abs(el.eta),
                    op.log(op.abs(el.dz)),
                    el.pfRelIso03_all
                )[0],
                -1.
            ))
            # Add attributes to electron and muon proxy class
            # to take these from the precalculated arrays
            t.Muon.valueType.mvaTOP = btd.itemProxy(muon_mvaTOP)
            t.Electron.valueType.mvaTOP = btd.itemProxy(electron_mvaTOP)

            fakeable_electrons = op.select(
                loose_electrons,
                partial(is_fakeable_electron_top, year=year)
            )
            fakeable_muons = op.select(
                loose_muons,
                partial(is_fakeable_muon_top, year=year)
            )

            hasAtLeast2Fakeable = has2Loose.refine("has2Fl", cut=(
                op.rng_len(fakeable_electrons) + op.rng_len(fakeable_muons) >= 2
            ))

            muon_isFakeable = op.map(t.Muon, lambda mu: op.rng_any(
                fakeable_muons, lambda fm: fm == mu))
            electron_isFakeable = op.map(t.Electron, lambda mu: op.rng_any(
                fakeable_electrons, lambda fm: fm == mu))

            if self.args.preselSkim == "produce":
                return [Skim("TriggerAndge2Fakeable", {
                    # new columns
                    "Muon_isFakeable": muon_isFakeable,
                    "Muon_mvaTOP": muon_mvaTOP,
                    "Electron_isFakeable": electron_isFakeable,
                    "Electron_mvaTOP": electron_mvaTOP,
                }, hasAtLeast2Fakeable,
                    # copy everything except Photon, Tau, and IsoTrack attributes
                    keepOriginal=Skim.KeepRegex("^(?!Photon_|Tau_|IsoTrack_|LowPtElectron_|boostedTau_).*$")
                )]
            else:  # not using the skim
                t.Muon.valueType.isFakeable = btd.itemProxy(muon_isFakeable)
                t.Electron.valueType.isFakeable = btd.itemProxy(electron_isFakeable)

        def conept(lep):
            return op.switch(
                lep.isFakeable,
                op.switch(
                    lep.mvaTOP > 0.4,  # definition of "tight" (if fakeable)
                    lep.pt,  # tight
                    .67 * lep.pt * (1. + op.switch(
                        op.AND(lep.jet.isValid, op.deltaR(lep.p4, lep.jet.p4) < 0.4),
                        lep.jetRelIso,  # matching jet: use jet pt for cone
                        lep.miniPFRelIso_all  # no matching jet: use cone
                    ))
                ), 0.)
        # precalculate conept, same trick as isFakeable and mvaTOP in no-skim scenario
        for lepBase in (t.Muon, t.Electron):
            lepBase.valueType.conept = btd.itemProxy(op.map(lepBase, conept))

        # sort fakeable leptons by decreasing cone pt
        fakeable_muons = op.sort(fakeable_muons, lambda mu: -mu.conept)
        fakeable_electrons = op.sort(fakeable_electrons, lambda el: -el.conept)

        # 2l channel: ask for exactly two, and make flavour categories
        has2Fakeable = hasAtLeast2Fakeable.refine("hasEq2Fl", cut=(
            op.rng_len(fakeable_electrons) + op.rng_len(fakeable_muons) == 2
        ))
        has2Fakeable = CategorizedSelection(name="hasEq2Fl", categories={
            "ElEl": (has2Fakeable.refine("hasEq2Fl_ElEl", cut=(
                op.rng_len(fakeable_electrons) == 2
            )), (fakeable_electrons[0], fakeable_electrons[1])),
            "ElMu": (has2Fakeable.refine("hasEq2Fl_ElMu", cut=(
                op.rng_len(fakeable_electrons) == 1,
                op.rng_len(fakeable_muons) == 1,
                fakeable_electrons[0].conept > fakeable_muons[0].conept
            )), (fakeable_electrons[0], fakeable_muons[0])),
            "MuEl": (has2Fakeable.refine("hasEq2Fl_MuEl", cut=(
                op.rng_len(fakeable_electrons) == 1,
                op.rng_len(fakeable_muons) == 1,
                fakeable_electrons[0].conept < fakeable_muons[0].conept
            )), (fakeable_muons[0], fakeable_electrons[0])),
            "MuMu": (has2Fakeable.refine("hasEq2Fl_MuMu", cut=(
                op.rng_len(fakeable_muons) == 2
            )), (fakeable_muons[0], fakeable_muons[1]))
        })

        # cone pt plots
        plots = (
            has2Fakeable.makePlots(
                "2F_L1ConePT", (lambda ll: ll[0].conept), EqB(100, 0., 200.), plotopts={"rebin": 4})
            + has2Fakeable.makePlots(
                "2F_L2ConePT", (lambda ll: ll[1].conept), EqB(100, 0., 200.), plotopts={"rebin": 4})
            + has2Fakeable.makePlots(
                "2F_L1mvaTOP", (lambda ll: ll[0].mvaTOP), EqB(100, -1., 1.), plotopts={"log-y": True})
            + has2Fakeable.makePlots(
                "2F_L2mvaTOP", (lambda ll: ll[1].mvaTOP), EqB(100, -1., 1.), plotopts={"log-y": True})
        )

        return plots


def getTriggersAndPrimaryDatasets(year, fullEra, evt, isMC=False):
    """
    Trigger and primary dataset definitions for the multilepton mix in Run 2

    overly complex for this example, but maybe nice to have; the ranges come from
    https://gitlab.cern.ch/-/snippets/1275
    """
    if fullEra:
        era = fullEra[0]  # catch things like "C1" and "C2"
    else:
        era = ""
    hlt = evt.HLT

    def _getSel(hltSel):
        if str(hltSel) != hltSel:
            return [getattr(hlt, sel) for sel in hltSel]
        else:
            return [getattr(hlt, hltSel)]

    def forEra(hltSel, goodEras):
        if isMC or era in goodEras:
            return _getSel(hltSel)
        else:
            return []

    def notForEra(hltSel, badEras):
        if isMC or era not in badEras:
            return _getSel(hltSel)
        else:
            return []

    def fromRun(hltSel, firstRun, theEra, otherwise=True):
        if isMC:
            return _getSel(hltSel)
        elif fullEra == theEra:
            sel = _getSel(hltSel)
            return [op.AND((evt.run >= firstRun), (op.OR(*sel) if len(sel) > 1 else sel[0]))]
        elif otherwise:
            return _getSel(hltSel)
        else:
            return []

    # FIXME add three-lepton?
    if year == "2016":
        return {
            "SingleMuon": ([hlt.IsoMu24, hlt.IsoTkMu24, hlt.Mu50, hlt.Mu45_eta2p1]
                           + fromRun("TkMu50", 274954, "B2", otherwise=(era != "B"))),
            "SingleElectron": [hlt.Ele27_WPTight_Gsf, hlt.Ele105_CaloIdVT_GsfTrkIdT,
                               hlt.Ele115_CaloIdVT_GsfTrkIdT],
            # non-DZ version heavily prescaled for a few /fb at end of 2016,
            # Tk-Tk DZ-version only introduced at the end of 2016
            "DoubleMuon": ([hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                            hlt.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL,
                            hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                            hlt.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ]
                           + forEra(("TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL",
                                     "TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ"), "H")
                           + [hlt.Mu30_TkMu11]),
            # non-DZ not existing end of 2016, DZ-version not existing first half of 2016
            "MuonEG": (notForEra(("Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL",
                                  "Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL"), "H")
                       + forEra("Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ", "H")
                       + notForEra("Mu30_Ele30_CaloIdL_GsfTrkIdVL", "H")
                       + fromRun(("Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                                  "Mu33_Ele33_CaloIdL_GsfTrkIdVL"),
                                 278273, "F2", otherwise=(era in "GH"))),
            "DoubleEG": ([hlt.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ]
                         + notForEra("DoubleEle33_CaloIdL_GsfTrkIdVL", "H")
                         + [hlt.DoubleEle33_CaloIdL_GsfTrkIdVL_MW])
        }
    elif year == "2017":
        return {  # only consider eras B-F
            # HLT_IsoMu24 is off for a 3.48/fb,
            # HLT_IsoMu24_eta2p1 off for ~9/fb,
            # HLT_TkMu100 not existing for first ~5/fb
            "SingleMuon": ([hlt.IsoMu24, hlt.IsoMu24_eta2p1, hlt.IsoMu27, hlt.Mu50]
                           + notForEra(("OldMu100", "TkMu100"), "B")),
            # first two triggers heavily prescaled at some /fb, last trigger missing for first ~14/fb
            "SingleElectron": (fromRun("Ele32_WPTight_Gsf_L1DoubleEG",
                                       302026, "C2", otherwise=(era in "DEF"))
                               + [hlt.Ele35_WPTight_Gsf]
                               + notForEra("Ele115_CaloIdVT_GsfTrkIdT", "B")),
            "DoubleMuon": ([hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL, hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                            hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8]
                           + fromRun("Mu37_TkMu27", 302026, "C2", otherwise=(era in ("D", "E", "F")))
                           # Mass3p8 trigger off at start of 2017
                           + notForEra("Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8", "B")),
            "MuonEG": ([hlt.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                        hlt.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,
                        hlt.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ]
                       + notForEra("Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL", "B")
                       # Introduced from menu version 3 on (missing for first ~14/fb)
                       + fromRun(("Mu27_Ele37_CaloIdL_MW", "Mu37_Ele27_CaloIdL_MW"),
                                 302026, "C2", otherwise=(era in ("D", "E", "F")))),
            "DoubleEG": [hlt.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL, hlt.DoubleEle33_CaloIdL_MW]
        }
    elif year == "2018":
        return {
            # OldMu100 and TkMu100 are recommend to recover inefficiencies at high pt
            # https://indico.cern.ch/event/766895/contributions/3184188/attachments/1739394/2814214/IdTrigEff_HighPtMu_Min_20181023_v2.pdf  # noqa: 501
            "SingleMuon": [hlt.IsoMu24, hlt.IsoMu27, hlt.Mu50, hlt.OldMu100, hlt.TkMu100],
            "EGamma": [hlt.Ele32_WPTight_Gsf, hlt.Ele115_CaloIdVT_GsfTrkIdT,
                       hlt.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL, hlt.DoubleEle25_CaloIdL_MW],
            "DoubleMuon": [hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8, hlt.Mu37_TkMu27],
            "MuonEG": [hlt.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                       hlt.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,
                       hlt.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,
                       hlt.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                       hlt.Mu27_Ele37_CaloIdL_MW, hlt.Mu37_Ele27_CaloIdL_MW]
        }
