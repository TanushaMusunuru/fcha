"""Kaggle entry point for FedFlow.

Attach two inputs to the notebook/script: this repository (uploaded as a Kaggle dataset) and the
NetFlow CSV dataset. Settings come from environment variables, falling back to the YAML config:

    FEDFLOW_CONFIG   config path relative to the repo   (default: configs/fedflow/nf_ton_iot.yaml)
    FEDFLOW_SET      ';'-separated overrides, e.g. "federated.rounds=20;experiment.seeds=[42]"
    FEDFLOW_MODELS   comma-separated model subset        (default: all models in the config)
    FEDFLOW_FOLDS    comma-separated fold indices        (default: config)

Results go to /kaggle/working/<results_dir>; rerunning resumes from results.jsonl.
"""
import glob
import os
import subprocess
import sys
from pathlib import Path


def find_repo() -> Path:
    here = Path(__file__).resolve().parent.parent
    if (here / "fedflow" / "__init__.py").exists():
        return here
    hits = glob.glob("/kaggle/input/**/fedflow/__init__.py", recursive=True)
    if not hits:
        sys.exit("fedflow package not found: attach the repository as a Kaggle dataset.")
    return Path(hits[0]).parent.parent


def main() -> None:
    repo = find_repo()
    for pkg in ("pyyaml", "scikit-learn", "scipy"):
        try:
            __import__({"pyyaml": "yaml", "scikit-learn": "sklearn"}.get(pkg, pkg))
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], check=False)
    sys.path.insert(0, str(repo))
    from fedflow.run import main as run_main

    cfg = os.environ.get("FEDFLOW_CONFIG", "configs/fedflow/nf_ton_iot.yaml")
    args = ["--config", str(repo / cfg)]
    work = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path.cwd()
    from fedflow.config import load_config
    results_dir = load_config(repo / cfg).get("experiment", {}).get("results_dir", "results/fedflow")
    args += ["--set", f"experiment.results_dir={work / results_dir}"]
    for item in filter(None, os.environ.get("FEDFLOW_SET", "").split(";")):
        args += ["--set", item.strip()]
    if os.environ.get("FEDFLOW_MODELS"):
        args += ["--models", os.environ["FEDFLOW_MODELS"]]
    if os.environ.get("FEDFLOW_FOLDS"):
        args += ["--folds", os.environ["FEDFLOW_FOLDS"]]
    run_main(args)


if __name__ == "__main__":
    main()
