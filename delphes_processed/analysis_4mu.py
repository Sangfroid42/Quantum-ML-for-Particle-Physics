import ROOT

ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE)

# ==============================================================================
# 1. SETUP & PROCESSES
# ==============================================================================
inputDir = "./" 
outputDir = "output_histograms/"
includePaths = ["utils.h"]
procDict = "FCCee_procDict_winter2023_IDEA.json"

# Scaling Variables
doScale = True
intLumi = 0.41e6 

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

nCPUS = -1

# Define the histogram bins exactly as they appear in the paper
bins_m4mu   = (120, 335, 365)  # 4-muon mass (335 to 365 GeV)
bins_mumu   = (300, 0, 300)    # Di-muon mass (0 to 300 GeV)
bins_ptmumu = (180, 0, 180)    # Di-muon pT (0 to 180 GeV)

# ==============================================================================
# 2. ANALYSIS GRAPH (CUTS & HISTOGRAMS)
# ==============================================================================
def build_graph(df, dataset):
    hists = []
    
    # Extract ALL muons in the event
    df = df.Alias("Muon0", "Muon_objIdx.index")
    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
    
    # CUT 0: Require basic minimum momentum
    df = df.Define("muons", "FCCAnalyses::ReconstructedParticle::sel_p(10)(muons_all)")
    df = df.Define("muons_no", "FCCAnalyses::ReconstructedParticle::get_n(muons)")
    df = df.Define("muons_q", "FCCAnalyses::ReconstructedParticle::get_charge(muons)")
    
    # CUT 1: Require exactly 4 muons and a net charge of 0
    df = df.Filter("muons_no == 4 && Sum(muons_q) == 0")
    
    # Get physical vectors
    df = df.Define("muons_tlv", "FCCAnalyses::ReconstructedParticle::get_tlv(muons)")
    df = df.Define("muons_p", "FCCAnalyses::ReconstructedParticle::get_p(muons)")

    # -------------------------------------------------------------------------
    # 1. Four-Muon System (Top Plot in Paper)
    # -------------------------------------------------------------------------
    df = df.Define("four_muon_tlv", "muons_tlv[0] + muons_tlv[1] + muons_tlv[2] + muons_tlv[3]")
    df = df.Define("M_4mu", "four_muon_tlv.M()")

    # -------------------------------------------------------------------------
    # 2. Opposite-Sign Di-Muon Pairs (Middle & Bottom Plots in Paper)
    # -------------------------------------------------------------------------
    pair_mass_code = """
    ROOT::VecOps::RVec<double> masses;
    for(int i=0; i<4; ++i) {
        for(int j=i+1; j<4; ++j) {
            if(muons_q[i] != muons_q[j]) { // If Opposite Sign
                masses.push_back((muons_tlv[i] + muons_tlv[j]).M());
            }
        }
    }
    return masses;
    """
    
    pair_pt_code = """
    ROOT::VecOps::RVec<double> pts;
    for(int i=0; i<4; ++i) {
        for(int j=i+1; j<4; ++j) {
            if(muons_q[i] != muons_q[j]) { // If Opposite Sign
                pts.push_back((muons_tlv[i] + muons_tlv[j]).Pt());
            }
        }
    }
    return pts;
    """
    
    df = df.Define("M_mumu_all", pair_mass_code)
    df = df.Define("pT_mumu_all", pair_pt_code)
    
    # CREATE HISTOGRAMS
    hists.append(df.Histo1D(("M_4mu", "4-Muon Invariant Mass", *bins_m4mu), "M_4mu"))
    hists.append(df.Histo1D(("M_mumu_all", "Di-Muon Invariant Mass", *bins_mumu), "M_mumu_all"))
    hists.append(df.Histo1D(("pT_mumu_all", "Di-Muon Transverse Momentum", *bins_ptmumu), "pT_mumu_all"))

    df = df.Define("weight", "1.0")
    return hists, df.Sum("weight")
