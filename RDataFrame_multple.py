from ROOT import RDataFrame
import ROOT
import matplotlib.pyplot as plt
import awkward as ak
import json
from utils import (
    get_lepton_preselection, 
    get_jet_preselection
)


from ROOT import gROOT 
with open(f"fileset_2017_UL_NANO.json", "r") as f:
    fileset = json.load(f)



redirector = "root://cmsxrootd.fnal.gov/"
sample = "DYJetsToLL_M-50_HT-1200to2500"

file = fileset[sample]

"""
file = [
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/270000/58FE9875-8CED-E248-978F-8076F811BBE7.root",
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/280000/23AB22BC-0228-C847-9BB4-59DD4F7238A6.root",
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/280000/48F8F0E4-1117-E943-9FEE-4B2EFBC33FFF.root",
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/280000/89809F2E-C546-C74D-B83E-E846394C0285.root",
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/280000/E876B7D7-3F04-0D4D-9634-07628E317F98.root"
    ]"""


### Reading the ROOT FIles
names = ROOT.std.vector('string')()
for n in [redirector + filename for filename in file]: names.push_back(n)
df = RDataFrame("Events", names)


df = df.Range(100000)


channel = "electron"

with open(f"infiles/{channel}_selection.json", "r") as f:
    selection_dict = json.load(f)

lepton_preselection = selection_dict["preselection"]['lepton']
jet_preselection = selection_dict["preselection"]['jet']


preselections = {
    "good_electron": get_lepton_preselection(lepton_preselection, "ele"),
    "good_muon": get_lepton_preselection(lepton_preselection, "mu"),
    "good_tau": get_lepton_preselection(lepton_preselection, "tau"),
    "good_bjet": get_jet_preselection(jet_preselection),
}


for name, preselection in preselections.items():
    df = df.Define(name, preselection)



selections = selection_dict["selection"]


for selection_name, selection_value,  in selections.items():
    #print(selection_value)
    df = df.Filter(selection_value, selection_name)

report = df.Report()
report.Print()
#####################################################################

df = df.Define('good_Electron_pt', 'Electron_pt[good_electron]')


array = ak.from_rdataframe(
        rdf = df,
        columns=(
            "good_Electron_pt",
        ),
    )

plt.hist(array['good_Electron_pt'][:,0])
plt.savefig('Electron_pt.jpg')
