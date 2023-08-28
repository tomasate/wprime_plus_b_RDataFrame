from ROOT import RDataFrame
import ROOT
import matplotlib.pyplot as plt
import awkward as ak


from ROOT import gROOT 



redirector = "root://cmsxrootd.fnal.gov/"
file = [
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/270000/58FE9875-8CED-E248-978F-8076F811BBE7.root",
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/280000/23AB22BC-0228-C847-9BB4-59DD4F7238A6.root",
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/280000/48F8F0E4-1117-E943-9FEE-4B2EFBC33FFF.root",
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/280000/89809F2E-C546-C74D-B83E-E846394C0285.root",
        redirector + "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/280000/E876B7D7-3F04-0D4D-9634-07628E317F98.root"
    ]


### Reading the ROOT FIles
names = ROOT.std.vector('string')()
for n in [filename for filename in file]: names.push_back(n)
df = ROOT.RDataFrame("Events", names)


# hiperparameters
channel = "mu"
year = "2017"
year_mod = "" # "APV" or ""
btagger = "btagDeepFlavB"
deepjet_btag_wp = "M" # "L", "M" or "T"

electron_iso_wp = {
    "ele": "Electron_mvaFall17V2Iso_WP80",
    "mu": "Electron_mvaFall17V2Iso_WP90"}

deepjet_btag_wps = {
    "2016APV": {"L": 0.0508, "M": 0.2598, "T": 0.6502},
    "2016": {"L": 0.048, "M": 0.2489, "T": 0.6377},
    "2017": {"L": 0.0532, "M": 0.304, "T": 0.7476},
    "2018": {"L": 0.049, "M": 0.2783, "T": 0.71}}

jet_tagging = {
    "b": f"Jet_{btagger} > {deepjet_btag_wps[year + year_mod][deepjet_btag_wp]}",
    "c": ""}


# preselection for leptons and jets
lepton_preselection = lambda channel: {
    "lepton_pt": {
        "ele": "Electron_pt > 30",
        "mu": "Muon_pt > 30",
        "tau": "Tau_pt > 20",
    },
    "lepton_eta": {
        "ele": "abs(Electron_eta) < 2.5 && abs(Electron_eta) < 1.44 || abs(Electron_eta) > 1.57",
        "mu": "abs(Muon_eta) < 2.4",
        "tau": "abs(Tau_eta) <  2.3",
    },
    "lepton_iso": {
        "ele": "Electron_pfRelIso03_all < 0.25",
        "mu": "Muon_pfRelIso03_all < 0.25",
        "tau": "",
    },
    "lepton_id": {
        "ele": "",
        "mu": "Muon_tightId",
        "tau": "",
    },
    "lepton_iso_wp": {"ele": electron_iso_wp[channel], "mu": "", "tau": ""},
    "lepton_dz": {"ele": "", "mu": "", "tau": "Tau_dz < 0.2"},
    "lepton_idDeepTau2017v2p1VSjet": {
        "ele": "",
        "mu": "",
        "tau": "Tau_idDeepTau2017v2p1VSjet > 8",
    },
    "lepton_idDeepTau2017v2p1VSe": {
        "ele": "",
        "mu": "",
        "tau": "Tau_idDeepTau2017v2p1VSe > 8",
    },
    "lepton_idDeepTau2017v2p1VSmu": {
        "ele": "",
        "mu": "",
        "tau": "Tau_idDeepTau2017v2p1VSmu > 1",
    },
}


jet_preselection = lambda flavour: {
    "jet_pt": "Jet_pt > 20",
    "jet_eta": "abs(Jet_eta) < 2.4",
    "jet_id": "Jet_jetId == 6",
    "jet_puid": "Jet_puId == 7",
    "jet_tagging": jet_tagging[flavour],
}


def get_lepton_preselection(channel: str, flavour: str):
    """
    Return preselection mask string for leptons

    Parameters:
    -----------
        channel: lepton channel {"ele", "mu"}
        flavour: lepton flavour {"ele", "mu", "tau"}
    """
    return " && ".join(
        [
            lep_presel[flavour]
            for lep_presel in lepton_preselection(channel).values()
            if lep_presel[flavour]
        ]
    )


def get_jet_preselection(flavour: str):
    """
    Return preselection mask string for jets

    Parameters:
    -----------
        flavour: jet flavour {"b", "c"}
    """
    return " && ".join(
        [jet_presel for jet_presel in jet_preselection(flavour).values()]
    )


def get_preselection(obj: str, flavour: str, channel: str):
    """
    Return preselection mask string

    Parameters:
    -----------
        obj: object for preselection {"lepton", "jet"}
        flavour: object flavour. If obj is lepton use {"ele", "mu", ""}, otherwise use {"b", "c"}
        channel: lepton channel {"ele", "mu"}
    """
    if obj == "lepton":
        return get_lepton_preselection(channel, flavour)
    else:
        return get_jet_preselection(flavour)



preselections = lambda channel: {
    "good_electron": get_preselection(obj="lepton", flavour="ele", channel=channel),
    "good_muon": get_preselection(obj="lepton", flavour="mu", channel=channel),
    "good_tau": get_preselection(obj="lepton", flavour="tau", channel=channel),
    "good_bjet": get_preselection(obj="jet", flavour="b", channel=channel),
}

#for name, preselection in preselections(channel).items():
#    print(f"{name}: \t", preselection)


for name, preselection in preselections(channel).items():
    df = df.Define(name, preselection)

selections = {
    "ele": [
        "MET_pt > 50",
        "Sum(good_bjet) == 2",
        "Sum(good_tau) == 0",
        "Sum(good_muon) == 0",
        "Sum(good_electron) == 1",
    ],
    "mu": [
        "MET_pt > 50",
        "Sum(good_bjet) == 2",
        "Sum(good_tau) == 0",
        "Sum(good_electron) == 0",
        "Sum(good_muon) == 1",
    ],
}

#for selection in selections[channel]:
#    print(selection)

for selection in selections[channel]:
    #df = df.Filter(selection, name=selection)
    df = df.Filter(selection)


df = df.Define('good_Muon_pt', 'Muon_pt[good_muon]')


array = ak.from_rdataframe(
        rdf = df,
        columns=(
            "good_Muon_pt",
        ),
    )

plt.hist(array['good_Muon_pt'])
plt.savefig('Muon_pt.jpg')
