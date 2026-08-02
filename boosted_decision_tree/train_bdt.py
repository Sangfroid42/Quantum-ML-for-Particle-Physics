import ROOT
import os

# Initialize TMVA
ROOT.TMVA.Tools.Instance()

# Create an output file where TMVA will save the evaluation results and model weights
outFileName = "TMVA_BDT_Output.root"
outputFile = ROOT.TFile.Open(outFileName, "RECREATE")

# Set up the TMVA Factory
# The factory manages the training and testing process
factory = ROOT.TMVA.Factory(
    "TMVAClassification", 
    outputFile,
    "!V:!Silent:Color:DrawProgressBar:Transformations=I:AnalysisType=Classification"
)

# Set up the DataLoader
# The dataloader handles the input variables and the trees
dataloader = ROOT.TMVA.DataLoader("dataset")

# ------------------------------------------------------------------------------
# 1. DEFINE INPUT FEATURES
# ------------------------------------------------------------------------------
# We must register the exact 16 variables we saved in the treemaker script
for i in range(1, 5):
    dataloader.AddVariable(f"mu{i}_pt", "Muon pT", "GeV", "F")
    dataloader.AddVariable(f"mu{i}_eta", "Muon Eta", "", "F")
    dataloader.AddVariable(f"mu{i}_phi", "Muon Phi", "rad", "F")

for i in range(1, 3):
    dataloader.AddVariable(f"dp{i}_m", "Dark Photon Mass", "GeV", "F")
    dataloader.AddVariable(f"dp{i}_pt", "Dark Photon pT", "GeV", "F")

# ------------------------------------------------------------------------------
# 2. LOAD THE DATA
# ------------------------------------------------------------------------------
# Update these paths if your treemaker saved them with slightly different names
sigFile = ROOT.TFile.Open("outputs/treemaker/4mu/signal_EDM4hep.root")
bkgFile = ROOT.TFile.Open("outputs/treemaker/4mu/background_EDM4hep.root")

# Get the trees (FCCAnalyses usually names the output tree 'events')
sigTree = sigFile.Get("events")
bkgTree = bkgFile.Get("events")

# Add trees to the dataloader (weight = 1.0 for standard training)
dataloader.AddSignalTree(sigTree, 1.0)
dataloader.AddBackgroundTree(bkgTree, 1.0)

# Set the variable used for event weights (we saved this in the treemaker)
dataloader.SetWeightExpression("weight")

# ------------------------------------------------------------------------------
# 3. PREPARE TRAINING & TESTING SETS
# ------------------------------------------------------------------------------
# Split the data. For example: 50% for training, 50% for testing, as in paper
cutSig = ROOT.TCut("") 
cutBkg = ROOT.TCut("")
dataloader.PrepareTrainingAndTestTree(
    cutSig, cutBkg,
    "nTrain_Signal=0:nTest_Signal=0:nTrain_Background=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V"
)

# ------------------------------------------------------------------------------
# 4. BOOK THE METHOD & TRAIN
# ------------------------------------------------------------------------------
# Book the BDT. These are standard starting hyperparameters (400 trees, depth 3).
factory.BookMethod(
    dataloader, 
    ROOT.TMVA.Types.kBDT, 
    "BDT",
    "!H:!V:NTrees=400:MinNodeSize=2.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20"
)

# Run the full machine learning cycle
print("Starting BDT Training...")
factory.TrainAllMethods()

print("Starting BDT Testing...")
factory.TestAllMethods()

print("Starting BDT Evaluation...")
factory.EvaluateAllMethods()

outputFile.Close()
print(f"Done! Results saved to {outFileName}")
