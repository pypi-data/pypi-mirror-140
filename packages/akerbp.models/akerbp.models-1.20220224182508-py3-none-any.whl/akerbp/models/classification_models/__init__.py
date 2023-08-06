from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import class_weight
import xgboost

from akerbp.models import Model


class ClassificationModel(Model):
    """
    Wrapper class for classification models
    """
    def predict_proba(self, X: Any) -> np.ndarray:
        """
        Returns probability of each sample to be in a certain class

        Args:
            X (dict or DataFrame): features of each sample

        Raises:
            ValueError: raises an error when no model is found

        Returns:
            np.array: array with prediction probabilities of each class
        """
        if self.model is None:
            m = ("Model must be trained or loaded from file "
                 "before predict_proba can be run!")
            raise ValueError(m)
        self.X_pred = X
        self._validate_x_pred()
        if hasattr(self, '_validate_features'):
            self._validate_features()
        return self.model.predict_proba(self.X_pred)

    def _prepare_sample_weights(self, targets: pd.Series):
        """
        Weight samples if that is specified by the user, otherwise all samples
        have same weight.

        Args:
            targets (pd.Series): series with target values
        """
        if self.use_class_weights:
            weights = class_weight.compute_class_weight(
                'balanced', classes=np.unique(targets), y=targets.values
            )
            sw = targets.copy()
            classes = sw.unique()
            zip_iterator = zip(classes, weights)
            self.class_weights = dict(zip_iterator)
            sw = sw.replace(self.class_weights)
            self.sample_weights = sw.values
        else:
            self.sample_weights = np.ones_like(targets)


class XGBoostClassificationModel(ClassificationModel):
    """
    XGBoost classifier wrapper. Inherits ClassificationModel methods.
    """
    def __init__(
        self, settings: Dict, model_path: str, load: bool = True
    ):
        self.settings = settings
        for key, val in settings.items():
            setattr(self, key, val)
        self.model_path = model_path
        self._handle_model_path()
        if load:
            self.model = joblib.load(self.model_file_path)
            print('Model successfully loaded from ', self.model_file_path)
            self.le = joblib.load(self.le_file_path)
            print('LabelEncoder successfully loaded from ', self.le_file_path)

    def _validate_features(self):
        """
        Check that the features in the model match the features provided in
        the data (including their order)

        Raises:
            ValueError: raises an error if providd features are not the same as
            expected by the model
        """
        self.model_features = self.model.get_booster().feature_names
        if sorted(self.model_features) != sorted(self.X_pred.columns.values):
            m = (
                "Error in provided features. "
                f"Expected: {list(self.model_features)}"
                f"Provided: {list(self.X_pred.columns)}"
            )
            raise ValueError(m)
        self.X_pred = self.X_pred[self.model_features]

    def predict(self, X):
        return super().predict(X, validate_features=True).astype('int')

    def train(self, df, targets, **kwargs):
        """
        Trains on the data given in the provided dataframe and targets.
        The curves of the model must be present in the dataframe.

        Args:
            df (pd.DataFrame):  dataframe of samples and features
            targets ([type]): List of integers of the same length as the number of
            rows in df
        """
        self._prepare_sample_weights(targets)
        self.le = LabelEncoder()
        targets = self.le.fit_transform(targets)
        self.model = xgboost.XGBRFClassifier(**self.model_parameters)
        self.model.fit(df, targets, sample_weight=self.sample_weights, **kwargs)
