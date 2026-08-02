import uproot
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA

FEATURES = [
    "mu1_pt", "mu1_eta", "mu1_phi",
    "mu2_pt", "mu2_eta", "mu2_phi",
    "mu3_pt", "mu3_eta", "mu3_phi",
    "mu4_pt", "mu4_eta", "mu4_phi",
    "dp1_m",  "dp1_pt",
    "dp2_m",  "dp2_pt",
]

def load_data(sig_file, bkg_file, n_components=6, max_events=None, test_size=0.2, random_state=42):
    """
    Load signal and background from flat ROOT ntuples.
    Split first, then fit preprocessing only on the training set.

    Returns:
        X_train, X_test, y_train, y_test, scaler, pca, angle_scaler
    """

    with uproot.open(sig_file) as f:
        sig = f["events"].arrays(FEATURES, library="np")

    with uproot.open(bkg_file) as f:
        bkg = f["events"].arrays(FEATURES, library="np")

    X_sig = np.column_stack([sig[k] for k in FEATURES])
    X_bkg = np.column_stack([bkg[k] for k in FEATURES])

    if max_events is not None:
        X_sig = X_sig[:max_events]
        X_bkg = X_bkg[:max_events]

    X = np.vstack([X_sig, X_bkg])
    y = np.array([1] * len(X_sig) + [0] * len(X_bkg))

    mask = np.all(np.isfinite(X), axis=1)
    X = X[mask]
    y = y[mask]

    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
        shuffle=True,
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_test = scaler.transform(X_test_raw)

    pca = PCA(n_components=n_components, random_state=random_state)
    X_train = pca.fit_transform(X_train)
    X_test = pca.transform(X_test)

    explained = pca.explained_variance_ratio_.sum()
    print(f"PCA variance explained: {100 * explained:.1f}%")

    angle_scaler = MinMaxScaler(feature_range=(-np.pi, np.pi))
    X_train = angle_scaler.fit_transform(X_train)
    X_test = angle_scaler.transform(X_test)

    return X_train, X_test, y_train, y_test, scaler, pca, angle_scaler
