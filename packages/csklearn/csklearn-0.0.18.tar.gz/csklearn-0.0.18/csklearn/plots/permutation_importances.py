# Modules
import pandas as pd
import eli5
from eli5.sklearn import PermutationImportance

def permutation_importances(pipe, X_test, y_test, predictors = None, n_iter=20):
    """Generate html report with Permutation Importances. It uses eli5.

    Args:
        pipe (Pipeline): SKLearn pipeline
        X_test ([type]): [description]
        y_test ([type]): [description]
        predictors ([list]): list of feature names of X_test matrix
        n_iter (int, optional): [description]. Defaults to 20.

    Returns:
        html: html object to report
    """
    if isinstance(X_test, pd.core.frame.DataFrame):
        X_test = X_test.values

    perm = PermutationImportance(pipe, random_state=0, n_iter=n_iter).\
                fit(X_test, y_test)
    pimp_html = eli5.show_weights(perm, 
                            feature_names = predictors)
    return pimp_html