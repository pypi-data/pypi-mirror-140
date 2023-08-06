import matplotlib.pyplot as plt
import numpy as np
import sklearn.metrics as skmetrics
from sklearn.utils.multiclass import unique_labels


class ConfusionMatrix:

    def __init__(self, y_true=None, y_pred=None):
        self.y_true_ = y_true
        self.y_pred_ = y_pred
        self.labels_ = None

    @staticmethod
    def unique_labels(*ys):
        return unique_labels(*ys)

    @classmethod
    def from_pred(cls, y_true, y_pred):
        """
        Initialize a new ConfusionMatrix object with the given observations.
        Parameters
        ----------
        y_true : ndarray
            Ground-truth observations.
        y_pred : ndarray
            Predictions.

        Returns
        -------
        cm : ConfusionMatrix
            A new ConfusionMatrix object.
        """
        cm = ConfusionMatrix()
        cm.y_true_ = y_true
        cm.y_pred_ = y_pred
        return cm

    @classmethod
    def from_pred_prob(cls, y_true, y_pred_prob, decision=None):
        """
        Initialize a new ConfusionMatrix object with the given observations.
        Parameters
        ----------
        y_true : ndarray
            Ground-truth observations.
        y_pred_prob : ndarray
            Predicted probabilities.
        decision : func
            A decision function that accepts a row from `y_pred_prob` and returns a prediction value.

        Returns
        -------
        cm : ConfusionMatrix
            A new ConfusionMatrix object.
        """
        if decision is None:
            decision = lambda p: int(p >= 0.5)
        decision = np.vectorize(decision)

        cm = ConfusionMatrix()
        cm.y_true_ = y_true
        cm.y_pred_ = decision(y_pred_prob)
        return cm

    def set_labels(self, labels):
        self.labels_ = labels
        return self

    def _get_array(self, labels=None):
        if self.y_true_ is not None and self.y_pred_ is not None:
            return skmetrics.confusion_matrix(self.y_true_, self.y_pred_, labels=labels)
        else:
            raise ValueError("No y_true or y_pred specified. "
                             "Use ConfusionMatrix.from_pred(y_true, y_pred) as constructor.")

    def _get_binary_array(self):
        try:
            return self._get_array(labels=[1, 0])
        except ValueError as e:
            if str(e) != "At least one label specified must be in y_true": raise e
            else:
                try:
                    return self._get_array(labels=[True, False])
                except ValueError as e:
                    if str(e) != "At least one label specified must be in y_true": raise e
                    else:
                        raise ValueError("Input is not binary. Use (0, 1) or boolean values instead.")

    @property
    def array(self):
        if self.labels_ is None:
            # Try to make sure True Positives are in the upper-left.
            # Otherwise, default to standard sklearn sorted order.
            try:
                return self._get_binary_array()
            except ValueError as e:
                if str(e) != "Input is not binary. Use (0, 1) or boolean values instead.": raise e
                else:
                    return self._get_array()
        else:
            return self._get_array(labels=self.labels_)

    def __repr__(self):
        return repr(self.array)

    @property
    def _values(self):
        """
        Get binary matrix values as a contiguous flattened array.
        Returns
        -------
        y : ndarray
            A 1-D array containing binary matrix values.
        """
        return self._get_binary_array().ravel()

    @property
    def tp(self):
        """
        True positives (TP).
        """
        return self._values[0]

    @property
    def fn(self):
        """
        False negatives (FN).
        """
        return self._values[1]

    @property
    def fp(self):
        """
        False positives (FP).
        """
        return self._values[2]

    @property
    def tn(self):
        """
        True negatives (TN).
        """
        return self._values[3]

    def get_latex_table(self, multirow=True):
        """
        Generate Latex code to insert this confusion matrix as a table.

        Parameters
        ----------
        multirow : bool, default=True
            Whether to use the Latex package `multirow`, which is needed for rotating the left-hand table labels.
            If so, include `usepackage{multirow}` in your Latex preamble.

        Returns
        -------
        code : str
            Latex code to use in your tex file.
        """
        if multirow:
            actual = "\\multirow[c]{2}{*}{\\rotatebox[origin=center]{90}{Actual}}"
        else:
            actual = "{Actual}"

        code = "\\begin{tabular}{cc|cc}\n" \
               "\\multicolumn{2}{c}{} & \\multicolumn{2}{c}{Predicted} \\\\\n" \
               "& & Positive & Negative \\\\\n" \
               "\\cline{2-4}\n" \
               "%(actual)s\n" \
               "& Positive & %(tp)d & %(fn)d \\\\[1ex]\n" \
               "& Negative & %(fp)d & %(tn)d \\\\\n" \
               "\\cline{2-4}\n" \
               "\\end{tabular}" % {'tp': self.tp, 'fn': self.fn, 'fp': self.fp, 'tn': self.tn, 'actual': actual}
        return code

    def plot(self, ax=None, cmap=plt.cm.Blues):
        if self.labels_ is None:
            try:
                return skmetrics.ConfusionMatrixDisplay(self._get_binary_array(), display_labels=[True, False]).plot(ax=ax, cmap=cmap)
            except ValueError: pass
        return skmetrics.ConfusionMatrixDisplay(self.array, display_labels=self.unique_labels(self.y_true_, self.y_pred_)).plot(ax=ax, cmap=cmap)

    def __getattr__(self, name):
        """
        Forward unknown method calls to sklearn.metrics, supplying y_true and y_pred as additional attributes.

        Example
        -------
            self.recall_score(average='micro') -> sklearn.metrics.recall_score(self.y_true_, self.y_pred_, average='micro')
        """
        def _missing(*args, **kwargs):
            method = getattr(skmetrics, name)
            return method(self.y_true_, self.y_pred_, *args, **kwargs)

        return _missing
