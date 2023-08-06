import os.path

import pytest

testData = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture(scope="module")
def decoNano():
    from bamboo.root import gbl
    f = gbl.TFile.Open(os.path.join(testData, "DY_M50_2016postproc_JMEKin_bTagShape_puWeight.root"))
    tree = f.Get("Events")
    from bamboo.treedecorators import decorateNanoAOD, NanoAODDescription, nanoPUWeightVar, ReadJetMETVar
    from bamboo.dataframebackend import DataframeBackend
    nanoReadJetMETVar_MC = ReadJetMETVar(
        "Jet", "MET_T1",
        bTaggers=["csvv2", "deepcsv", "deepjet", "cmva"],
        bTagWPs=["L", "M", "T", "shape"])
    tup = decorateNanoAOD(
        tree, NanoAODDescription.get(
            "v5", year="2016", isMC=True,
            systVariations=[nanoPUWeightVar, nanoReadJetMETVar_MC]))
    be, noSel = DataframeBackend.create(tup)
    yield tup


def test_getSimpleObjects(decoNano):
    assert decoNano.Electron[0]
    assert decoNano.Muon[0]
    assert decoNano.Photon[0]
    assert decoNano.SubJet[0]
    assert decoNano.FatJet[0]


def test_getJet(decoNano):
    assert decoNano.Jet[0]


def test_simpleRef(decoNano):
    assert decoNano.Electron[0].photon
    assert decoNano.FatJet[0].subJet1


def test_toJetRef(decoNano):
    assert decoNano.Electron[0].jet
    assert decoNano.Muon[0].jet


def test_fromJetRef(decoNano):
    jet = decoNano.Jet[0]
    assert jet.muon1
    assert jet.muon2
    assert jet.electron1
    assert jet.electron2
