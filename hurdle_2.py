import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LinearRegression, LogisticRegression

class Hurdle(BaseEstimator, ClassifierMixin):

    def __init__(self, classifier=LogisticRegression(),
                 regressor=LinearRegression()):
        '''
        '''
        # Parameters
        self.classifier = classifier
        self.regressor = regressor
        # Attributes
        self.y_class_ = None
        self.pred_x_class_ = None
        self.pred_x_reg_ = None
        self.pred_x_class_proba_ = None

    def fit(self, X, y):
        '''
        '''
        self.y_class_ = (y > 0).astype(int)
        self.classifier.fit(X, self.y_class_)
        self.regressor.fit(X[self.y_class_ == 1], y[self.y_class_ == 1])

    def predict(self, X, y=None):
        '''
        '''
        self.pred_x_class_ = self.classifier.predict(X)
        self.pred_x_reg_ = self.regressor.predict(X)
        return self.pred_x_class_ * self.pred_x_reg_

    def predict_expected_value(self, X, y=None):
        '''
        '''
        self.pred_x_class_proba_ = self.classifier.predict_proba(X)
        self.pred_x_reg_ = self.regressor.predict(X)
        return self.pred_x_class_proba_[:,1] * self.pred_x_reg_
