import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


def plot_pca_variability(X_train, ax = None):
    """Plot PCA variability from train data.

    Args:
        X_train (pd.DataFrame): input data.
        ax ([type], optional): matplotlib axis. Defaults to None.

    Returns:
        [type]: [description]
    """

    if ax is None:
        ax = plt.gca()

    # Define PCA and fit with input data
    pca = PCA(random_state=0)
    pca.fit(X_train)

    # Auxiliar DataFrame
    df_aux = pd.DataFrame({'explained_variance':
                                    np.cumsum(pca.explained_variance_ratio_)})

    # Figure
    df_aux.plot(linewidth=3, ax = ax)
    for idx in df_aux.index:
        df_aux2 = df_aux.loc[idx]
        ax.vlines(x = idx, ymin=df_aux.min(), ymax=df_aux2['explained_variance'].max(), color = 'red')
        ax.annotate('{}%'.format(round(df_aux2['explained_variance'].min()*100)), xy = (idx, df_aux2['explained_variance'].max()), 
                    ha = 'center', va = 'bottom', color = 'red')
    ax.set_xlabel('Number of components', fontsize = 14, weight = 'bold')
    ax.set_xticks(df_aux.index)
    ax.set_ylabel('ratio explained',  fontsize = 14, weight = 'bold')
    ax.set_title('PCA Components Analysis',  fontsize = 16, weight = 'bold')
    return ax
