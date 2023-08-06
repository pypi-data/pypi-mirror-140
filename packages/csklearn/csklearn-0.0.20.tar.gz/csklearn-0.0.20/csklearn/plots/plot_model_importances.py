import pandas as pd
import matplotlib.pyplot as plt


def plot_model_importances(pipe, predictors, n_top_features=10, 
                           title='Feature Importances', ax = None, **kwargs):
    

    if ax is None:
        ax = plt.gca()
    
    df_aux = pd.DataFrame({'Features':predictors, 
                           'Importances':pipe.feature_importances_})
    df_aux = df_aux.sort_values('Importances', ascending=True).\
                                                        tail(n_top_features)
    df_aux.set_index('Features').plot(kind='barh', ax = ax, **kwargs)
    ax.set_title(title)
    ax.set_legend = None
    return ax