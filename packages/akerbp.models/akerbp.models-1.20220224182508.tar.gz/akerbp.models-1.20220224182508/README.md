## AkerBP.models

Machine Learning Models for Petrophysics.

- Classification Models
    - Wrapper for XGBoost classifier
    - Hierarchical and nested models for lithology (outdated)
- Regression Models
    - Wrapper for XGBoost regressor
- Rule-based models - several methods for badlog detection, including:
    - Crossplots outlier detection (supported: OCSVM, Elliptic envelope and Isolation Forest)
    - Logtrend, outliers, DENC and washout (based on the crossplots above)
    - Flatline
    - Resistivities
    - Casing
    - UMAP 3D segmentation
    - crosscorrelation

## How to use

Example of how to use the badlog model class.

        import akerbp.models.rule_based_models as models
        # instantiate a badlog model object
        model = models.BadlogModel()

        # define which methods to run for badlog detection and run prediction
        # on data from one well
        methods = ['casing', 'flatline', 'dencorr', 'logtrend']
        model_predictions = model.predict(
            df_well,
            methods=methods,
            settings=None,
            mappings=None,
            folder_path=None
        )

Example of how to use the regression model class (wrapper of XGBoost).

        import akerbp.models.regression_models as models
        # instantiate an XGBoost regression model object with parameters as model_settings
        reg_model = models.XGBoostRegressionModel(
            settings=model_settings,
            model_path=folder_path
        )
        results = reg_model.predict(df_well)
        reg_model.save()  # it saves the model to specified folder path

This library is closely related and advised to be used together with [akerbp.mlpet](https://pypi.org/project/akerbp.mlpet/), also developed by AkerBP.

### Rule-based models

The dataframe returned from running predictions on data from one well will contain new columns named in the following format "TYPE_METHOD_VAR", where:

- TYPE: either "flag" or "agg". Flag can be 0 or 1 for regular or badlog samples respectively. Agg is the aggregation type, or score. It indicates how anomalous is the sample (used as a way for the user to set thresholds per method).
- METHOD: method for the column flag. It should be as in the methods given to the predictions. An exception is the crossplots method, that will instead have [vpden, vpvs, aivpvs] as output method column names.
- VAR: variable or curve that the column flags. It should be one of the following: den, ac, acs, rmed, rdep, rmic, calib_bs (one column only).


## License

AkerBP.models Copyright 2021 AkerBP ASA

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
