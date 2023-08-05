"""Class to represent probability estimates, thus predictions that do not
directly return fitted values but that can be converted to such. It can be
viewed as the step before BinaryPrediction.

It allows to compute AUC score and other metrics that depend on the convertion
threshold as arrays."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from easypred import BinaryPrediction
from easypred.utils import check_lengths_match, lists_to_nparray, other_value

if TYPE_CHECKING:
    from easypred.type_aliases import BinaryMetricFunction, Vector, VectorPdNp


class BinaryScore:
    """Class to represent a prediction in terms of probability estimates, thus
    having each observation paired with a score between 0 and 1 representing
    the likelihood of being the "positive value".

    Attributes
    -------
    computation_decimals: int
        The number of decimal places to be considered when rounding probability
        scores to obtain the unique values.
    fitted_scores: np.ndarray | pd.Series
        The array-like object of length N containing the probability scores.
    real_values: np.ndarray | pd.Series
        The array-like object containing the N real values.
    value_positive: Any
        The value in the data that corresponds to 1 in the boolean logic.
        It is generally associated with the idea of "positive" or being in
        the "treatment" group. By default is 1.

    Examples
    -------
    >>> from easypred import BinaryScore
    >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
    ...                     [0.31, 0.44, 0.24, 0.28, 0.37, 0.18],
    ...                     value_positive=1)
    >>> score.real_values
    array([0, 1, 1, 0, 1, 0])
    >>> score.fitted_scores
    array([0.31, 0.44, 0.24, 0.28, 0.37, 0.18])
    >>> score.value_positive
    1
    >>> score.computation_decimals
    3
    """

    def __init__(
        self,
        real_values: Vector,
        fitted_scores: Vector,
        value_positive: Any = 1,
    ):
        """Create a BinaryScore object to represent a prediction in terms of
        probability estimates.

        Arguments
        -------
        real_values: np.ndarray | pd.Series | list | tuple
            The array-like object containing the real values. If not pd.Series
            or np.array, it will be coerced into np.array.
        fitted_scores: np.ndarray | pd.Series | list | tuple
            The array-like object of length N containing the probability scores.
            It must have the same length as real_values. If not pd.Series or
            np.array, it will be coerced into np.array.
        value_positive: Any
            The value in the data that corresponds to 1 in the boolean logic.
            It is generally associated with the idea of "positive" or being in
            the "treatment" group. By default is 1.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> BinaryScore([0, 1, 1, 0, 1, 0], [0.31, 0.44, 0.24, 0.28, 0.37, 0.18])
        <easypred.binary_score.BinaryScore object at 0x000001E8AD923430>
        """
        self.real_values, self.fitted_scores = lists_to_nparray(
            real_values, fitted_scores
        )
        self.value_positive = value_positive
        self.computation_decimals = 3

        # Processing appening at __init__
        check_lengths_match(
            self.real_values, self.fitted_scores, "Real values", "Fitted scores"
        )

    def __str__(self):
        return self.fitted_scores.__str__()

    def __len__(self):
        return len(self.fitted_scores)

    def __eq__(self, other):
        return np.all(self.fitted_scores == other.fitted_scores)

    def __ne__(self, other):
        return np.any(self.fitted_scores != other.fitted_scores)

    @property
    def value_negative(self) -> Any:
        """Return the value that it is not the positive value.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.24, 0.28, 0.37, 0.18],
        ...                     value_positive=1)
        >>> score.value_negative
        0
        """
        return other_value(self.real_values, self.value_positive)

    @property
    def unique_scores(self) -> VectorPdNp:
        """Return the unique values attained by the fitted scores, sorted in
        ascending order

        Returns
        -------
        np.ndarray | pd.Series
            The array containing the sorted unique values. Its type matches
            fitted_scores' type.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.24, 0.28, 0.37, 0.24],
        ...                     value_positive=1)
        >>> score.unique_scores
        array([0.24, 0.28, 0.31, 0.37, 0.44])
        """
        scores = np.unique(self.fitted_scores.round(self.computation_decimals))

        if isinstance(self.fitted_scores, pd.Series):
            return pd.Series(scores)

        return scores

    def score_to_values(self, threshold: float = 0.5) -> VectorPdNp:
        """Return an array contained fitted values derived on the basis of the
        provided threshold.

        Parameters
        ----------
        threshold : float, optional
            The minimum value such that the score is translated into
            value_positive. Any score below the threshold is instead associated
            with the other value. By default 0.5.

        Returns
        -------
        np.ndarray | pd.Series
            The array containing the inferred fitted values. Its type matches
            fitted_scores' type.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.24, 0.28, 0.37, 0.24],
        ...                     value_positive=1)
        >>> score.score_to_values(threshold=0.6)
        array([0, 0, 0, 0, 0, 0])
        >>> score.score_to_values(threshold=0.31)
        array([1, 1, 0, 0, 1, 0])
        """
        return np.where(
            (self.fitted_scores >= threshold),
            self.value_positive,
            self.value_negative,
        )

    @property
    def auc_score(self) -> float:
        """Return the Area Under the Receiver Operating Characteristic Curve
        (ROC AUC).

        It is computed using pairs properties as:  (Nc - 0.5 * Nt) / Ntot.
        Where Nc is the number of concordant pairs, Ntot is the number of tied
        pairs and Ntot is the total number of pairs.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.24, 0.28, 0.37, 0.24],
        ...                     value_positive=1)
        >>> score.auc_score
        0.7222222222222222
        """
        concordant_pairs = self.pairs_count().loc["Concordant", "Count"]
        tied_pairs = self.pairs_count().loc["Tied", "Count"]
        total_pairs = self.pairs_count().loc["Total", "Count"]
        return (concordant_pairs - 0.5 * tied_pairs) / total_pairs

    @property
    def accuracy_scores(self) -> np.ndarray:
        """Return an array containing the accuracy scores calculated setting the
        threshold for each unique score value.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.244, 0.28, 0.37, 0.241],
        ...                     value_positive=1)
        >>> score.accuracy_scores
        array([0.5       , 0.66666667, 0.5       , 0.66666667, 0.83333333,
               0.66666667])

        Note that the length of the array changes if the number of decimals
        used in the computation of unique values is lowered to 2. This is
        because 0.241 and 0.244 establish a unique threshold equal to 0.24.

        >>> score.computation_decimals = 2
        >>> score.accuracy_scores
        array([0.5       , 0.5       , 0.66666667, 0.83333333, 0.66666667])
        """
        from easypred.metrics import accuracy_score

        return self._metric_array(accuracy_score)

    @property
    def false_positive_rates(self) -> np.ndarray:
        """Return an array containing the false positive rates calculated
        setting the threshold for each unique score value.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.244, 0.28, 0.37, 0.241],
        ...                     value_positive=1)
        >>> score.false_positive_rates
        array([1.        , 0.66666667, 0.66666667, 0.33333333, 0.        ,
               0.        ])

        Note that the length of the array changes if the number of decimals
        used in the computation of unique values is lowered to 2. This is
        because 0.241 and 0.244 establish a unique threshold equal to 0.24.

        >>> score.computation_decimals = 2
        >>> score.false_positive_rates
        array([1.        , 0.66666667, 0.33333333, 0.        , 0.        ])
        """
        from easypred.metrics import false_positive_rate

        return self._metric_array(
            false_positive_rate, value_positive=self.value_positive
        )

    @property
    def recall_scores(self) -> np.ndarray:
        """Return an array containing the recall scores calculated setting the
        threshold for each unique score value.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.244, 0.28, 0.37, 0.241],
        ...                     value_positive=1)
        >>> score.recall_scores
        array([1.        , 1.        , 0.66666667, 0.66666667, 0.66666667,
               0.33333333])

        Note that the length of the array changes if the number of decimals
        used in the computation of unique values is lowered to 2. This is
        because 0.241 and 0.244 establish a unique threshold equal to 0.24.

        >>> score.computation_decimals = 2
        >>> score.recall_scores
        array([1.        , 0.66666667, 0.66666667, 0.66666667, 0.33333333])
        """
        from easypred.metrics import recall_score

        return self._metric_array(recall_score, value_positive=self.value_positive)

    @property
    def f1_scores(self) -> np.ndarray:
        """Return an array containing the f1 scores calculated setting the
        threshold for each unique score value.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.244, 0.28, 0.37, 0.241],
        ...                     value_positive=1)
        >>> score.f1_scores
        array([0.66666667, 0.75      , 0.57142857, 0.66666667, 0.8       ,
               0.5       ])

        Note that the length of the array changes if the number of decimals
        used in the computation of unique values is lowered to 2. This is
        because 0.241 and 0.244 establish a unique threshold equal to 0.24.

        >>> score.computation_decimals = 2
        >>> score.f1_scores
        array([0.66666667, 0.57142857, 0.66666667, 0.8       , 0.5       ])
        """
        from easypred.metrics import f1_score

        return self._metric_array(f1_score, value_positive=self.value_positive)

    def _metric_array(
        self, metric_function: BinaryMetricFunction, **kwargs
    ) -> np.ndarray:
        """Return an array containing the passed metric calculated setting the
        threshold for each unique score value.

        Parameters
        ----------
        metric_function : Callable(VectorPdNp, VectorPdNp, ...) -> float
            The function that calculates the metric.
        **kwargs : Any
            Arguments to be directly passed to metric_function.

        Returns
        -------
        np.ndarray
            The array containing the metrics calculated for each threshold.
        """
        return np.array(
            [
                metric_function(self.real_values, self.score_to_values(val), **kwargs)
                for val in self.unique_scores
            ]
        )

    def best_threshold(self, criterion="f1") -> float:
        """Return the threshold to convert scores into values that performs the
        best given a specified criterion.

        Parameters
        ----------
        criterion : str, optional
            The value to be maximized by the threshold. It defaults to "f1",
            the options are:
            - "f1": maximize the f1 score
            - "accuracy": maximize the accuracy score

        Returns
        -------
        float
            The threshold that maximizes the indicator specified.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.244, 0.28, 0.37, 0.241],
        ...                     value_positive=1)
        >>> score.best_threshold(criterion="f1")
        0.37
        """
        if criterion == "f1":
            numb = np.argmax(self.f1_scores)
        elif criterion == "accuracy":
            numb = np.argmax(self.accuracy_scores)
        else:
            raise ValueError(
                f"Unrecognized criterion: {criterion}. Allowed "
                "criteria are 'f1', 'accuracy'."
            )

        return self.unique_scores[numb]

    def pairs_count(self, relative: bool = False) -> pd.DataFrame:
        """Return a dataframe containing the count of concordant,
        discordant, tied and total pairs.

        Parameters
        ----------
        relative : bool, optional
            If True, return the relative percentage for the three types of pairs
            instead that the absolute count. By default is False.

        Returns
        -------
        pd.DataFrame
            A dataframe of shape (3, 1) containing in one column the information
            about concordant, discordant and tied pairs.

        Examples
        -------
        >>> real = [1, 0, 0, 1, 0]
        >>> fit = [0.81, 0.31, 0.81, 0.73, 0.45]
        >>> from easypred import BinaryScore
        >>> score = BinaryScore(real, fit, value_positive=1)
        >>> score.pairs_count()
                    Count
        Concordant      4
        Discordant      1
        Tied            1
        Total           6
        >>> score.pairs_count(relative=True)
                    Percentage
        Concordant    0.666667
        Discordant    0.166667
        Tied          0.166667
        Total              1.0
        """
        measures = np.array([0, 0, 0, 0])

        positive_only = self.real_values == self.value_positive

        for score_one in self.fitted_scores[positive_only]:
            # Concordant
            measures[0] += (self.fitted_scores[~positive_only] < score_one).sum()
            # Discordant
            measures[1] += (self.fitted_scores[~positive_only] > score_one).sum()
            # Tied
            measures[2] += (self.fitted_scores[~positive_only] == score_one).sum()

        column = "Count"
        total_pairs = positive_only.sum() * (~positive_only).sum()
        measures[3] = total_pairs

        if relative:
            measures = measures / total_pairs
            column = "Percentage"

        return pd.DataFrame(
            {column: measures},
            index=["Concordant", "Discordant", "Tied", "Total"],
        )

    @property
    def somersd_score(self) -> float:
        """Return the Somer's D score, computed as the difference between the
        number of concordant and discordant pairs, divided by the total number
        of pairs.

        Also called: Gini coefficient.

        Returns
        -------
        float
            Somer's D score.

        References
        -------
        https://en.wikipedia.org/wiki/Somers%27_D#Somers'_D_for_binary_dependent_variables
        """
        concordant_pairs = self.pairs_count().loc["Concordant", "Count"]
        discordant_pairs = self.pairs_count().loc["Discordant", "Count"]
        total_pairs = self.pairs_count().loc["Total", "Count"]
        return (concordant_pairs - discordant_pairs) / total_pairs

    @property
    def goodmankruskagamma_score(self) -> float:
        """Return the Goodman and Kruskal's gamma, computed as the ratio between
        the difference and the sum of the number of concordant and discordant
        pairs.

        Returns
        -------
        float
            Goodman and Kruskal's gamma.

        References
        -------
        https://en.wikipedia.org/wiki/Goodman_and_Kruskal%27s_gamma
        """
        concordant_pairs = self.pairs_count().loc["Concordant", "Count"]
        discordant_pairs = self.pairs_count().loc["Discordant", "Count"]
        return (concordant_pairs - discordant_pairs) / (
            concordant_pairs + discordant_pairs
        )

    @property
    def kendalltau_score(self) -> float:
        """Return the Kendall tau-a, computed as the difference between the
        number of concordant and discordant pairs, divided by the number of
        combinations of pairs.

        Returns
        -------
        float
            Kendall tau-a.

        References
        -------
        https://en.wikipedia.org/wiki/Kendall_rank_correlation_coefficient#Tau-a
        """
        concordant_pairs = self.pairs_count().loc["Concordant", "Count"]
        discordant_pairs = self.pairs_count().loc["Discordant", "Count"]
        return (concordant_pairs - discordant_pairs) / (
            0.5 * len(self) * (len(self) - 1)
        )

    @property
    def c_score(self) -> float:
        """Return the Kendall tau-a, computed as the difference between the
        number of concordant and discordant pairs, divided by the number of
        combinations of pairs.

        Returns
        -------
        float
            Kendall tau-a.

        References
        -------
        https://en.wikipedia.org/wiki/Kendall_rank_correlation_coefficient#Tau-a
        """
        concordant_pairs = self.pairs_count().loc["Concordant", "Count"]
        discordant_pairs = self.pairs_count().loc["Discordant", "Count"]
        return (concordant_pairs - discordant_pairs) / (
            0.5 * len(self) * (len(self) - 1)
        )

    def to_binary_prediction(self, threshold: float | str = 0.5) -> BinaryPrediction:
        """Create an instance of BinaryPrediction from the BinaryScore object.

        Parameters
        ----------
        threshold : float | str, optional
            If float, it is the minimum value such that the score is translated
            into value_positive. Any score below the threshold is instead
            associated with the other value.
            If str, the threshold is automatically set such that it maximizes
            the metric corresponding to the provided keyword. The available
            keywords are:
            - "f1": maximize the f1 score
            - "accuracy": maximize the accuracy score

            By default 0.5.

        Returns
        -------
        BinaryPrediction
            An object of type BinaryPrediction, a subclass of Prediction
            specific for predictions with just two outcomes. The class instance
            is given the special attribute "threshold" that returns the
            threshold used in the convertion.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.244, 0.28, 0.37, 0.241],
        ...                     value_positive=1)
        >>> score.to_binary_prediction(threshold=0.37)
        <easypred.binary_prediction.BinaryPrediction object at 0x000001E8C813FAF0>
        """
        if isinstance(threshold, str):
            threshold = self.best_threshold(criterion=threshold)
        binpred = BinaryPrediction(
            real_values=self.real_values,
            fitted_values=self.score_to_values(threshold=threshold),
            value_positive=self.value_positive,
        )
        binpred.threshold = threshold
        return binpred

    def describe(self) -> pd.DataFrame:
        """Return a dataframe containing some key information about the
        prediction.

        Examples
        -------
        >>> real = [0, 1, 1, 0, 1, 0]
        >>> fit = [0.31, 0.44, 0.24, 0.28, 0.37, 0.18]
        >>> from easypred import BinaryScore
        >>> score = BinaryScore(real, fit, value_positive=1)
        >>> score.describe()
                                Value
        N                    6.000000
        Max fitted score     0.440000
        AUC score            0.777778
        Max accuracy         0.833333
        Thresh max accuracy  0.370000
        Max F1 score         0.800000
        Thresh max F1 score  0.370000
        """
        return pd.DataFrame(
            {
                "N": [len(self)],
                "Max fitted score": [self.fitted_scores.max()],
                "AUC score": [self.auc_score],
                "Max accuracy": [self.accuracy_scores.max()],
                "Thresh max accuracy": [self.best_threshold(criterion="accuracy")],
                "Max F1 score": [self.f1_scores.max()],
                "Thresh max F1 score": [self.best_threshold(criterion="f1")],
            },
            index=["Value"],
        ).transpose()

    def plot_roc_curve(
        self,
        figsize: tuple[int, int] = (20, 10),
        plot_baseline: bool = True,
        show_legend: bool = True,
        title_size: int = 14,
        axes_labels_size: int = 12,
        ax: Axes | None = None,
        **kwargs,
    ) -> Axes:
        """Plot the ROC curve for the score. This curve depicts the True
        Positive Rate (Recall score) against the False Positive Rate.

        Parameters
        ----------
        figsize : tuple[int, int], optional
            Tuple of integers specifying the size of the plot. Default is
            (20, 10).
        plot_baseline : bool, optional
            If True, a reference straight line with slope 1 is added to the
            plot, representing the performance of a random classifier. By
            default is True.
        title_size : int, optional
            Font size of the plot title. Default is 14.
        axes_labels_size : int, optional
            Font size of the axes labels. Default is 12.
        ax : matplotlib Axes, optional
            Axes object to draw the plot onto, otherwise creates new Figure
            and Axes. Use this option to further customize the plot.
        kwargs : key, value mappings
            Other keyword arguments tp be passed through to
            matplotlib.pyplot.plot().

        Returns
        -------
        matplotlib Axes
            Matplotlib Axes object with the plot drawn on it.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.244, 0.28, 0.37, 0.241],
        ...                     value_positive=1)
        >>> score.plot_roc_curve()
        <AxesSubplot:title={'center':'ROC Curve'},
        xlabel='False Positive Rate', ylabel='True Positive Rate'>
        >>> from matplotlib import pyplot as plt
        >>> plt.show()
        """
        if ax is None:
            _, ax = plt.subplots(figsize=figsize)

        ax.plot(self.false_positive_rates, self.recall_scores, label="Model", **kwargs)

        if plot_baseline:
            ax.plot((0, 1), (0, 1), c="red", ls="--", label="Random classifier")

        ax.set_title("ROC Curve", fontsize=title_size)
        ax.set_xlabel("False Positive Rate", fontsize=axes_labels_size)
        ax.set_ylabel("True Positive Rate", fontsize=axes_labels_size)

        ax.grid(True, ls="--")
        if show_legend:
            ax.legend(fontsize=axes_labels_size)

        return ax

    def plot_score_histogram(
        self,
        figsize: tuple[int, int] = (20, 10),
        title_size: int = 14,
        axes_labels_size: int = 12,
        ax: Axes | None = None,
        **kwargs,
    ) -> Axes:
        """Plot the histogram of the probability scores.

        Parameters
        ----------
        figsize : tuple[int, int], optional
            Tuple of integers specifying the size of the plot. Default is
            (20, 10).
        title_size : int, optional
            Font size of the plot title. Default is 14.
        axes_labels_size : int, optional
            Font size of the axes labels. Default is 12.
        ax : matplotlib Axes, optional
            Axes object to draw the plot onto, otherwise creates new Figure
            and Axes. Use this option to further customize the plot.
        kwargs : key, value mappings
            Other keyword arguments tp be passed through to
            matplotlib.pyplot.hist().

        Returns
        -------
        matplotlib Axes
            Matplotlib Axes object with the plot drawn on it.

        Examples
        -------
        >>> from easypred import BinaryScore
        >>> score = BinaryScore([0, 1, 1, 0, 1, 0],
        ...                     [0.31, 0.44, 0.244, 0.28, 0.37, 0.241],
        ...                     value_positive=1)
        >>> score.plot_score_histogram()
        <AxesSubplot:title={'center':'Fitted Scores Distribution'},
        xlabel='Fitted Scores', ylabel='Frequency'>
        >>> from matplotlib import pyplot as plt
        >>> plt.show()

        Passing keyword arguments to matplotlib's hist function:

        >>> score.plot_score_histogram(bins=10)
        <AxesSubplot:title={'center':'Fitted Scores Distribution'},
        xlabel='Fitted Scores', ylabel='Frequency'>
        """
        if ax is None:
            _, ax = plt.subplots(figsize=figsize)

        ax.hist(self.fitted_scores, **kwargs)

        ax.set_title("Fitted Scores Distribution", fontsize=title_size)
        ax.set_xlabel("Fitted Scores", fontsize=axes_labels_size)
        ax.set_ylabel("Frequency", fontsize=axes_labels_size)

        ax.grid(True, ls="--")

        return ax

    def plot_metric(
        self,
        metric: BinaryMetricFunction | list[BinaryMetricFunction],
        figsize: tuple[int, int] = (20, 10),
        show_legend: bool = True,
        title_size: int = 14,
        axes_labels_size: int = 12,
        ax: Axes | None = None,
        **kwargs,
    ) -> Axes:
        """Plot the variation for one or more metrics given different values
        for the threshold telling "1s" from "0s".

        Parameters
        ----------
        metric : Metric function | list[Metric functions]
            A function from easypred.metrics or a list of such functions. It
            defines which values are to be plotted.
        figsize : tuple[int, int], optional
            Tuple of integers specifying the size of the plot. Default is
            (20, 10).
        show_legend : bool, optional
            If True, show the plot's legend. By default is True.
        title_size : int, optional
            Font size of the plot title. Default is 14.
        axes_labels_size : int, optional
            Font size of the axes labels. Default is 12.
        ax : matplotlib Axes, optional
            Axes object to draw the plot onto, otherwise creates new Figure
            and Axes. Use this option to further customize the plot.
        kwargs : key, value mappings
            Other keyword arguments tp be passed through to
            matplotlib.pyplot.hist().

        Returns
        -------
        matplotlib Axes
            Matplotlib Axes object with the plot drawn on it.

        Examples
        -------
        With one metric

        >>> real = [0, 1, 1, 0, 1, 0]
        >>> fit = [0.31, 0.44, 0.73, 0.28, 0.37, 0.18]
        >>> from easypred import BinaryScore
        >>> score = BinaryScore(real, fit, value_positive=1)
        >>> from easypred.metrics import accuracy_score
        >>> score.plot_metric(metric=accuracy_score)
        <AxesSubplot:title={'center':'accuracy_score given different thresholds'},
        xlabel='Threshold', ylabel='Metric value'>
        >>> from matplotlib import pyplot as plt
        >>> plt.show()

        Adding a second metric

        >>> from easypred.metrics import f1_score
        >>> score.plot_metrics(metric=[accuracy_score, f1_score])
        <AxesSubplot:title={'center':'accuracy_score & f1_score given different thresholds'},
        xlabel='Threshold', ylabel='Metric value'>
        >>> plt.show()
        """
        if ax is None:
            _, ax = plt.subplots(figsize=figsize)

        if not isinstance(metric, list):
            metric = [metric]
        for met in metric:
            metric_values = self._metric_array(met, value_positive=self.value_positive)
            ax.plot(
                self.unique_scores,
                metric_values,
                label=met.__name__,
                **kwargs,
            )

        names = " & ".join([x.__name__ for x in metric])
        ax.set_title(f"{names} given different thresholds", fontsize=title_size)
        ax.set_xlabel("Threshold", fontsize=axes_labels_size)
        ax.set_ylabel("Metric value", fontsize=axes_labels_size)

        ax.grid(True, ls="--")
        if show_legend:
            ax.legend(fontsize=axes_labels_size)

        return ax
