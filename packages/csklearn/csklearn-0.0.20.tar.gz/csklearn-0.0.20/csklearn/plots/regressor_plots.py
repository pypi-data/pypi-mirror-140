import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates


def plot_ts_preds(df, y_real:str, y_pred:str, 
                            ts:str='ts',
                            ts_vlines:list = [], 
                            title:str = None):
    """Repsol's particular function to represent forecasts. Takes a
        PandasDataFrame which contains Timestamp, Target and Prediction columns.

    Args:
        df ([pd.DataFrame]): Pandas DataFrame with Timestamp, Target and Prediction.
        y_real (str): target name
        y_pred (str): prediction name
        ts (str, optional): target name. Defaults to None.
        ts_vlines (list, optional): to plot vertical lines in Timestamp axis. Defaults to [].
        title (str, optional): set title in graphic. Defaults to None.

    Returns:
        [type]: matplotlib figure
    """

    # Main plots
    fig, ax = plt.subplots(figsize=(30,10))
    df.set_index('ts')[y_real].\
            plot(ax=ax, color = 'blue', style='.-', linewidth=2,  alpha=.4)
    df.set_index('ts')[y_pred].\
            plot(ax=ax, color = 'orange', style='.-', linewidth=2,  alpha=.8)

    # Axis                                            
    ax.set_title(title, fontweight="bold", fontsize=14)
    ax.set_ylabel(y_real, fontsize=12)
    ax.set_xlabel(None, fontsize=14)
    ax.legend(**{'fontsize':14})
    ax.grid(b=True, which='both', axis = 'x', **{'color':'white', 
                                                'linestyle':':', 
                                                'linewidth':'0.7'})

    # Dates Formaters
    fd_major = DateFormatter("\n%m/%Y")
    fd_minor = DateFormatter("%d")
    interval_major = mdates.MonthLocator(interval=1)
    interval_minor = mdates.DayLocator(interval=14)
    ax.xaxis.set_major_formatter(fd_major)
    ax.xaxis.set_minor_formatter(fd_minor)
    ax.xaxis.set_major_locator(interval_major)
    ax.xaxis.set_minor_locator(interval_minor)
    ax.grid(b=True, which='major', color='k', alpha=.2, linewidth=1.0)
    ax.grid(b=True, which='minor', color='w', alpha=.2, linewidth=1.0)
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    for vline in ts_vlines:
        ax2.axvline(vline, color='r', ls = '--', linewidth=3)
    ax2.set_xticks(ts_vlines)
    ax2.set_xticklabels(ts_vlines, fontsize=10, color='red')

    plt.close()

    return fig