# Tremetrics

[![PyPi](https://img.shields.io/pypi/v/tremetrics)](https://pypi.org/project/tremetrics/)

Tremendous Metrics.

## Installation

You can install Tremetrics from [PyPi](https://pypi.org/project/tremetrics/) using `pip`.

```
pip install tremetrics
```

## Usage

### ConfusionMatrix

```
from tremetrics import ConfusionMatrix

y_true, y_pred = ...                            # Generate predictions
cm = ConfusionMatrix.from_pred(y_true, y_pred)  # Create a new confusion matrix object

print(cm)                                       # Print the confusion matrix
array_for_further_use = cm.array                # Get the matrix as a numpy array
print(cm.tp, cm.fn, cm.fp, cm.tn)               # Get the individual quadrant values

print(cm.get_latex_table(multirow=True))        # Get the matrix as code for a Latex table

print(cm.recall_score(average='micro'))         # Call any sklearn.metrics function using the data in the matrix
```
