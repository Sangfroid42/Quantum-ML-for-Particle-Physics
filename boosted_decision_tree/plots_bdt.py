import ROOT

# global parameters
intLumi        = 1.00 
intLumiLabel   = "L = 0.41 ab^{-1}"
ana_tex        = 'Dark Photon #rightarrow 4#mu'
energy         = 350.0
collider       = 'FCC-ee'
formats        = ['png','pdf']

inputDir       = "output_bdt_histograms/" 
outdir         = "plots_bdt/"

plotStatUnc    = False
leg_position   = [0.8, 0.7, 0.96, 0.88]

procs = {}
procs['signal']      = {'DarkPhoton': ['signal_EDM4hep']}
procs['backgrounds'] = {'Background': ['background_EDM4hep']}

stacksig = ['nostack']

colors = {}
colors['DarkPhoton'] = ROOT.kRed
colors['Background'] = ROOT.kBlack

legend = {}
legend['DarkPhoton'] = 'Signal (4#mu)'
legend['Background'] = 'Background'

hists = {}

# ==============================================================================
# 1. BEFORE BDT CUT (Huge background, needs higher axes/log scale)
# ==============================================================================
hists["M_4mu_before"] = {
    "output":   "M_4mu_before",
    "logy":     True,
    "stack":    False,
    "rebin":    1,
    "xmin":     335,
    "xmax":     365,
    "ymin":     0.5,
    "ymax":     1e6, 
    "xtitle":   "M_{#mu^{+}#mu^{#minus}#mu^{+}#mu^{#minus}} (Before BDT) [GeV]",
    "ytitle":   "Events",
}

hists["M_mumu_all_before"] = {
    "output":   "M_mumu_all_before",
    "logy":     True,   
    "stack":    False,
    "rebin":    1,
    "xmin":     0,
    "xmax":     300,
    "ymin":     0.5,
    "ymax":     1e6,
    "xtitle":   "M_{#mu^{+}#mu^{#minus}} (Before BDT) [GeV]",
    "ytitle":   "Events",
}

hists["pt_mumu_all_before"] = {
    "output":   "pt_mumu_all_before",
    "logy":     True,
    "stack":    False,
    "rebin":    1,
    "xmin":     0,
    "xmax":     180,
    "ymin":     0.5,
    "ymax":     1e6,
    "xtitle":   "p_{T_{#mu^{+}#mu^{#minus}}} (Before BDT) [GeV]",
    "ytitle":   "Events",
}

# ==============================================================================
# 2. AFTER BDT CUT (Background removed, zoomed-in linear scales)
# ==============================================================================
hists["M_4mu_after"] = {
    "output":   "M_4mu_after",
    "logy":     False,
    "stack":    False,
    "rebin":    1,
    "xmin":     335,
    "xmax":     365,
    "ymin":     0,
    "ymax":     400, 
    "xtitle":   "M_{#mu^{+}#mu^{#minus}#mu^{+}#mu^{#minus}} (After BDT) [GeV]",
    "ytitle":   "Events",
}

hists["M_mumu_all_after"] = {
    "output":   "M_mumu_all_after",
    "logy":     True,   
    "stack":    False,
    "rebin":    1,
    "xmin":     0,
    "xmax":     300,
    "ymin":     0.5,
    "ymax":     1e5,
    "xtitle":   "M_{#mu^{+}#mu^{#minus}} (After BDT) [GeV]",
    "ytitle":   "Events",
}

hists["pt_mumu_all_after"] = {
    "output":   "pt_mumu_all_after",
    "logy":     False,
    "stack":    False,
    "rebin":    1,
    "xmin":     0,
    "xmax":     180,
    "ymin":     0,
    "ymax":     350,
    "xtitle":   "p_{T_{#mu^{+}#mu^{#minus}}} (After BDT) [GeV]",
    "ytitle":   "Events",
}
