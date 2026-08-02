import ROOT
f = ROOT.TFile("output_bdt_histograms/signal_EDM4hep.root")
f.ls()  # see what's actually stored

for name in ["M_4mu_before", "M_mumu_all_before", "pt_mumu_all_before",
             "M_4mu_after",  "M_mumu_all_after",  "pt_mumu_all_after"]:
    h = f.Get(name)
    if h:
        print(f"{name}: {h.GetEntries()} entries, integral={h.Integral()}")
    else:
        print(f"{name}: NOT FOUND in file")
