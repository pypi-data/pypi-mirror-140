import scipy
from sklearn.base import *
from sklearn.preprocessing import *


class as_str(BaseEstimator, TransformerMixin):
    """
    Transform X into string.
    """

    def fit(self, X, y=None, **kwargs):
        """Dummy fit function that does nothing particular."""
        return self

    def transform(self, X, y=None, **kwargs):
        """Convert input column X as string type

        Args:
            X ([type]): [description]
            y ([type], optional): Do nothing. Defaults to None.

        Returns:
            [type]: [description]
        """
        return X.astype(str)


class as_np(BaseEstimator, TransformerMixin):
    """
    Transform X to numpy array if it is sparse csr.
    """

    def fit(self, X, y=None, **kwargs):
        """Dummy fit function that does nothing particular."""
        return self

    def transform(self, X, y=None, **kwargs):
        """Convert input column X as string type

        Args:
            X (array-like): array-like of shape (n_samples, n_features).
            y (array-like): array-like of shape (n_samples, ). 
                Do nothing. Defaults to None.

        Returns:
            [type]: [description]
        """
        if isinstance(X, scipy.sparse.csr.csr_matrix):
            return X.toarray()
        else:
            return X