import nltk
import pandas as pd
import numpy as np
import re
from sklearn.base import *
from tqdm import tqdm
from collections import Counter


class TextCleaning(BaseEstimator, TransformerMixin):
    def __init__(self, rm_whitespaces:bool = True,
                        normalize_method:bool = None,
                        stopwords:bool = True,
                        lowercase:bool = True,
                        rm_numbers:bool = True,
                        rm_punct:bool = True,
                        onlywords:bool = True,
                        stp_lang: str = 'english',
                        ls_rmregex = ['[—°]'],
                        split_regexp: str = '[/]',
                        len_threshold:int = 1,
                        verbose = False):
        """SKLearn Transformer to preprocess text as tokens and removes
            extraneous characters. It is useful when semantic information cannot
            be extracted from the text to be processed, but keywords can be
            extracted.

        Args:
            rm_whitespaces (bool, optional): Remove extra white spaces.
                Defaults to False.
            normalize_method (str, optional): base form of the words.
                Options: [None, 'stemming', 'lemmatization']. lemmatization only
                 supported with english.
                Note: stemming technique only looks at the form of the word
                whereas lemmatization technique looks at the meaning of the
                word. It means after applying lemmatization, we will always get
                a valid wordDefaults to None.
            stopwords (bool, optional): Remove stop words.
                Defaults to False.
            lowercase (bool, optional): Convert to lowercase.
                Defaults to False.
            rm_numbers (bool, optional): Remove all digits.
                Defaults to False.
            rm_punct (bool, optional): Remove all punctuations.
                Defaults to False.
            stp_lang (str, optional): Language for stop words and stemmer.
                Defaults to 'english'.
            ls_rmregex (tuple, optional): Regular expressions to remove words.
            len_threshold (int, optional): length threshold to allow a word.
                Defaults to 1.
            split_regexp (str, optional): strings used to split text.
                Defaults to '[/]'.
            verbose (bool, optional): if True, shows progress bar.
                Defaults to False.
        """
        # Arguments
        self.rm_whitespaces = rm_whitespaces
        self.normalize_method = normalize_method
        self.stopwords = stopwords
        self.lowercase = lowercase
        self.rm_numbers = rm_numbers
        self.onlywords = onlywords
        self.rm_punct = rm_punct
        self.stp_lang = stp_lang
        self.ls_rmregex = ls_rmregex
        self.split_regexp = split_regexp
        self.len_threshold = len_threshold

        # Settings
        self.verbose = verbose


    def fit(self, X, y=None):
        """Fit method. If target_encoding is False, then not applies.

        Args:
            X (array-like, sparse matrix): Training vectors. If there are more
                than 1 feature, they are concatenated.
            y (array-like of shape (n_samples,), optional): Defaults to None.
        Returns:
            [object]: self
        """
        return self


    def transform(self, X, y=None):
        """Given a raw matrix string, return cleaned text

        Args:
            X (pd.Dataframe or np.array): matrix with text fields
            y ([type], optional): Not used, only for compatibility with sklearn.
                Defaults to None.

        Returns:
            np.array: array with text cleaned
        """
        X = np.array(X)
        X_shape = X.shape
        if self.verbose:
            tf=np.array([self._clean_text(str(y)) for y in tqdm(X.flatten())]).\
                reshape(X_shape)
        else:
            tf=np.array([self._clean_text(str(y)) for y in X.flatten()]).\
                reshape(X_shape)
        return tf


    def _clean_text(self, text):
        return clean_text(text, rm_whitespaces = self.rm_whitespaces,
                                normalize_method = self.normalize_method,
                                stopwords = self.stopwords,
                                lowercase = self.lowercase,
                                rm_numbers = self.rm_numbers,
                                rm_punct = self.rm_punct,
                                onlywords = self.onlywords,
                                stp_lang = self.stp_lang,
                                ls_rmregex = self.ls_rmregex,
                                split_regexp = self.split_regexp,
                                len_threshold = self.len_threshold)



class OneHotEncodingWords(BaseEstimator, TransformerMixin):
    def __init__(self, prefix=None):
        """SKLearn Transformer to vectorize text as One Hot Encoding.

        Args:
            prefix (str, optional): OHE prefix. Defaults to ''.
        """

        # Results
        self.d_words_availables_ = None
        self.prefix = prefix
       


    def fit(self, X, y=None):
        """Fit method. Needs a column with text in each row.

        Args:
            X (array-like, sparse matrix): Training vectors. If there are more
                than 1 feature, they are concatenated.
            y (array-like of shape (n_samples,), optional): Class labels (only
                for classification). Defaults to None.

        Returns:
            [object]: self
        """
    
        if self.prefix:
            prefix = self.prefix+'_'
        else:
            prefix = ''

        X = np.array(X).flatten()

        # Select unique words of the entire column
        features_out = sorted(np.unique(np.hstack([x.split(' ') 
                                                    for x in X.flatten()])))
        self.features_out = [x for x in features_out if x != '']
        self.colnames_ = [prefix+x for x in self.features_out]

        return self


    def transform(self, X, y=None):
        """Given a raw matrix string, return cleaned text

        Args:
            X (pd.Dataframe or np.array): matrix with text fields
            y ([type], optional): Not used, only for compatibility with sklearn.
                Defaults to None.

        Returns:
            np.array: array with text cleaned
        """
        
        df_aux = pd.DataFrame(np.array(X), columns=['_txt'])

        
        df_aux[self.colnames_] = df_aux.apply(lambda row: 
                    pd.Series(np.isin(self.features_out, row['_txt'].split(' '))*1), 
                                                                    axis=1)
        df_aux.drop('_txt', axis=1)
        

        return df_aux.iloc[:,1:]

    
    def get_feature_names(self, features_in=None):
        """[summary]

        Args:
            features_in (array, optional): Dummy Argument for compatibility. 
                Defaults to None.
        """
        return self.colnames_

        

class TextEncoding(BaseEstimator, TransformerMixin):
    def __init__(self,
                        nwords_threshold:int = 20,
                        nrows_threshold:int = 4,
                        avoid_words = ['nan'],
                        label_unique_threshold = 1.0,
                        label_topk:int = None):
        """SKLearn Transformer to encoding text. It is useful when
            semantic information cannot be extracted from the text to be
            processed, but keywords can be extracted. It is divided into two
            blocks: text cleaning and token target encoding.

        Args:
            nwords_threshold (int, optional): minimum number of times that a
                word must appear in all words (for each target label).
                Defaults to 20.
            nrows_threshold (int, optional): minimum number of times that a
                word must appear in all rows (for each target label).
                Defaults to 5.
            avoid_words (array, optional): strings to be avoided.
                Defaults to ['nan'].
            label_unique_threshold (float, optional): ratio between 0 and 1 that
                indicates for a token how many different labels it appears on.
                If the token exceeds this ratio, then it is not considered.
                All tokens will be included if it is set to 1.
                Defaults to 1.
            label_topk (int, optional): number of top tokens to use for each
                label class. If None then uses all tokens.
                Defaults to None.

        Other Args:
            verbose (bool, optional): if True, shows progress bar.
                Defaults to False.
        """

        # If target encoding, else not applies
        self.nwords_threshold = nwords_threshold
        self.nrows_threshold = nrows_threshold
        self.avoid_words = avoid_words
        self.label_unique_threshold = label_unique_threshold
        self.label_topk = label_topk

        # Results
        self.d_impotokens_ = None
        self.d_toptokens_ = None
        self.ls_toptokens_ = None


    def fit(self, X, y=None):
        """Fit method. If target_encoding is False, then not applies.

        Args:
            X (array-like, sparse matrix): Training vectors. If there are more
                than 1 feature, they are concatenated.
            y (array-like of shape (n_samples,), optional): Class labels (only
                for classification). Defaults to None.

        Raises:
            Exception: if target_encoding and y is not given

        Returns:
            [object]: self
        """

        X = np.array(X)
        if y is None:
            raise Exception('target_encoding is True, y is needed!')

        self.d_impotokens_, self.d_toptokens_, self.ls_toptokens_ = \
                    TokenizedTargetEncoding(X, y,
                        label_unique_threshold=self.label_unique_threshold,
                        label_topk=self.label_topk,
                        nwords_threshold=self.nwords_threshold,
                        nrows_threshold=self.nrows_threshold,
                        avoid_words=self.avoid_words,
                        )
        return self


    def transform(self, X, y=None):
        """Given a raw matrix string, return cleaned text

        Args:
            X (pd.Dataframe or np.array): matrix with text fields
            y ([type], optional): Not used, only for compatibility with sklearn.
                Defaults to None.

        Returns:
            np.array: array with text cleaned
        """
        X_shape = X.shape
        X = np.array(X).flatten()

        if self.ls_toptokens_ is None:
            raise Exception('Not fitted yet!')

        tf=np.array([' '.join([word for word in row.split() if
                                                word in self.ls_toptokens_])
                        for row in X]).reshape(X_shape)
        print(tf)
        # tf=np.array([' '.join([word for word in row.split() if
        #                                         word in self.ls_toptokens_])
        #                 for row in X])
        return tf

    def fit(self, X, y=None):
        """Fit method. If target_encoding is False, then not applies.

        Args:
            X (array-like, sparse matrix): Training vectors. If there are more
                than 1 feature, they are concatenated.
            y (array-like of shape (n_samples,), optional): Class labels (only
                for classification). Defaults to None.

        Raises:
            Exception: if target_encoding and y is not given

        Returns:
            [object]: self
        """

        X = np.array(X)
        if y is None:
            raise Exception('target_encoding is True, y is needed!')

        self.d_impotokens_, self.d_toptokens_, self.ls_toptokens_ = \
                    TokenizedTargetEncoding(X, y,
                        label_unique_threshold=self.label_unique_threshold,
                        label_topk=self.label_topk,
                        nwords_threshold=self.nwords_threshold,
                        nrows_threshold=self.nrows_threshold,
                        avoid_words=self.avoid_words,
                        )
        return self


    def transform(self, X, y=None):
        """Given a raw matrix string, return cleaned text

        Args:
            X (pd.Dataframe or np.array): matrix with text fields
            y ([type], optional): Not used, only for compatibility with sklearn.
                Defaults to None.

        Returns:
            np.array: array with text cleaned
        """
        #X_shape = X.shape
        X = np.array(X).flatten()

        if self.ls_toptokens_ is None:
            raise Exception('Not fitted yet!')

        tf=np.array([' '.join([word for word in row.split() if
                                                word in self.ls_toptokens_])
                        for row in X])#.reshape(X_shape)
        # tf=np.array([' '.join([word for word in row.split() if
        #                                         word in self.ls_toptokens_])
        #                 for row in X])
        return tf


def clean_text(text, rm_whitespaces = True,
                        normalize_method = None,
                        stopwords = True,
                        lowercase = True,
                        rm_numbers = True,
                        rm_punct = True,
                        onlywords = True,
                        stp_lang: str = 'english',
                        ls_rmregex = ['[—°]'],
                        split_regexp: str = '[/]',
                        len_threshold:int = 1):
    for regexp in ls_rmregex:
        text = re.sub(regexp, '', text)
    text = re.sub(split_regexp, ' ', text)
    if rm_numbers:
        text = "".join([x for x in text if not x.isdigit()])
    if rm_punct:
        text = re.sub('[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]', ' ', text)
    if lowercase:
        text = text.lower()#casefold()
    if stopwords:
        text = rm_stop_words(text, stp_lang)
    if normalize_method is not None:
        text = normalize_words(text, normalize_method, stp_lang)
    if rm_whitespaces:
        text = re.sub("\s\s+" , " ", text)
    if len_threshold > 0:
        text = " ".join([word for word in text.split()
                                                if len(word) > len_threshold])
    if onlywords:
        text = " ".join(re.findall(r'\b([A-Za-z]+)\b', text)) #.isalpha() tambien hace esta operacion
    return text.strip()


def normalize_words(text, normalize_method, stp_lang = None):
        if (normalize_method == 'lemmatization'):
            if stp_lang != 'english':
                raise Exception('NLTK only support english to lemmatize')
            lemma = nltk.stem.WordNetLemmatizer()
            text = " ".join([lemma.lemmatize(word) for word in text.split()])
        elif normalize_method == 'stemming':
            stemmer = nltk.stem.snowball.SnowballStemmer(stp_lang)
            text = " ".join([stemmer.stem(word) for word in text.split()])
        else:
            raise Exception("Select normalize_method options: \
[None, 'stemming', 'lemmatization'].")
        return text


def rm_stop_words(text, stp_lang):
    stop_words = nltk.corpus.stopwords.words(stp_lang)
    return (" ".join([word for word in text.split() if
                        word not in stop_words]))


def word_counts(X, nwords_threshold = 20, nrows_threshold = 4,
                    avoid_words = ['nan']):
    """Function to count words and filter unfrequent words.

    Args:
        X (pd.DataFrame): [description]
        nwords_threshold (int, optional): minimum number of words in all text.
            Defaults to 5.
        nrows_threshold (int, optional): minimum number of rows which contains
            the word. Defaults to 4.
        avoid_words (list, optional): list of words to avoid.
            Defaults to ['nan'].

    Returns:
        dict: dictionary with word counter filtered.
    """

    X = np.array(X)

    # Count all words
    ls_text = ' '.join(X).split()
    word_counts = Counter(ls_text)

    # Count row times appear a word
    ls_unique_text = ' '.join(
                map(lambda x:' '.join(np.unique(x.split(' '))), X)).split()
    word_rowcounts = Counter(ls_unique_text)

    # MAIN FILTER
    words = [word for word in ls_text if
                                    (word_counts[word] >= nwords_threshold) &
                                    (word_rowcounts[word] >= nrows_threshold) &
                                    (word not in avoid_words)]

    return {k:v for k,v in Counter(words).items()}


def TokenizedTargetEncoding(X, y,
                            nwords_threshold = 4,
                            nrows_threshold = 20,
                            avoid_words = ['nan'],
                            label_unique_threshold = 1,
                            label_topk = None,
                            return_X = False):
    """Function to find Bag of Words (BoW) with Target Encoding.

    Args:
        X (array-like, sparse matrix): Training vectors. If there are more
            than 1 feature, they are concatenated.
        y (array-like of shape (n_samples,), optional): Class labels (only
            for classification). Defaults to None.
        nwords_threshold (int, optional): minimum number of words in label text.
            Defaults to 5.
        nrows_threshold (int, optional): minimum number of rows which contains
            the word for each label. Defaults to 4.
        avoid_words (list, optional): list of words to avoid.
            Defaults to ['nan'].
        label_unique_threshold (float, optional): ratio between 0 and 1 that
            indicates for a token how many different labels it appears on.
            If the token exceeds this ratio, then it is not considered.
            All tokens will be included if it is set to 1.
            Defaults to 1.
        label_topk (int, optional): number of top tokens to use for each
            label class. If None then uses all tokens.
            Defaults to None.
        return_X (bool, optional): to return matrix instead of BoW.
            Defaults to False.
    """

    X = np.array(X)
    X_shape = X.shape
    X = X.flatten()

    # Conteo total de palabras
    d_total_word_counts = word_counts(X, nwords_threshold, nrows_threshold,
                                        avoid_words)
    d_label_wordcount = {}
    d_label_wordratio = {}

    # Tópicos del target
    topics = sorted(np.unique(y))

    # Count words for each topic. Which is the ratio of a word between labels?
    for label in topics:
        X_l = X[np.where(y == label)]

        # Contador de palabras para cada label.
        d_label_wordcount[label] = dict(sorted({k:v for k,v in
            word_counts(X_l, nwords_threshold,
                            nrows_threshold,
                            avoid_words).items()}.items(),
                        key=lambda x: x[1],reverse=True))

        # Calcular el ratio de una palabra en label sobre el total de palabras
        d_label_wordratio[label]=\
            dict(sorted({k:round(v/d_total_word_counts[k],3)
                        for k, v in d_label_wordcount[label].items()}.items(),
                        key=lambda item: item[1], reverse=True))

    # Use pandas help find nones
    dfx = pd.DataFrame(d_label_wordcount).T
    df = (1-dfx.isnull().sum()/len(dfx)).to_frame('label_wordratio')
    df['label_wordcount'] = (len(dfx)-dfx.isnull().sum())
    df.sort_values('label_wordratio', ascending=False, inplace=True)

    # Percentage of times a word appears among all labels
    ls_filtered_words = df.loc[df['label_wordratio'] <=
                                                label_unique_threshold].index

    # Final dictionary with labels and their words
    d_impotokens = {label:{word:v for word,v in d.items() if
                    (word in ls_filtered_words)}
                    for label,d in d_label_wordratio.items()}

    d_toptokens = {labels:{k:x for k,x in zip(list(words.keys())[:label_topk],
                                    list(words.values())[:label_topk])}
                                for labels, words in d_impotokens.items()}
    df_toptokens = pd.DataFrame(d_toptokens)

    ls_toptokens = np.unique(np.hstack(
                                [[x for x in list(words.keys())[:label_topk]]
                            for words in d_impotokens.values()]))

    # Returns X vector with only important words
    if return_X:
        X=np.array([' '.join([word for word in row.split() if
                                                        word in ls_toptokens])
                            for row in X]).reshape(X_shape)
        return X
    else:
        # returns bag of words dictionaries and top tokens list
        return (d_impotokens, d_toptokens, ls_toptokens)
