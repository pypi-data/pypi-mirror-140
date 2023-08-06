from sklearn.utils.validation import _check_feature_names_in
import category_encoders as ce
    

class wOrdinalEncoder(ce.OrdinalEncoder):
    """
    Wrapper SimpleImputer to get feature names out
    """
        
    def get_feature_names_out(self, input_features=None):
        return self.get_feature_names()

class wCountEncoder(ce.CountEncoder):
    """
    Wrapper SimpleImputer to get feature names out
    """
        
    def get_feature_names_out(self, input_features=None):
        return self.get_feature_names()