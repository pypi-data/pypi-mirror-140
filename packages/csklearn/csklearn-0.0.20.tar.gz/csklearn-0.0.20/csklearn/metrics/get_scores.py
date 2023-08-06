from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline
import numpy as np
import re


def get_score(y_test, y_pred, scorer) -> float:
    """Get score from an element of d_scorer

    Args:
        y_test (array-like): array-like of shape (n_samples,). Test data
        y_pred (array-like): array-like of shape (n_samples,). Predicted data
        scorer (float): sklearn scorer

    Returns:
        [float]: score
    """
    metric = scorer.__dict__['_score_func']
    kwargs = scorer.__dict__['_kwargs']
    return metric(y_test, y_pred, **kwargs)


def get_pipe_score(pipe:Pipeline, X_test, y_test, scorer) -> float:
    """Get score given a Pipeline

    Args:
        pipe (Pipeline): sklearn pipeline.
        X_test (array-like): array-like of shape (n_samples, n_features).
        y_test (array-like): array-like of shape (n_samples,).
        scorer (_PredictScorer): sklearn scorer

    Returns:
        float: score
    """

    # Handle with predict and predict_proba
    try:
        return get_score(y_test, pipe.predict(X_test), scorer)
    except:
        return get_score(y_test, pipe.predict_proba(X_test), scorer)


def get_scores(y_test, y_pred, d_scorer:dict, prefix:str=None) -> dict:
    """Get scores given a dictionary of scorers.

    Args:
        y_test (_type_): (array-like): array-like of shape (n_samples,).
        y_pred (_type_): (array-like): array-like of shape (n_samples,).
        d_scorer (dict): dictionary of {key:make_scorer()}.
        prefix (str, optional): _description_. Defaults to None.

    Returns:
        dict: _description_

    Example of d_scorer input:
        d_scorer = {
            'rmse':make_scorer(mean_squared_error),
            'mae':make_scorer(mean_absolute_error),
            'r2':make_scorer(r2_score)
        }
    """
    prefix = prefix+'_' if prefix is not None else ''
    return {prefix+k:get_score(y_test, y_pred, v) for k,v in d_scorer.items()}


def get_pipe_scores(pipe, X_test, y_test, d_scorer, prefix=None):

    # no podemos utilizar get_scores para tener en cuenta la excepcion predict_proba
    d_res = {}

    # Prefix case
    prefix = prefix+'_' if prefix is not None else ''
    for k,v in d_scorer.items():
        try:
            d_res.update({prefix+k:get_score(y_test, 
                                                pipe.predict(X_test), 
                                                v)})
        except:
            d_res.update({prefix+k:get_score(y_test, 
                                                pipe.predict_proba(X_test), 
                                                v)})
    return d_res


def get_cv(pipe, X, y, d_scorer, cv=3, prefix='cv', dec_round = 4, 
                                                    return_times = False, 
                                                    return_estimators = True,
                                                    **kwargs):

    # To get useful info
    regex_filter = 'test'
    if return_times:
        regex_filter = '(test|fit_time)'

    # Crossvalidate with sklearn function
    cv_output = cross_validate(pipe, X, y, cv=cv, scoring=d_scorer, 
                                            return_estimator=return_estimators,
                                            **kwargs)
    

    # Results
    d_cv_results = {k.replace('test', prefix).replace('fit', prefix):v 
                                        for k,v in cv_output.items() 
                                        if re.compile(regex_filter).match(k)}
    d_cv_results = {k+'_'+str(i):v for k in d_cv_results.keys() 
                                    for i,v in enumerate(d_cv_results[k])}
    # print(d_cv_results)

    # Median
    d_cv_results_median = {prefix+'_median_'+k:np.median(
                            [v2 for k2,v2 in d_cv_results.items() if k in k2]) 
                                    for k in d_scorer.keys()}

    # Mean
    d_cv_results_mean = {prefix+'_mean_'+k:np.mean(
                            [v2 for k2,v2 in d_cv_results.items() if k in k2]) 
                                    for k in d_scorer.keys()}

    # Std
    d_cv_results_std = {prefix+'_std_'+k:np.std(
                            [v2 for k2,v2 in d_cv_results.items() if k in k2]) 
                                    for k in d_scorer.keys()}

    # Mean+Std
    d_cv_results_std = {prefix+'_meanstd_'+k:np.std(
                            [v2 for k2,v2 in d_cv_results.items() if k in k2]) 
                                    for k in d_scorer.keys()}
    d_cv_results.update(d_cv_results_std)

    # Time
    if return_times:
        d_cv_results_times = {prefix+'_mean_time':np.mean(
                        [v2 for k2,v2 in d_cv_results.items() if 'time' in k2])}
        d_cv_results_mean.update(d_cv_results_times)
        d_cv_results_std.update({prefix+'_std_time':np.std(
                    [v2 for k2,v2 in d_cv_results.items() if 'time' in k2])})

    # Update all
    d_cv_results.update(d_cv_results_median)
    d_cv_results.update(d_cv_results_mean)
    d_cv_results.update(d_cv_results_std)
    d_cv_results = {k:round(v, dec_round) for k,v in d_cv_results.items() 
                                                    if 'meanstd' not in k}

    # Mean+Std
    d_ms = {k.replace('mean','meanstd'):'{:}+-{:}'.format(round(v1,dec_round),
                                                            round(v2,dec_round)) 
                                for k,v1,v2 in zip(d_cv_results_mean.keys(), 
                                                    d_cv_results_mean.values(), 
                                                    d_cv_results_std.values())}
    d_cv_results.update(d_ms)
    

    # Add Estimators
    if return_estimators:
        cv_estimators = {'fitted_estimator_'+str(i):v for i,v in 
                                            enumerate(cv_output['estimator'])}
        d_cv_results.update(cv_estimators)

    return d_cv_results


def get_cv_scores_from_cv_results(d_cv_results:dict, 
                                    only_mean:bool=True, 
                                    mean_str:bool= True, 
                                    prefix:str='cv')->dict:
    """Función muy particular para obtener predicción en otro conjunto de cada
    fold. Coge el d_cv_results de la función get_scores_cv filtrando.

    Args:
        d_cv_results (dict): diccionario generado por la función get_cv()
        only_mean (bool, optional): devolver sólo las medias (evitando los
            resultados de cada fold). Defaults to True.
        mean_str (bool, optional): para devolver como string mean+-std. 
            Defaults to True.
        prefix (str, optional): prefijo de la validación. Defaults to 'cv'.

    Returns:
        dict: diccionario con los resultados
    """
    if (only_mean) & (mean_str):
        return {k:v for k,v in d_cv_results.items() if 
                        ((prefix+'_median' in k) |\
                        ('meanstd' in k))}
    elif (only_mean):
        return {k:v for k,v in d_cv_results.items() if 
                        (((prefix+'_mean' in k) | (prefix+'_median' in k)) &\
                        ('meanstd' not in k))}
    else:
        return {k:v for k,v in d_cv_results.items() if (prefix in k)}


def get_test_scores_from_cv_results(d_cv_results:dict, 
                                    X_test, y_test, 
                                    d_scorer:dict, 
                                    dec_round:int = 4,
                                    only_mean:bool=True, 
                                    mean_str:bool = True, 
                                    prefix:str='test') -> dict:
    """Función muy particular para obtener predicción en otro conjunto de cada
    fold. Coge el d_cv_results de la función get_scores_cv, filtra y calcula.

    Args:
        d_cv_results (dict): diccionario generado por la función get_cv()
        X_test (pd.DataFrame): [description]
        y_test (pd.Series): [description]
        d_scorer (dict): diccionario con los scorers de SKLearn.
        dec_round (int): decimal a redondear. Defaults to 4.
        only_mean (bool, optional): devolver sólo las medias (evitando los
            resultados de cada fold). Defaults to True.
        mean_str (bool, optional): para devolver como string mean+-std. 
            Defaults to True. Defaults to True.
        prefix (str, optional): prefijo de la validación. Defaults to 'test'.

    Returns:
        dict: diccionario con los resultados
    """
    # Score in Test
    d_res_test = {k:get_pipe_scores(est, X_test, y_test, d_scorer, prefix) 
                                        for k, est in  d_cv_results.items() 
                                            if ('fitted_estimator' in k)}

    d_res_test = {k.replace('fitted_','')+'_'+k2:v2 
                    for k,v in d_res_test.items() for k2,v2 in v.items()}
    d_res_test = {'_'.join([k.split('_')[2],
                            k.split('_')[0],
                            k.split('_')[1],
                            k.split('_')[3]]):v for k,v in d_res_test.items()}

    # Median
    d_res_test.update({prefix+'_median_'+k:
                    np.median([v2 for k2,v2 in d_res_test.items() if '_'+k in k2]) 
                    for k in d_scorer.keys()})
    
    # Mean
    d_cv_results_mean = {prefix+'_mean_'+k:
                    np.mean([v2 for k2,v2 in d_res_test.items() if '_'+k in k2]) 
                    for k in d_scorer.keys()}
    d_res_test.update(d_cv_results_mean)

    # Std
    d_cv_results_std = {prefix+'_std_'+k:
                    np.std([v2 for k2,v2 in d_res_test.items() if '_'+k in k2]) 
                    for k in d_scorer.keys()}
    d_res_test.update(d_cv_results_std)

    # Round
    d_res_test = {k:round(v, dec_round) for k,v in d_res_test.items() 
                                                    if 'meanstd' not in k}

    # Mean+Std
    d_ms = {k.replace('mean','meanstd'):'{:}+-{:}'.format(round(v1,dec_round),
                                                            round(v2,dec_round)) 
                                for k,v1,v2 in zip(d_cv_results_mean.keys(), 
                                                    d_cv_results_mean.values(), 
                                                    d_cv_results_std.values())}
    d_res_test.update(d_ms)

    if (only_mean) & (mean_str):
        return {k:v for k,v in d_res_test.items() if 
                                ( (prefix+'_median_' in k) |
                                  (prefix+'_meanstd_' in k)
                                )}
    elif (only_mean):
        return {k:v for k,v in d_res_test.items() if 
                                ( (prefix+'_median_' in k) |
                                  (prefix+'_mean_' in k) |
                                  (prefix+'_std_' in k))}
    else:
        return d_res_test