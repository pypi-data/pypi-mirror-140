import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s: %(name)s: %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

class PyDataEncoder:
    def __init__(self, **Kwargs):

        self.Kwargs = Kwargs

        try:
            self.data = self.Kwargs['data']    
        except Exception as AttributeError:
            logger.error('No data is found')
            raise Exception('No data is found')

        try:
            assert isinstance(self.data, pd.DataFrame)
        except Exception as AttributeError:
            logger.error('data must be of type: pd.DataFrame')    
            raise Exception('data must be of type: pd.DataFrame')    

        try:
            self.features = self.Kwargs['features']  
        except Exception as AttributeError:
            logger.error('No feature(s) are found')
            raise Exception('No feature(s) are found')

        try:
            assert isinstance(self.features, list)
        except Exception as AttributeError:
            logger.error('feature(s) must be passed as a list')    
            raise Exception('feature(s) must be passed as a list')    
        
        try:
            self.encoder = self.Kwargs['encoder']    
        except Exception as AttributeError:
            logger.error('No encoder is found')
            logger.error('Allowed encoders: FindnReplace, LabelEncoder, OneHotEncoder, ScikitOrdinalEncoder and ScikitOneHotEncoder')
            raise Exception('No encoder is found')

        try:
            if self.encoder == 'FindnReplace':
                self.FindnReplace()
            elif self.encoder == 'LabelEncoder':
                self.LabelEncoder()
            elif self.encoder == 'OneHotEncoder':
                self.OneHotEncoder()
            elif self.encoder == 'ScikitOrdinalEncoder':
                self.ScikitOrdinalEncoder()
            elif self.encoder == 'ScikitOneHotEncoder':
                self.ScikitOneHotEncoder()
            else:
                logger.error('Allowed encoders: FindnReplace, LabelEncoder, OneHotEncoder, ScikitOrdinalEncoder and ScikitOneHotEncoder')
                raise Exception('Allowed encoders: FindnReplace, LabelEncoder, OneHotEncoder, ScikitOrdinalEncoder and ScikitOneHotEncoder')
        except Exception as e:
            logger.error('Allowed encoders: FindnReplace, LabelEncoder, OneHotEncoder, ScikitOrdinalEncoder and ScikitOneHotEncoder')
            raise Exception('Allowed encoders: FindnReplace, LabelEncoder, OneHotEncoder, ScikitOrdinalEncoder and ScikitOneHotEncoder')

        
    def FindnReplace(self):
        self.encoded_data = self.data.replace({feature: dict(zip(self.data[feature].unique(), range(len(self.data[feature].unique())))) for feature in self.features}).values

    def LabelEncoder(self):
        self.encoded_data = (self.data[feature].astype('category').cat.codes for feature in self.features).values

    def OneHotEncoder(self):
        self.encoded_data = pd.get_dummies(data, columns=self.features).values

    def ScikitOrdinalEncoder(self):
        ct = ColumnTransformer([('cat_encoder', OrdinalEncoder(), [self.data.columns.get_loc(c) for c in self.features if c in self.data])], remainder='passthrough')
        self.encoded_data = np.array(ct.fit_transform(self.data.values))

    def ScikitOneHotEncoder(self):
        ct = ColumnTransformer([('cat_encoder', OneHotEncoder(), [self.data.columns.get_loc(c) for c in self.features if c in self.data])], remainder='passthrough')
        self.encoded_data = np.array(ct.fit_transform(self.data.values))    