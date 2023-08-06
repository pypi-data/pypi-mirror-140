from sklearn.model_selection import StratifiedKFold


class CustomStratifiedKFold(StratifiedKFold):
    """Same than StratifiedKFold but takes an array to stratify in
    initialization (not in split). Useful when you want to stratify by an
    arbitrary variable (not y)
    """
    def __init__(self, x_stratify, n_splits=5, shuffle = False, 
                                                        random_state = None):
        """Same initialization than StratifiedKFold with an extra argument.

        Args:
            x_stratify (array-like): array-like of shape (n_samples, n_features).
                Column to be stratified
            n_splits (int, optional): [description]. Defaults to 5.
            shuffle (bool, optional): [description]. Defaults to False.
            random_state ([type], optional): [description]. Defaults to None.
        """
        super(CustomStratifiedKFold, self).__init__(n_splits=n_splits, 
                                                    shuffle = shuffle, 
                                                    random_state = random_state)
        self.x_stratify = x_stratify


    def split(self, X, y = None, groups = None):
        """_summary_

        Args:
            X (array-like): array-like of shape (n_samples, n_features).
            y (_type_, optional): _description_. Defaults to None.
            groups (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        # Uses parent split (StratifiedKFold) to return a generator
        return super().split(X = X, y = self.x_stratify)