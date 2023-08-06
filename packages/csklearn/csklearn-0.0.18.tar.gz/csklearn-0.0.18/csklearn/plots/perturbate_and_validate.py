import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class perturbate_and_validate:
    """Class to get perturbation validations.

    Example of use:
    pv = perturbate_and_validate()

    # Get range from X_test (min and max values) and predictor to use
    pv.fit_predictor(X_test_tf, predictor_p = 'pca0') 

    # Plots
    fig, ax = plt.subplots(figsize = (10,5))
    pv.plot_perturbations(estimator, X_test_tf, y_test = y_test, 
                    y_test_name = TARGET, n_iter = 4, n_pert = 10, ax = ax)
    plt.show()
    """

    def __init__(self):
        self.predictor_p = None
        self.min = None
        self.max = None
        self.step = None
        

    def fit_predictor(self, X_train, predictor_p):
        """
        Introducir del conjunto de entrenamiento el predictor a perturbar
        para conocer sus medidas estadísticas.
        """
        self.predictor_p = predictor_p
        self.min = min(X_train[predictor_p])
        self.max = max(X_train[predictor_p])


    def perturbate(self, pipe, pdseries_row, n_iter=500) -> pd.DataFrame:
        """Method to generate pandas dataframe with n_pert rows (coming from
        only 1 perturbated)

        Args:
            pipe (Pipeline): sklearn pipeline.
            pdseries_row (pd.Series): a pandas series row. Example: df.iloc[0]
            n_iter (int, optional): number of points to show. 
                Defaults to 500.

        Raises:
            Exception: if is not fitted.

        Returns:
            pd.DataFrame: pandas dataframe with n_pert rows.
        """
        # Check is fitted
        if self.predictor_p is None:
            raise Exception('You must use fit_predictor method before perturbate!')

        row = pdseries_row#.copy()
        self.step = (self.max - self.min)/n_iter
        self.step = 1e-5 if self.step == 0 else self.step

        perturbations = []
        for perturbation in np.arange(self.min, self.max+1e-4, self.step):
            row[self.predictor_p] = perturbation
            y = pipe.predict(row.to_frame().transpose().values)
            perturbations.append(np.hstack([row, y]))


        df_p = pd.DataFrame(perturbations,
                              columns = list(row.keys())+['y_pred'])
        cols_order = ['y_pred', self.predictor_p]+\
                list(set(df_p.columns) - set(['y_pred', self.predictor_p]))
        df_p[['y_pred', self.predictor_p]].sort_values(self.predictor_p)

        return df_p[cols_order]


    def plot_perturbations(self, pipe, X_test, y_test = None, 
                                            y_test_name:str = None,
                                            n_pert:int=10, 
                                            n_iter:int = 50, 
                                            ax = None,  **kwargs):
        """Method to plot perturbations. Return matplotlib axes.

        Args:
            pipe (Pipeline): sklearn pipeline.
            X_test (pd.DataFrame): needed to be perturbated (randomly)
            y_test (pd.DataFrame, optional): if is defined, then uses this to
                make a scatter plot of the real variables. Defaults to None.
            y_test_name (str, optional): [description]. Defaults to None.
            n_iter (int, optional): number of points to show. 
                Defaults to 500.
            n_pert (int, optional): number of perturbations to generate. 
                Defaults to 10.
            ax (AxesSubplot, optional): matplotlib axes. Defaults to None.

        Raises:
            Exception: if X_test and y_test length differ.
            Exception: if n_pert is higher than X_test length.

        Returns:
            AxesSubplot: matplotlib axes.
        """
        
        # Check
        if len(X_test) != len(y_test):
            raise Exception('X_test and y_test have different lenght: {} vs {}'.\
                            format(len(X_test), len(y_test)))
        if n_pert > len(X_test):
            raise Exception("You can't get more perturbations than data you have!")
            
        y_test_name = 'y' if y_test_name is None else y_test_name
        
        if ax is None:
            ax = plt.gca()       
        
        # Get random indexes to plot
        idxs = np.random.choice(range(len(X_test)), n_pert, replace = False)
        
        # Change color
        cmap = plt.cm.get_cmap('hsv', len(idxs))

        # Real points scattered
        if y_test is not None:
            X_test[y_test_name] = y_test.values
            X_test.plot.scatter(x=self.predictor_p, y=y_test_name, 
                                    ax=ax, 
                                    color = 'black', 
                                    marker='x', 
                                    legend=True)
                
            # Important!
            X_test.drop(y_test_name, axis = 1, inplace = True)

        for c, idx in enumerate(idxs):
            row = X_test.iloc[idx]
            df_p = self.perturbate(pipe, row, n_iter=n_iter)
            
            # Perturbations
            df_p.plot(self.predictor_p, 'y_pred', 
                                color = cmap(c), 
                                linewidth = .7, 
                                alpha = .8,
                                ax = ax, **kwargs)
            
            # remove legend
            ax.get_legend().remove()
        return ax