# Quantum Machine Learning for Dark Photon Classification
### Signal vs. Background Classification at the FCC-ee IDEA Detector

## Project Overview
This project explores the application of **Quantum Machine Learning (QML)** in High Energy Physics (HEP). Specifically, it benchmarks a **Quantum Support Vector Machine (QSVM)** against classical **Boosted Decision Trees (BDTs)** and classical SVMs for the classification of Dark Photon signal events versus Standard Model background events, simulated for the proposed FCC-ee IDEA detector. 

The primary goal is to evaluate if quantum kernel state encoding can provide an advantage in identifying rare physics signals amidst large backgrounds, serving as a proof-of-concept for future quantum algorithms in particle physics.

## Technologies & Skills Utilized
- **Quantum Computing & QML:** Qiskit, Quantum Kernels, QSVM, ZZFeatureMap state encoding, Qubit entanglement
- **Classical Machine Learning:** Boosted Decision Trees (ROOT TMVA), Radial Basis Function (RBF) SVM, Principal Component Analysis (PCA)
- **High Energy Physics (HEP) Software:** MadGraph5_aMC@NLO, Delphes (Fast Detector Simulation)
- **Programming & Computing:** Python, C++ (ROOT), High-Performance Computing (Cluster job parallelization)

---

## Project Workflow & Implementation

### 1. Event Generation (MadGraph5)
- Simulated hypothetical Dark Photon signal events ($e^+ e^- \to A' A' \to 4\mu$) at $\sqrt{s} = 350$ GeV and mass $M_{A'} = 150$ GeV.
- Generated Standard Model background events ($e^+ e^- \to 4\mu$).
- Integrated custom physics models using **DarkPhoton UFO (Universal FeynRules Output)**.

### 2. Detector Simulation (Delphes)
- Processed the generated Monte Carlo events through **Delphes** using the **FCC-ee IDEA** detector configuration cards to simulate realistic detector responses (e.g., muon tracking, momentum smearing).
- Reconstructed key kinematic observables such as total mass, dimuon mass, and transverse momentum.

### 3. Classical Baseline: Boosted Decision Trees (ROOT TMVA)
- Engineered a dataset of 16 kinematic variables to train a BDT (400 trees, depth 3).
- Successfully reproduced reference literature results, achieving exceptional separation:
  - **Signal Efficiency:** 99.1%
  - **Background Rejection:** 99.0%
  - **Significance Improvement:** $S/\sqrt{S+B}$ increased from ~296 to ~297.

### 4. Quantum Support Vector Machine (Qiskit)
- Implemented a QSVM using a quantum kernel $K(x_i, x_j) = |\langle\phi(x_i)|\phi(x_j)\rangle|^2$.
- Utilized a **ZZFeatureMap** for data encoding, capturing individual features, pair correlations, and linear entanglement across 4 qubits.
- Addressed computational bottlenecks by applying **PCA** to reduce dimensionality to 4 features and parallelizing quantum circuit execution across computing clusters.

---

## Results & Key Takeaways

| Model | Accuracy | ROC AUC | Notes |
| :--- | :--- | :--- | :--- |
| **BDT (Classical)** | **~99%** | **~0.99** | Serves as the robust, highly-optimized HEP baseline. |
| **RBF SVM (Classical)**| 88.12% | 0.9205 | Trained on the reduced 4-dimensional PCA dataset. |
| **QSVM (Quantum)** | 50.00% | 0.5089 | Trained on the same reduced dataset (160 train / 640 test). |

**Conclusion:** 
While the current iteration of the QSVM was constrained by the high computational cost of simulating quantum state encoding (resulting in 50% accuracy), it successfully established a complete end-to-end pipeline bridging HEP event generation with quantum machine learning. This project highlights the complexities of mapping classical HEP data to quantum Hilbert spaces and lays the groundwork for testing more advanced quantum feature maps as quantum hardware and simulators scale.
