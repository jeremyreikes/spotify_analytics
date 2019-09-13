import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression

class HurdleLinearRegression():
    """Implements linear regression with a hurdle at 0.
    """

    def __init__(self):
        self.logistic = LogisticRegression()
        self.linear = LinearRegression()

    def fit(self, X, y):
        self.logistic.fit(X, y>0)
        self.linear.fit(X[y>0], y[y>0])
        return self

    def predict(self, X):
        p = self.logistic.predict_proba(X)
        y_hat = self.linear.predict(X)
        return p * y_hat
