#ifndef UTILS_BDT_H
#define UTILS_BDT_H

#include "TMVA/Reader.h"
#include "TLorentzVector.h"

// ==============================================================================
// 1. TMVA BDT READER SETUP
// ==============================================================================

TMVA::Reader* bdt_reader = nullptr;

// Variables must be globally bound in memory for TMVA
float v_mu1_pt, v_mu1_eta, v_mu1_phi;
float v_mu2_pt, v_mu2_eta, v_mu2_phi;
float v_mu3_pt, v_mu3_eta, v_mu3_phi;
float v_mu4_pt, v_mu4_eta, v_mu4_phi;
float v_dp1_m, v_dp1_pt, v_dp2_m, v_dp2_pt;

void init_bdt() {
    if (bdt_reader != nullptr) return;

    bdt_reader = new TMVA::Reader("!Color:!Silent");

    // EXACT same order as training
    bdt_reader->AddVariable("mu1_pt", &v_mu1_pt);
    bdt_reader->AddVariable("mu1_eta", &v_mu1_eta);
    bdt_reader->AddVariable("mu1_phi", &v_mu1_phi);

    bdt_reader->AddVariable("mu2_pt", &v_mu2_pt);
    bdt_reader->AddVariable("mu2_eta", &v_mu2_eta);
    bdt_reader->AddVariable("mu2_phi", &v_mu2_phi);

    bdt_reader->AddVariable("mu3_pt", &v_mu3_pt);
    bdt_reader->AddVariable("mu3_eta", &v_mu3_eta);
    bdt_reader->AddVariable("mu3_phi", &v_mu3_phi);

    bdt_reader->AddVariable("mu4_pt", &v_mu4_pt);
    bdt_reader->AddVariable("mu4_eta", &v_mu4_eta);
    bdt_reader->AddVariable("mu4_phi", &v_mu4_phi);

    bdt_reader->AddVariable("dp1_m", &v_dp1_m);
    bdt_reader->AddVariable("dp1_pt", &v_dp1_pt);
    bdt_reader->AddVariable("dp2_m", &v_dp2_m);
    bdt_reader->AddVariable("dp2_pt", &v_dp2_pt);

    bdt_reader->BookMVA("BDT", "dataset/weights/TMVAClassification_BDT.weights.xml");
}

// Evaluate BDT
float get_bdt_score(float m1pt, float m1eta, float m1phi,
                    float m2pt, float m2eta, float m2phi,
                    float m3pt, float m3eta, float m3phi,
                    float m4pt, float m4eta, float m4phi,
                    float d1m, float d1pt, float d2m, float d2pt) {

    init_bdt();

    v_mu1_pt = m1pt; v_mu1_eta = m1eta; v_mu1_phi = m1phi;
    v_mu2_pt = m2pt; v_mu2_eta = m2eta; v_mu2_phi = m2phi;
    v_mu3_pt = m3pt; v_mu3_eta = m3eta; v_mu3_phi = m3phi;
    v_mu4_pt = m4pt; v_mu4_eta = m4eta; v_mu4_phi = m4phi;

    v_dp1_m = d1m; v_dp1_pt = d1pt;
    v_dp2_m = d2m; v_dp2_pt = d2pt;

    return bdt_reader->EvaluateMVA("BDT");
}

// ==============================================================================
// 2. PHYSICS UTILITIES (for flat ntuples)
// ==============================================================================

// Compute invariant mass of 4 muons
double compute_4mu_mass(
    double pt1, double eta1, double phi1,
    double pt2, double eta2, double phi2,
    double pt3, double eta3, double phi3,
    double pt4, double eta4, double phi4)
{
    const double mu_mass = 0.105; // GeV

    TLorentzVector m1, m2, m3, m4;

    m1.SetPtEtaPhiM(pt1, eta1, phi1, mu_mass);
    m2.SetPtEtaPhiM(pt2, eta2, phi2, mu_mass);
    m3.SetPtEtaPhiM(pt3, eta3, phi3, mu_mass);
    m4.SetPtEtaPhiM(pt4, eta4, phi4, mu_mass);

    return (m1 + m2 + m3 + m4).M();
}

#endif
