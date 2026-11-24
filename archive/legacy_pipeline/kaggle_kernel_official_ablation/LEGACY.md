# Legacy scripts

These scripts produced the numbers in the current paper draft. The original version used the
class label (`label_idx`) as an input feature: on random-noise data it reached 93% balanced
accuracy. The scripts have been patched (label excluded, train-statistics normalisation,
interpolation fixes) but are kept for reference only.

Use the `fedflow` package instead (see `FEDFLOW.md` at the repository root).
