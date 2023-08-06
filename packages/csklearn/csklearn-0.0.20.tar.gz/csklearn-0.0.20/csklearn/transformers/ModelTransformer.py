from sklearn.base import TransformerMixin
import numpy as np
import pandas as pd


class ModelTransformer(TransformerMixin):
    """Convert an estimator into transformer. Is useful to use model predictions 
    as predictors. It works by using indexes of "X" to find those of "y".
    """

    def __init__(self, model, 
                        df_y, 
                        predict:bool=True, 
                        predict_proba:bool=False, 
                        drop_first_prob:bool = True, 
                        prefix_output:str = 'mt'):
        """Initialization with model and target "y" with indexes.

        Args:
            model (_type_): _description_
            df_y (pd.Series or pd.DataFrame): target "y" with all "X" indexes.
            predict (bool, optional): wheter include predictions. Defaults to True.
            predict_proba (bool, optional): wheter include probabilities \
                (only works in classification). Defaults to False.
            drop_first_prob (bool, optional): whether remove 1st column in probabilities predictions. \
                Defaults to True.
            prefix_output (str, optional): set prefix to describe a step in \
                Pipelines. Defaults to 'mt'.

        Raises:
            Exception: if target "y" is not a pd.Series or pd.DataFrame.

        Example of usage:
            any_target = 'use_a_column_as_target'
            df_y = df[any_target] # Specify target (will use needed indexes)
            target_regt = Pipeline(steps=[
                ('target_tf', target_tf_fu), # Preliminary preprocessing
                ('target_reg', ModelTransformer(
                            model = algorithm,
                                    predict_labels = True,
                                    predict_probs = False,
                                    df_y = df_y, # ModelTransformer select indexes!
                            )),
            ])
        """
        self.model = model
        self.predict = predict
        self.predict_proba = predict_proba
        self.drop_first_prob = drop_first_prob # Eliminar la primera columna de predict_proba
        self.prefix_output = prefix_output
        self._feature_names_out = None
        self.df_y = df_y
        
        # Important check
        if self.df_y is not None:
            if isinstance(df_y, pd.Series) | isinstance(df_y, pd.DataFrame):
                self.df_y = df_y
            else:
                raise Exception('ModelTransformer Error: "y" argument must be pd.Series or pd.DataFrame')


    def get_params(self, deep=True):
        return dict(model=self.model, predict_proba=self.predict_proba, 
                    drop_first_prob = self.drop_first_prob,
                    df_y=self.df_y, prefix_output=self.prefix_output)


    def fit(self, *args, **kwargs):
        """Usual fit from SKLearn framework.

        Raises:
            Exception: if "y" is not a pd.Series or pd.DataFrame.
            Exception: if "y" does not have all "X" indexes.
        """

        # Get indexes from X
        X_ = args[0] # usually is a matrix
        y_ = args[1] # we need to be a pd.series

        # Print to check if is working (SKLEARN 1.0.1 - 16/12/2021 works):
        # print('Indices not used to fit:')
        # print([x for x in self.df_y.index if x not in y_.index])

        # sanity check
        if not (isinstance(y_, pd.Series) | isinstance(y_, pd.DataFrame)):
            raise Exception('ModelTransformer Error: pd.Series or pd.DataFrame indexes are needed in "y"')

        # In args, we have X_test, so we can get indexes      
        if self.df_y is None:
            self.model.fit(*args, **kwargs)
        else:
            # Sanity Check. All indexes should be in df_y
            if len([x for x in y_.index if x not in self.df_y.index]) > 0:
                raise Exception('ModelTransformer Error: "df_y" indexes does not\
 match with "X" indexes. "df_y" should have all "X" indexes (you can use the entire "df_y").')
            self.model.fit(X_, self.df_y.loc[y_.index], **kwargs)

        # Get feature names!
        _ = self.transform(X_) # doesn't return anything!
        
        return self


    def _predict_proba(self, X):
        Xtrf = self.model.predict_proba(X)
        arr = np.asarray(Xtrf).reshape((len(X), -1))
        cols = [self.prefix_output+'p_'+str(x) for x in self.model.classes_]

        if self.drop_first_prob:
            arr = arr[:,1:] # From 1st column to the rest (avoid colineality)
            cols = cols[1:]
        return arr, cols
    

    def _predict(self, X):
        Xtrf = self.model.predict(X)
        arr = np.asarray(Xtrf).reshape((len(X),1))
        cols = [self.prefix_output+'l_'+'_y']
        return arr, cols


    def transform(self, X, **transform_params) -> pd.DataFrame:
        """Usual transform in SKLearn framework.

        Args:
            X (array-like): X matrix.

        Raises:
            Exception: if predict and predict_proba are both set in False.

        Returns:
            pd.DataFrame: transformed matrix with new columns.
        """

        if (self.predict_proba) & (self.predict):
            arrp, colsp = self._predict_proba(X)
            arrl, colsl = self._predict(X)
            arr = np.hstack([arrp, arrl])
            cols = np.hstack([colsp, colsl]).tolist()

        elif (self.predict_proba):
            arr, cols = self._predict_proba(X)

        elif self.predict:
            arr, cols = self._predict(X)
        
        else:
            raise Exception('predict_proba or predict methods must be at least one True')

        self._feature_names_out = cols
        return pd.DataFrame(arr, columns = cols)


    def get_feature_names_out(self, features_in=None):
        """Get feature names after preprocessing.

        Args:
            features_in (array, optional): Dummy Argument for compatibility. 
                Defaults to None.
        """
        return self._feature_names_out