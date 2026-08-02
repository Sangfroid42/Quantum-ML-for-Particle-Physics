import ROOT

ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE)

# ==============================================================================
# 1. SETUP & PROCESSES
# ==============================================================================
inputDir = "outputs/treemaker" 
outputDir = "output_bdt_histograms/"

# This line dynamically injects your C++ code into ROOT
includePaths = ["utils_bdt.h"]

# 1. The master dictionary (must be a string to prevent the join() TypeError)
procDict = "FCCee_procDict_winter2023_IDEA.json"

# 2. Add your custom local processes and their cross-sections to the dictionary
processList = {
    'signal_EDM4hep': {
        'crossSection': 0.004118,
        'numberOfEvents': 100000
    },
    'background_EDM4hep': {
        'crossSection': 0.001135,
        'numberOfEvents': 94804
    }
}

intLumi = 4.1e5 # pb^-1
nCPUS = 1

# ==============================================================================
# 2. ANALYSIS GRAPH
# ==============================================================================
def build_graph(df, dataset):
    hists = []

    # --- BEFORE BDT: book these FIRST on a clean df ---
    df = df.Define("M_4mu",
    "compute_4mu_mass(mu1_pt, mu1_eta, mu1_phi, "
                     "mu2_pt, mu2_eta, mu2_phi, "
                     "mu3_pt, mu3_eta, mu3_phi, "
                     "mu4_pt, mu4_eta, mu4_phi)"
                   )
    hists.append(df.Histo1D(("M_4mu_before",    "", 100, 335, 365), "M_4mu",  "weight"))
    hists.append(df.Histo1D(("M_mumu_all_before","", 100, 0,   300), "dp1_m",  "weight"))
    hists.append(df.Histo1D(("pt_mumu_all_before","",100, 0,   180), "dp1_pt", "weight"))

    print("Event count:", df.Count().GetValue()) 
    print("Columns:", df.GetColumnNames())

    # --- BDT score defined AFTER before-histograms are booked ---
    df = df.Define("bdt_score",
        "get_bdt_score(mu1_pt, mu1_eta, mu1_phi, "
                      "mu2_pt, mu2_eta, mu2_phi, "
                      "mu3_pt, mu3_eta, mu3_phi, "
                      "mu4_pt, mu4_eta, mu4_phi, "
                      "dp1_m, dp1_pt, dp2_m, dp2_pt)"
    )
    df_cut = df.Filter("bdt_score > 0.01")

    hists.append(df_cut.Histo1D(("M_4mu_after",    "", 100, 335, 365), "M_4mu",  "weight"))
    hists.append(df_cut.Histo1D(("M_mumu_all_after","", 100, 0,   300), "dp1_m",  "weight"))
    hists.append(df_cut.Histo1D(("pt_mumu_all_after","",100, 0,   180), "dp1_pt", "weight"))

    return hists, df_cut.Sum("weight")
