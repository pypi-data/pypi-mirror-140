import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix


def plot_accuracy(y_test, y_pred,
                         title='accuracy',
                         ax=None):
    """Agrupo por los labels y cuento las predicciones
    buenas vs lo que no son buenas.

    Args:
        X (pd.DataFrame or np.array): [description]
        y (pd.Series or np.array): [description]
        title (str, optional): [description]. Defaults to 'Sensitivity'.
        ax ([type], optional): [description]. Defaults to None.

    Returns:
        [matplotlib axes]: [description]
    """
    df_preds = pd.DataFrame({'y':y_test})
    df_preds['y_pred'] = y_pred
    df_preds['ok'] = (df_preds['y'] == df_preds['y_pred'])*1
    df_preds['nok'] = (df_preds['y'] != df_preds['y_pred'])*1  # preds equivocadas
    df_acc = df_preds.groupby('y').agg({'ok':lambda x: np.sum(x),
                                        'nok':lambda x: np.sum(x)}).\
            sort_values('ok', ascending=False)
    # plot
    if ax is None:
        ax = plt.gca()
    df_acc.plot(kind='barh', ax=ax)
    ax.set_title(title)
    ax.set_ylabel('Real label')
    return ax


def plot_preds(y_test, y_pred,
                        title='Predictions',
                        ax=None):
    """True Negative rate: measures the proportion of negatives that are 
    correctly identified. Agrupo por predicción y cuento las clases reales
    que ha acertado vs clases reales que no coinciden.

    Args:
        X (array-like): array-like of shape (n_samples, n_features).
        y (array-like): array-like of shape (n_samples, ).
        title (str, optional): [description]. Defaults to 'Sensitivity'.
        ax ([type], optional): [description]. Defaults to None.

    Returns:
        [matplotlib axes]: [description]
    """
    df_preds = pd.DataFrame({'y':y_test})
    df_preds['y_pred'] = y_pred
    df_preds['ok'] = (df_preds['y'] == df_preds['y_pred'])*1
    df_preds['nok'] = (df_preds['y'] != df_preds['y_pred'])*1 
    df_acc = df_preds.groupby('y_pred').agg({'ok':lambda x: np.sum(x),
                                                'nok':lambda x: np.sum(x)}).\
            sort_values('ok', ascending=False)
    # plot
    if ax is None:
        ax = plt.gca()
    df_acc.plot(kind='barh', ax=ax)
    ax.set_title(title)
    ax.set_ylabel('Prediction')
    return ax


def get_confusion_matrix(y_test, y_pred, all_labels=None, 
                            filter_labels_test:list=None,
                            filter_labels_pred:list=None,
                            filter_threshold=None,
                            colormap = True,
                            cmap = 'Reds',
                            vmin = 0,
                            vmax = None):
    """
    Description:
    Method to get the confusion matrix.

    Args:
        X (array-like): array-like of shape (n_samples, n_features).
        y (array-like): array-like of shape (n_samples, ).
        all_labels: numpy array with the possible values of the target
                    variable.
    Output:
    pandas DataFrame with the confusion matrix. The entry i-j is the number
    of times a row with label i was predicted as j.
    """
    # create confusion matrix
    if all_labels is None:
        unique_y = y_test.unique()
        unique_y_pred = np.unique(y_pred)
        cm_labels = np.unique(np.concatenate((unique_y,
                                                unique_y_pred),
                                                axis=0))
    else:
        cm_labels = all_labels
    array_cm = confusion_matrix(y_true=y_test,
                                y_pred=y_pred,
                                labels=cm_labels)
    # np array to pandas DataFrame
    df_cm = pd.DataFrame(data=array_cm,
                            index=cm_labels,
                            columns=cm_labels)

    for i in range(df_cm.shape[0]):
        df_cm.iloc[i, i] = -df_cm.iloc[i, i]

    # Auxiliar matrix to help
    df_aux = df_cm.copy()
    np.fill_diagonal(df_aux.to_numpy(), 0)
    max_value = df_aux.max().max()

    if vmax is None:
        vmax = max_value


    if filter_threshold:
        # df_aux hace 0 la diagonal para encontrar los indices del filtro
        row_idx, col_idx = list(np.where(df_aux.values > filter_threshold))

        filter_labels_test = df_cm.iloc[np.unique(row_idx)].index
        filter_labels_pred = df_cm.columns[np.unique(col_idx)]

        

    if filter_labels_test is not None:
        df_cm = df_cm.loc[filter_labels_test]

    if filter_labels_pred is not None:
        df_cm = df_cm[filter_labels_pred]
    
    if colormap:
        return df_cm.style.background_gradient(cmap=cmap, vmin=vmin, vmax=vmax)
    return df_cm


def get_accuracy_matrix(y_test, y_pred) -> pd.DataFrame:
    """_summary_

    Args:
        y_test (array-like): array-like of shape (n_samples, ).
        y_pred (array-like): array-like of shape (n_samples, ).

    Returns:
        pd.DataFrame: _description_
    """

    # precision
    df_preds = pd.DataFrame({'y':y_test.tolist()})
    df_preds['y_pred'] = y_pred.tolist()
    df_preds['ok'] = (df_preds['y'] == df_preds['y_pred'])*1
    df_preds['accuracy'] = (df_preds['y'] == df_preds['y_pred'])*1
    df_preds['nok'] = (df_preds['y'] != df_preds['y_pred'])*1  
    df_acc = df_preds.groupby('y_pred').agg({'accuracy':lambda x: np.sum(x)/len(x),\
        'ok':lambda x: np.sum(x), 'nok':lambda x: np.sum(x)}).\
        sort_values('ok', ascending=False)
    df_acc['precision'] = df_acc.ok / (df_acc.ok + df_acc.nok)
    df_acc.reset_index(inplace=True)

    # sensitivity
    df_sen = df_preds.groupby('y').agg({'ok':lambda x: np.sum(x), 'nok':lambda x: np.sum(x),
             'y_pred': lambda x: '||||'.join([str(a)+' ('+str(b)+')' 
                         for a,b in zip(np.unique(x, return_counts=True)[0], 
                         np.unique(x, return_counts=True)[1])]),}).\
        sort_values('ok', ascending=False)
    df_sen['sensitivity'] = df_sen.ok / (df_sen.ok + df_sen.nok)
    df_sen.reset_index(inplace=True)

    # merge sensitivity and precision
    df_merge = df_acc.merge(df_sen, how='left', left_on='y_pred', right_on='y')
    df_merge.sort_values('sensitivity', ascending=False, inplace=True)

    return df_merge


def get_preds_matrix(y_test, y_pred) -> pd.DataFrame:
    """_summary_

    Args:
        y_test (array-like): array-like of shape (n_samples, ).
        y_pred (array-like): array-like of shape (n_samples, ).

    Returns:
        pd.DataFrame: _description_
    """
    df_preds = pd.DataFrame({'y':y_test})
    df_preds['y_pred'] = y_pred
    df_preds['ok'] = (df_preds['y'] == df_preds['y_pred'])*1
    df_preds['county'] = df_preds['y']
    df_miss = df_preds.groupby('y_pred', as_index=False).\
            agg({'county':'count',
                    'y': lambda x: '||||'.join([str(a)+' ('+str(b)+')' 
                        for a,b in zip(np.unique(x, return_counts=True)[0], 
                        np.unique(x, return_counts=True)[1])]),
                    'ok':'sum'}).\
            rename(columns={'county':'preds_count', 'ok':'correct_class'})

    df_miss['y'] = df_miss['y'].apply(lambda x: x.split('||||'))
    df_preds.drop('county', axis=1, inplace=True)
                            

    df_miss['accuracy'] = round(df_miss['correct_class']/
                                df_miss['preds_count'], 3)
    df_miss = df_miss.sort_values('accuracy', ascending=False)

    return df_miss

