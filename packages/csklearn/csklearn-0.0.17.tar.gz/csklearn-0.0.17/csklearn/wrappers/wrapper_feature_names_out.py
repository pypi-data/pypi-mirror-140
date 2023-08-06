from sklearn.utils.validation import _check_feature_names_in
from sklearn.decomposition import PCA
from sklearn.impute import *
from sklearn.preprocessing import *


class wPCA(PCA):
    """
    Wrapper PCA to get feature names out
    """
        
    def get_feature_names_out(self, input_features=None):
        return ['pca'+str(i) for i in range(len(self.components_))]
    

class wSimpleImputer(SimpleImputer):
    """
    Wrapper SimpleImputer to get feature names out
    """
        
    def get_feature_names_out(self, input_features=None):
        return _check_feature_names_in(self, input_features)


class wBinarizer(Binarizer):
    """
    Wrapper Binarizer to get feature names out
    """
        
    def get_feature_names_out(self, input_features=None):
        return _check_feature_names_in(self, input_features)


class wKBinsDiscretizer(KBinsDiscretizer):
    """
    Wrapper Binarizer to get feature names out
    """
        
    def get_feature_names_out(self, input_features=None):
        return ['kbd'+str(i) for i in range(len(self.n_bins_))]


class wKNNImputer(KNNImputer):
    """
    Wrapper Binarizer to get feature names out
    """
        
    def get_feature_names_out(self, input_features=None):
        return _check_feature_names_in(self, input_features)