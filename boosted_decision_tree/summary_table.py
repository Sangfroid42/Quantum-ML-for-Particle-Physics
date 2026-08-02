"""
summary_table.py
Reads FCCAnalyses output ROOT files and prints a cut-flow + BDT performance
table matching Table 7 from the paper.

Usage:
    python summary_table.py
"""

import ROOT
import math
import ctypes

ROOT.gROOT.SetBatch(True)

# ==============================================================================
# CONFIG — match these to your analysis_bdt.py and treemaker_4mu.py
# ==============================================================================
inputDir = "output_bdt_histograms/"

signal_file     = inputDir + "signal_EDM4hep.root"
background_file = inputDir + "background_EDM4hep.root"

# Histogram names written by analysis_bdt.py
BEFORE = "M_4mu_before"
AFTER  = "M_4mu_after"

# Raw event counts from your generation and reconstruction steps.
# Set to None to skip rows you don't have yet.
N_generated_sig  = 100000
N_generated_bkg  = 94804
N_reco_sig       = 91639   
N_reco_bkg       = 89057

# BDT cut threshold used in analysis_bdt.py
BDT_CUT = 0.01

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def get_hist(filepath, histname):
    f = ROOT.TFile(filepath, "READ")
    if f.IsZombie():
        raise RuntimeError(f"Cannot open {filepath}")
    h = f.Get(histname)
    if not h:
        raise RuntimeError(f"Histogram '{histname}' not found in {filepath}")
    h.SetDirectory(0)
    f.Close()
    return h

def integral_and_error(h):
    err = ctypes.c_double(0)
    integral = h.IntegralAndError(1, h.GetNbinsX(), err)
    return float(integral), float(err.value)

def get_param(filepath, paramname):
    f = ROOT.TFile(filepath, "READ")
    p = f.Get(paramname)
    val = p.GetVal() if p else None
    f.Close()
    return val

def safe_div(a, b):
    return a / b if b and b != 0 else float('inf')

# ==============================================================================
# READ HISTOGRAMS
# ==============================================================================
print("\nReading histograms from ROOT files...")

h_sig_before = get_hist(signal_file,     BEFORE)
h_bkg_before = get_hist(background_file, BEFORE)
h_sig_after  = get_hist(signal_file,     AFTER)
h_bkg_after  = get_hist(background_file, AFTER)

# Use sumOfWeights for total event counts (avoids histogram range restriction)
sig_before = get_param(signal_file,     "sumOfWeights")
bkg_before = get_param(background_file, "sumOfWeights")

# Scale by BDT efficiency measured from the histogram ratio
sig_eff_fraction = h_sig_after.Integral() / h_sig_before.Integral()
bkg_eff_fraction = h_bkg_after.Integral() / h_bkg_before.Integral()

sig_after = sig_before * sig_eff_fraction
bkg_after = bkg_before * bkg_eff_fraction

intLumi = get_param(signal_file, "intLumi")

# ==============================================================================
# COMPUTE METRICS
# ==============================================================================
SoB_before      = safe_div(sig_before, bkg_before)
SoB_after       = safe_div(sig_after,  bkg_after)
SoB_improvement = safe_div(SoB_after,  SoB_before)

sig_eff       = safe_div(sig_after, sig_before) * 100
bkg_rejection = (1.0 - safe_div(bkg_after, bkg_before)) * 100

det_eff_sig = safe_div(N_reco_sig, N_generated_sig) * 100 if N_reco_sig else None
det_eff_bkg = safe_div(N_reco_bkg, N_generated_bkg) * 100 if N_reco_bkg else None

significance_before = safe_div(sig_before, math.sqrt(sig_before + bkg_before))
significance_after  = safe_div(sig_after,  math.sqrt(sig_after  + bkg_after))

# ==============================================================================
# PRINT TABLE
# ==============================================================================
W  = 56
L  = 34   # label column width
VC =  9   # value column width

def hline(char="-"):
    print(char * W)

def row2(label, sig_val, bkg_val, fmt="{:,.1f}"):
    s = fmt.format(sig_val) if sig_val is not None else "N/A"
    b = fmt.format(bkg_val) if bkg_val is not None else "N/A"
    print(f"  {label:<{L}} {s:>{VC}}  {b:>{VC}}")

def row1(label, val, fmt="{:.2f}"):
    v = fmt.format(val) if val is not None else "N/A"
    print(f"  {label:<{L}} {v:>{VC*2+2}}")

lumi_str = f"{intLumi:.2f} ab^-1" if intLumi else "(check intLumi in config)"

print()
hline("=")
print(f"  BDT Cut-Flow Summary    sqrt(s) = 350 GeV")
print(f"  Luminosity : {lumi_str}")
print(f"  BDT cut    : score > {BDT_CUT}")
hline("=")
print(f"  {'Quantity':<{L}} {'Signal':>{VC}}  {'Background':>{VC}}")
hline()

if N_generated_sig or N_generated_bkg:
    row2("Events generated",
         N_generated_sig, N_generated_bkg, fmt="{:,.0f}")

if N_reco_sig or N_reco_bkg:
    row2("Events reconstructed",
         N_reco_sig, N_reco_bkg, fmt="{:,.0f}")

hline()
row1("BDT cut threshold", BDT_CUT, fmt="{:.3f}")
row2("Events before BDT cut", sig_before, bkg_before, fmt="{:,.1f}")
row2("Events after BDT cut",  sig_after,  bkg_after,  fmt="{:,.1f}")

hline()
row1("S/B before BDT cut",    SoB_before,      fmt="{:.2f}")
row1("S/B after BDT cut",     SoB_after,       fmt="{:.1f}")
row1("S/B improvement",       SoB_improvement, fmt="{:.1f}")

hline()
row1("Signal efficiency after BDT (%)",    sig_eff,       fmt="{:.1f}")
row1("Background rejection after BDT (%)", bkg_rejection, fmt="{:.1f}")
row1("Significance before BDT (S/√S+B)",   significance_before, fmt="{:.2f}")
row1("Significance after BDT  (S/√S+B)",   significance_after,  fmt="{:.2f}")

if det_eff_sig is not None:
    hline()
    row1("Detector efficiency sig (%)", det_eff_sig, fmt="{:.1f}")
    row1("Detector efficiency bkg (%)", det_eff_bkg, fmt="{:.1f}")

hline("=")
print()
