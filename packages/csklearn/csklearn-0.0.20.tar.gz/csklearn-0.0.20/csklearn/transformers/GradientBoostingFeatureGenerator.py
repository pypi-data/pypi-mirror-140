import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.multiclass import check_classification_targets
from sklearn.utils.validation import _check_feature_names_in


class GradientBoostingFeatureGenerator(BaseEstimator, TransformerMixin):
    """
    Feature generator from a gradient boosting.

    Gradient boosting decision trees are a powerful and very convenient way to implement non-linear and tuple transformations.
    We treat each individual tree as a categorical feature that takes as value the index of the leaf an instance ends up falling in
    and then perform one hot encoding for these features.

     Parameters
    ----------
    stack_to_X: bool, default = True
        Generates leaves features using the fitted self.gbm and saves them in R.
        If `stack_to_X is True` then `.transform` returns the original features with 'R' appended as columns.
        If `stack_to_X is False` then  `.transform` returns only the leaves features from 'R'

    add_probs: bool, default = False
        If `add_probs is True` then the created features are appended a probability [0,1].
        If `add_probs is False` features are binary



    Example
    -------
    >>> from sktools import GradientBoostingFeatureGenerator
    >>> from sklearn.datasets import make_classification
    >>> X, y = make_classification()
    >>> mf = GradientBoostingFeatureGenerator()
    >>> mf.fit(X, y)
    >>> mf.transform(X)

    References
    ----------

    .. [1] Practical Lessons from Predicting Clicks on Ads at Facebook, from
    https://research.fb.com/wp-content/uploads/2016/11/practical-lessons-from-predicting-clicks-on-ads-at-facebook.pdf

    .. [2] Feature Generation with Gradient Boosted Decision Trees, Towards Data Science, Carlos Mougan
    """

    def __init__(
        self,
        stack_to_X=True,
        add_probs=False,
        regression=False,
        **kwargs,
    ):

        # Deciding whether to append features or simply return generated features
        self.stack_to_X = stack_to_X
        self.add_probs = add_probs
        self.regression = regression
        self.feat_names = None # needed to get_feature_names_out
        self.input_features = None # needed for input features inside pipeline

        if self.regression:
            # Key arguments for the gradient boosting regressor
            self.gbm = GradientBoostingRegressor(**kwargs)

        else:
            # Key arguments for the gradient boosting classifier
            self.gbm = GradientBoostingClassifier(**kwargs)


    def _get_leaves(self, X):
        X_leaves = self.gbm.apply(X)

        # Difference in return methods
        if self.regression:
            n_rows, n_cols = X_leaves.shape
        else:
            n_rows, n_cols, _ = X_leaves.shape

        X_leaves = X_leaves.reshape(n_rows, n_cols)

        return X_leaves


    def _predict_probs(self, X):
        if self.regression == True:
            # Key arguments for the gradient boosting regressor
            return self.gbm.predict(X)
        else:
            # Key arguments for the gradient boosting classifier
            return self.gbm.predict_proba(X)


    def _decode_leaves(self, X):
        return self.encoder.transform(X).todense()


    def fit(self, X, y):

        # Get names if is a pandas dataframe (probably the first step)
        self.input_features = X.columns if isinstance(X, pd.DataFrame) else None

        if self.regression == False:
            # Check that is a classification target
            check_classification_targets(y)

        self.gbm.fit(X, y)
        self.encoder = OneHotEncoder(categories="auto")
        X_leaves = self._get_leaves(X)
        self.encoder.fit(X_leaves)

        # get feature names:
        _ = self.transform(X) # we dont want to return X_new

        return self      


    def transform(self, X):
        """
        L contains the matrix with the encoded leaves. The shape depends upon the parameters.
        P contains a two columns array with the probability.
        """
        L = self._decode_leaves(self._get_leaves(X))
        self.feat_names = ['gbL'+str(i) for i in range(L.shape[1])]
        
        if self.add_probs:
            P = self._predict_probs(X)
            self.feat_names = self.feat_names+\
                                ['gbP'+str(i) for i in range(P.shape[1])]
            L = np.hstack((L, P))
            X_new = np.hstack((X, L)) if self.stack_to_X == True else L
        else:
            X_new = np.hstack((X, L)) if self.stack_to_X == True else L
        return X_new


    def get_feature_names_out(self, input_features=None):
        """Get output feature names for transformation.

        Parameters
        ----------
        input_features : array-like of str or None, default=None
            Input features.

            - If `input_features` is `None`, then `feature_names_in_` is
              used as feature names in. If `feature_names_in_` is not defined,
              then names are generated: `[x0, x1, ..., x(n_features_in_)]`.
            - If `input_features` is an array-like, then `input_features` must
              match `feature_names_in_` if `feature_names_in_` is defined.

        Returns
        -------
        feature_names_out : ndarray of str objects
            Transformed feature names.
        """
        input_features = self.input_features
        if input_features is None:
            input_features = _check_feature_names_in(self, input_features)
        return np.asarray(list(input_features)+self.feat_names, dtype = object)
