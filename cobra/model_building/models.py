import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression


class LogisticRegressionModel:

    """Wrapper around the LogisticRegression class, with additional methods
    implemented such as evaluation (using auc), getting a list of coefficients,
    a ditionary of coefficients per predictor, ... for convenience

    Attributes
    ----------
    logit : LogisticRegression
        scikit-learn logistic regression model
    predictors : list
        List of predictors used in the model
    """

    def __init__(self):
        self.logit = LogisticRegression(fit_intercept=True, C=1e9,
                                        solver='liblinear')
        # placeholder to keep track of a list of predictors
        self.predictors = []
        self._eval_metrics_by_split = {}

    def get_coef(self) -> np.array:
        """Returns the model coefficients

        Returns
        -------
        np.array
            array of model coefficients
        """
        return self.logit.coef_[0]

    def get_intercept(self) -> float:
        """Returns the intercept of the model

        Returns
        -------
        float
            intercept of the model
        """
        return self.logit.intercept_[0]

    def get_coef_by_predictor(self) -> dict:
        """Returns a map predictor -> coefficient

        Returns
        -------
        dict
            map predictor -> coefficient
        """
        return dict(zip(self.predictors, self.logit.coef_[0]))

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Fit the model

        Parameters
        ----------
        X_train : pd.DataFrame
            predictors of train data
        y_train : pd.Series
            target of train data
        """
        self.predictors = list(X_train.columns)
        self.logit.fit(X_train, y_train)

    def score_model(self, X: pd.DataFrame) -> np.ndarray:
        """Score a model on a (new) dataset

        Parameters
        ----------
        X : pd.DataFrame
            dataset of predictors to score the model

        Returns
        -------
        np.ndarray
            score of the model for each observation
        """
        # We select predictor columns (self.predictors) here to
        # ensure we have the proper predictors and the proper order!!!
        return self.logit.predict_proba(X[self.predictors])[:, 1]

    def evaluate(self, X: pd.DataFrame, y: pd.Series,
                 split: str="train") -> float:
        """Evaluate the model on a given split (train, selection, validation)
        of a data set (X, y)

        Parameters
        ----------
        X : pd.DataFrame
            dataset containing the predictor values for each observation
        y : pd.Series
            dataset containig the target of each observation
        split : str, optional
            split of the dataset (e.g. train-selection-validation)

        Returns
        -------
        float
            the performance score of the model (e.g. AUC)
        """
        if self._eval_metrics_by_split.get(split) is None:

            y_pred = self.score_model(X)

            self._eval_metrics_by_split[split] = roc_auc_score(y_true=y,
                                                               y_score=y_pred)
        return self._eval_metrics_by_split[split]
