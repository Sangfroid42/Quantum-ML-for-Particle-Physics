import os
import ROOT

ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE)

# ==============================================================================
# 1. SETUP & PROCESSES
# ==============================================================================
# List of processes and their scaled cross-sections

inputDir = "./"

processList = {
    'signal_EDM4hep': {
        'fraction': 1,
        'crossSection': 0.004118,
    },
    'background_EDM4hep': {
        'fraction': 1,
        'crossSection': 0.001135,
    }
}

# Output directory for the flat ML trees
outputDir = "./outputs/treemaker/"

# Additional C++ functions, defined in header files (optional)
includePaths = ["utils.h"]

# ==============================================================================
# 2. RDF ANALYSIS CLASS
# ==============================================================================
class RDFanalysis:

    # __________________________________________________________
    # Mandatory: analysers function to define the operations on the dataframe
    def analysers(df):
        # Extract ALL muons in the event
        df = df.Alias("Muon0", "Muon_objIdx.index")
        df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
        
        # CUT 0: Require basic minimum momentum (10 GeV)
        df = df.Define("muons", "FCCAnalyses::ReconstructedParticle::sel_p(10)(muons_all)")
        df = df.Define("muons_no", "FCCAnalyses::ReconstructedParticle::get_n(muons)")
        df = df.Define("muons_q", "FCCAnalyses::ReconstructedParticle::get_charge(muons)")
        
        # CUT 1: Require exactly 4 muons and a net charge of 0
        df = df.Filter("muons_no == 4 && Sum(muons_q) == 0")
        
        # Get physical vectors
        df = df.Define("muons_tlv", "FCCAnalyses::ReconstructedParticle::get_tlv(muons)")
        
        # -------------------------------------------------------------------------
        # FEATURE EXTRACTION 1: The 4 Muons (Sorted by pT)
        # -------------------------------------------------------------------------
        sort_code = """
        std::vector<TLorentzVector> sorted_muons;
        for(int i=0; i<4; ++i) { sorted_muons.push_back(muons_tlv[i]); }
        std::sort(sorted_muons.begin(), sorted_muons.end(), [](const TLorentzVector& a, const TLorentzVector& b) {
            return a.Pt() > b.Pt();
        });
        return sorted_muons;
        """
        df = df.Define("sorted_muons", sort_code)
        
        # Extract pT, Eta, Phi for the 12 individual muon features
        for i in range(4):
            df = df.Define(f"mu{i+1}_pt", f"sorted_muons[{i}].Pt()")
            df = df.Define(f"mu{i+1}_eta", f"sorted_muons[{i}].Eta()")
            df = df.Define(f"mu{i+1}_phi", f"sorted_muons[{i}].Phi()")

        # -------------------------------------------------------------------------
        # FEATURE EXTRACTION 2: The 2 Dark Photons (Min Mass Difference)
        # -------------------------------------------------------------------------
        dp_code = """
        std::vector<TLorentzVector> pos_mu, neg_mu;
        for(int i=0; i<4; ++i) {
            if(muons_q[i] > 0) pos_mu.push_back(muons_tlv[i]);
            else neg_mu.push_back(muons_tlv[i]);
        }
        
        // Pairing A: (pos0, neg0) and (pos1, neg1)
        TLorentzVector dpA1 = pos_mu[0] + neg_mu[0];
        TLorentzVector dpA2 = pos_mu[1] + neg_mu[1];
        double diffA = std::abs(dpA1.M() - dpA2.M());
        
        // Pairing B: (pos0, neg1) and (pos1, neg0)
        TLorentzVector dpB1 = pos_mu[0] + neg_mu[1];
        TLorentzVector dpB2 = pos_mu[1] + neg_mu[0];
        double diffB = std::abs(dpB1.M() - dpB2.M());
        
        std::vector<TLorentzVector> final_dps;
        if (diffA < diffB) {
            final_dps = {dpA1, dpA2};
        } else {
            final_dps = {dpB1, dpB2};
        }
        
        // Sort the two Dark Photons by pT for consistency
        if (final_dps[1].Pt() > final_dps[0].Pt()) std::swap(final_dps[0], final_dps[1]);
        return final_dps;
        """
        df = df.Define("dark_photons", dp_code)
        
        # Extract Mass and pT for the 4 dark photon features
        for i in range(2):
            df = df.Define(f"dp{i+1}_m", f"dark_photons[{i}].M()")
            df = df.Define(f"dp{i+1}_pt", f"dark_photons[{i}].Pt()")

        # Add a dummy weight column if needed for ML training downstream
        df = df.Define("weight", "1.0")

        return df

    # __________________________________________________________
    # Mandatory: output function to return the branchlist as a python list
    def output():
        branchList = []
        
        # Add the 12 Muon features
        for i in range(4):
            branchList.append(f"mu{i+1}_pt")
            branchList.append(f"mu{i+1}_eta")
            branchList.append(f"mu{i+1}_phi")
            
        # Add the 4 Dark Photon features
        for i in range(2):
            branchList.append(f"dp{i+1}_m")
            branchList.append(f"dp{i+1}_pt")
            
        # Add weights
        branchList.append("weight")

        return branchList
