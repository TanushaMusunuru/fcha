"""Evaluation metrics. Classes absent from the test fold are excluded from macro averages and reported."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support


def evaluate(y_true: np.ndarray, y_pred: np.ndarray, classes: List[str],
             benign_class: Optional[str] = None, train_classes: Optional[List[int]] = None,
             min_class_support: int = 0) -> Dict[str, Any]:
    labels = list(range(len(classes)))
    present = [c for c in labels if (y_true == c).any()]
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    out: Dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(np.mean(r[present])) if present else float("nan"),
        "macro_f1": float(np.mean(f[present])) if present else float("nan"),
        "macro_precision": float(np.mean(p[present])) if present else float("nan"),
        "classes_absent_from_test": [classes[c] for c in labels if c not in present],
        "per_class": {classes[c]: {"precision": float(p[c]), "recall": float(r[c]), "f1": float(f[c]),
                                   "support": int(s[c])} for c in labels},
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }
    if train_classes is not None:
        # Host-disjoint folds can hold out every sender of a class; report both views.
        seen = [c for c in present if c in set(train_classes)]
        out["balanced_accuracy_seen_classes"] = float(np.mean(r[seen])) if seen else float("nan")
        out["test_classes_unseen_in_training"] = [classes[c] for c in present if c not in set(train_classes)]
        if min_class_support > 0:
            # Leave-attacker-out folds can hold a handful of flows of a class (one stray flow from a
            # held-out host); a recall over 1-4 flows would weigh as much as a whole class.
            ok = [c for c in seen if s[c] >= min_class_support]
            out["balanced_accuracy_supported"] = float(np.mean(r[ok])) if ok else float("nan")
            out["macro_f1_supported"] = float(np.mean(f[ok])) if ok else float("nan")
            out["classes_supported"] = [classes[c] for c in ok]
    if benign_class is not None and benign_class in classes:
        b = classes.index(benign_class)
        benign, attack = y_true == b, y_true != b
        out["false_positive_rate"] = float((y_pred[benign] != b).mean()) if benign.any() else float("nan")
        out["attack_detection_rate"] = float((y_pred[attack] != b).mean()) if attack.any() else float("nan")
    return out
