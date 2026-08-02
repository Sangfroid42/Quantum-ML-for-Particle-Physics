import os

# Prevent each parallel process from spawning too many internal CPU threads
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np
import joblib
import time

from tqdm import tqdm
from joblib import Parallel, delayed

from load_data import load_data

from qiskit.circuit.library import zz_feature_map
from qiskit.primitives import StatevectorSampler
from qiskit_machine_learning.state_fidelities import ComputeUncompute
from qiskit_machine_learning.kernels import FidelityQuantumKernel

from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

# ============================================================
# CONFIG
# ============================================================

SIG_FILE = "../outputs/treemaker/signal_EDM4hep.root"
BKG_FILE = "../outputs/treemaker/background_EDM4hep.root"

N_QUBITS = 4
MAX_TRAIN = 200
N_REPS = 1

KERNEL_BLOCK_SIZE = 20
N_JOBS = 8

C_VALUE = 1.0
RANDOM_STATE = 42

# ============================================================
# LOAD DATA
# ============================================================

loaded = load_data(
    SIG_FILE,
    BKG_FILE,
    n_components=N_QUBITS,
    max_events=MAX_TRAIN + 200,
)

# This allows the script to work whether load_data returns 6 or 7 values
if len(loaded) == 6:
    X_train, X_test, y_train, y_test, scaler, pca = loaded

    angle_scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
    X_train = angle_scaler.fit_transform(X_train)
    X_test = angle_scaler.transform(X_test)

elif len(loaded) == 7:
    X_train, X_test, y_train, y_test, scaler, pca, angle_scaler = loaded

else:
    raise ValueError(
        f"load_data returned {len(loaded)} values, but expected 6 or 7."
    )

print(f"Training on {len(X_train)} events, testing on {len(X_test)}")
print(f"Signal fraction in train: {np.mean(y_train):.3f}")
print(f"Signal fraction in test : {np.mean(y_test):.3f}")

# ============================================================
# CLASSICAL BASELINE
# ============================================================

print("\nRunning classical RBF SVM baseline...")

rbf = SVC(
    kernel="rbf",
    C=C_VALUE,
    gamma="scale",
    probability=True,
    random_state=RANDOM_STATE,
)

rbf.fit(X_train, y_train)

y_pred_rbf = rbf.predict(X_test)
y_proba_rbf = rbf.predict_proba(X_test)[:, 1]

acc_rbf = accuracy_score(y_test, y_pred_rbf)
auc_rbf = roc_auc_score(y_test, y_proba_rbf)

print("\n" + "=" * 40)
print("  Classical RBF SVM Baseline")
print("=" * 40)
print(f"  Accuracy : {acc_rbf * 100:.2f}%")
print(f"  ROC AUC  : {auc_rbf:.4f}")
print("=" * 40)

# ============================================================
# BUILD QUANTUM KERNEL
# ============================================================

feature_map = zz_feature_map(
    feature_dimension=N_QUBITS,
    reps=N_REPS,
    entanglement="linear",
)

sampler = StatevectorSampler()
fidelity = ComputeUncompute(sampler=sampler)

quantum_kernel = FidelityQuantumKernel(
    feature_map=feature_map,
    fidelity=fidelity,
)

# ============================================================
# PARALLEL BLOCK KERNEL COMPUTATION
# ============================================================

def compute_kernel_blockwise_parallel(
    kernel,
    X_left,
    X_right=None,
    block_size=25,
    symmetric=False,
    n_jobs=4,
):
    """
    Compute a quantum kernel matrix in parallel blocks with tqdm progress.

    For training:
        symmetric=True, X_left=X_train, X_right=X_train

    For testing:
        symmetric=False, X_left=X_test, X_right=X_train
    """

    X_left = np.asarray(X_left)

    if X_right is None:
        X_right = X_left

    X_right = np.asarray(X_right)

    n_left = len(X_left)
    n_right = len(X_right)

    K = np.zeros((n_left, n_right))

    if symmetric:
        block_pairs = []

        for i in range(0, n_left, block_size):
            for j in range(i, n_right, block_size):
                block_pairs.append((i, j))

        def compute_one_block(i, j):
            i_end = min(i + block_size, n_left)
            j_end = min(j + block_size, n_right)

            K_block = kernel.evaluate(
                x_vec=X_left[i:i_end],
                y_vec=X_right[j:j_end],
            )

            return i, i_end, j, j_end, K_block

        results = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(compute_one_block)(i, j)
            for i, j in tqdm(block_pairs, desc="Quantum kernel train blocks")
        )

        for i, i_end, j, j_end, K_block in results:
            K[i:i_end, j:j_end] = K_block

            if i != j:
                K[j:j_end, i:i_end] = K_block.T

    else:
        block_pairs = []

        for i in range(0, n_left, block_size):
            for j in range(0, n_right, block_size):
                block_pairs.append((i, j))

        def compute_one_block(i, j):
            i_end = min(i + block_size, n_left)
            j_end = min(j + block_size, n_right)

            K_block = kernel.evaluate(
                x_vec=X_left[i:i_end],
                y_vec=X_right[j:j_end],
            )

            return i, i_end, j, j_end, K_block

        results = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(compute_one_block)(i, j)
            for i, j in tqdm(block_pairs, desc="Quantum kernel test blocks")
        )

        for i, i_end, j, j_end, K_block in results:
            K[i:i_end, j:j_end] = K_block

    return K

# ============================================================
# COMPUTE QUANTUM KERNEL MATRICES
# ============================================================

print("\nComputing training quantum kernel matrix...")
start = time.time()

K_train = compute_kernel_blockwise_parallel(
    quantum_kernel,
    X_train,
    X_train,
    block_size=KERNEL_BLOCK_SIZE,
    symmetric=True,
    n_jobs=N_JOBS,
)

train_kernel_time = time.time() - start
print(f"Training kernel computed in {train_kernel_time:.2f} s")

print("\nComputing test quantum kernel matrix...")
start = time.time()

K_test = compute_kernel_blockwise_parallel(
    quantum_kernel,
    X_test,
    X_train,
    block_size=KERNEL_BLOCK_SIZE,
    symmetric=False,
    n_jobs=N_JOBS,
)

test_kernel_time = time.time() - start
print(f"Test kernel computed in {test_kernel_time:.2f} s")

# ============================================================
# TRAIN SVM ON PRECOMPUTED QUANTUM KERNEL
# ============================================================

print("\nFitting SVM with precomputed quantum kernel...")

qsvm = SVC(
    kernel="precomputed",
    C=C_VALUE,
    probability=True,
    random_state=RANDOM_STATE,
)

qsvm.fit(K_train, y_train)

# ============================================================
# EVALUATE
# ============================================================

print("\nEvaluating QSVM...")

y_pred = qsvm.predict(K_test)
y_proba = qsvm.predict_proba(K_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)

print("\n" + "=" * 40)
print("  QSVM Results")
print("=" * 40)
print(f"  Accuracy : {acc * 100:.2f}%")
print(f"  ROC AUC  : {auc:.4f}")
print("=" * 40)

print("\nConfusion matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification report:")
print(classification_report(y_test, y_pred, target_names=["background", "signal"]))

# ============================================================
# SAVE MODEL AND PREPROCESSING
# ============================================================

joblib.dump(
    {
        "model": qsvm,
        "scaler": scaler,
        "pca": pca,
        "angle_scaler": angle_scaler,
        "quantum_kernel": quantum_kernel,
        "feature_map": feature_map,
        "X_train_kernel_reference": X_train,
        "K_train": K_train,
        "config": {
            "N_QUBITS": N_QUBITS,
            "MAX_TRAIN": MAX_TRAIN,
            "N_REPS": N_REPS,
            "KERNEL_BLOCK_SIZE": KERNEL_BLOCK_SIZE,
            "N_JOBS": N_JOBS,
            "C_VALUE": C_VALUE,
        },
    },
    "qsvm_model.pkl",
)

print("\nModel saved to qsvm_model.pkl")
