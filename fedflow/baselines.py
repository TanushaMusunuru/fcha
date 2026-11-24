"""Centralised flow-feature baselines (reference points; they see pooled training data)."""
from __future__ import annotations

from typing import Any, Dict

import numpy as np


def fit_predict_classical(mcfg: Dict[str, Any], X_tr: np.ndarray, y_tr: np.ndarray, X_te: np.ndarray,
                          seed: int) -> np.ndarray:
    est = mcfg.get("estimator", "random_forest")
    params = dict(mcfg.get("params", {}) or {})
    if est == "random_forest":
        from sklearn.ensemble import RandomForestClassifier
        params.setdefault("n_estimators", 200)
        params.setdefault("n_jobs", -1)
        params.setdefault("class_weight", "balanced")
        model = RandomForestClassifier(random_state=seed, **params)
    elif est == "hist_gradient_boosting":
        from sklearn.ensemble import HistGradientBoostingClassifier
        params.setdefault("class_weight", "balanced")
        model = HistGradientBoostingClassifier(random_state=seed, **params)
    elif est == "xgboost":
        try:
            from xgboost import XGBClassifier
        except ImportError as exc:
            raise ImportError("estimator 'xgboost' needs the xgboost package (pip install xgboost)") from exc
        params.setdefault("n_estimators", 300)
        params.setdefault("tree_method", "hist")
        model = XGBClassifier(random_state=seed, **params)
        # XGBoost needs contiguous labels 0..k-1.
        uniq, y_enc = np.unique(y_tr, return_inverse=True)
        model.fit(X_tr, y_enc)
        return uniq[model.predict(X_te).astype(int)]
    elif est == "logistic_regression":
        from sklearn.linear_model import LogisticRegression
        params.setdefault("max_iter", 1000)
        params.setdefault("class_weight", "balanced")
        model = LogisticRegression(random_state=seed, **params)
    else:
        raise ValueError(f"Unknown classical estimator {est!r}")
    model.fit(X_tr, y_tr)
    return model.predict(X_te)
