import yaml

from cppyy import gbl
from dataframe.dataframebackend import DataframeBackend
from dataframe.treedecorators import decorateTTW

with open("ttW.yaml") as df:
    ttWdesc = yaml.load(df)

f = gbl.TFile.Open("ttW_sample.root")
t_ = f.Get("t")
t = decorateTTW(t_, description=ttWdesc)
be, noSel = DataframeBackend.create(t)
