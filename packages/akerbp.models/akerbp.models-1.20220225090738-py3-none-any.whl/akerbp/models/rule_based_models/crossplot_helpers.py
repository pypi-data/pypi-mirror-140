from typing import List, Tuple, Any
from pandas.core.frame import DataFrame
import numpy as np
import pandas as pd
from sklearn.covariance import EllipticEnvelope
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from pyod.utils.utility import standardizer
from akerbp.mlpet import Dataset


def get_params(**kwargs) -> Tuple:
    """
    Gets parameters for the outlier detection algorithms

    Returns:
        tuple: dictionaries with parameters per method
    """
    SVM_params = {"nu": kwargs.get("SVM_nu", 0.01)}
    IsoFor_params = {
        "n_estimators": kwargs.get("IsoFor_n_estimators", 50),
        "contamination": kwargs.get("IsoFor_contamination", 0.01),
        "random_state": kwargs.get("IsoFor_random_state", 0),
    }
    Abod_parameters = {"contamination": 0.1, "n_neighbors": 10}
    EliEnv_parameters = {"contamination": 0.05, "random_state": 0}
    Abod_parameters = {"contamination": 0.1, "n_neighbors": 10}
    EliEnv_parameters = {"contamination": 0.05, "random_state": 0}
    return SVM_params, IsoFor_params, Abod_parameters, EliEnv_parameters


def find_crossplot_scores(
    df: DataFrame, x: str, y: str, algo: str = "comb", **kwargs
) -> List:
    """
    Find anomalies based on the crossplots of x vs. y

    Args:
        df (DataFrame): dataframe with data from one well
        x (str): column for axis x in crossplot
        y (str): column for axis y in crossplot
        algo (str, optional): which algorithm to use. Defaults to 'comb'

    Returns:
        list: list with indices of anomalous samples
    """
    algo = algo.lower()
    df = df[(df[x] != 0) & (df[y] != 0)].copy()
    tmp = df[[x, y]].dropna().copy()
    anomal_idx = []
    method_scores = dict()
    return_scores = dict()
    SVM_params, IsoFor_params, _, EliEnv_parameters = get_params(**kwargs)
    # if there are not even 10 samples we return
    if len(tmp) < 10:
        return [], {}, tmp.index
    if (algo == "comb") or (algo == "elienv"):
        try:
            elienv = EllipticEnvelope(
                contamination=EliEnv_parameters["contamination"],
                random_state=EliEnv_parameters["random_state"],
            ).fit(tmp[[x, y]])
            preds2 = elienv.predict(tmp[[x, y]])
            original_scores = elienv.score_samples(tmp[[x, y]])
        except Exception as e:
            # FIXME: elliptic envelope throws covariance error when not so many
            # samples. # Quick fix for now.
            preds2 = np.zeros(len(tmp))
            original_scores = np.zeros(len(tmp))
            print(e)
        if algo == "elienv":
            preds = preds2
        method_scores["elienv"] = np.abs(standardizer(original_scores.reshape(-1, 1)))

    if (algo == "comb") or (algo == "svm"):
        svm = OneClassSVM(kernel="rbf", gamma="scale", nu=SVM_params["nu"]).fit(
            tmp[[x, y]]
        )
        preds3 = svm.predict(tmp[[x, y]])
        if algo == "svm":
            preds = preds3
        original_scores = svm.score_samples(tmp[[x, y]])
        method_scores["SVM"] = np.abs(standardizer(original_scores.reshape(-1, 1)))

    if (algo == "comb") or (algo == "isofor"):
        ifo = IsolationForest(
            n_estimators=IsoFor_params["n_estimators"],
            contamination=IsoFor_params["contamination"],
            random_state=IsoFor_params["random_state"],
        ).fit(tmp[[x, y]])
        preds4 = ifo.predict(tmp[[x, y]])
        if algo == "isofor":
            preds = preds4
        original_scores = ifo.score_samples(tmp[[x, y]])
        method_scores["IsoFor"] = standardizer(original_scores.reshape(-1, 1))

    if algo == "comb":
        preds = (
            np.where(preds2 == -1, 1, 0)
            + np.where(preds3 == -1, 1, 0)
            + np.where(preds4 == -1, 1, 0)
        )
        tmp["pred"] = np.where(preds > 1, 1, 0)
    else:
        tmp["pred"] = np.where(preds == -1, 1, 0)

    for k, v in method_scores.items():
        return_scores[k] = v[:, 0]

    return_scores = pd.DataFrame(return_scores)
    return_scores["agg"] = return_scores.mean(axis=1)
    anomal_idx.append(list(tmp[tmp.pred == 1].index))
    return sum(anomal_idx, []), return_scores, tmp.index


def train_crossplot(**kwargs):
    pass


def get_proba_predictions(
    X: DataFrame, y: DataFrame, bad_logs: DataFrame, model: Any, cp_name: str
) -> DataFrame:
    """
    Add to the dataframe the score results for each of the bad anomalies.

    Args:
        X (DataFrame): dataframe for prediction on
        y (DataFrame): datafrrame with columns to populate results
        bad_logs (DataFrame): bad log samples dataframe
        model (Any): trained model with Scikit learn or XGBoost model
        cp_name (str): crossplot name

    Returns:
        y: DataFrame populated with results
    """
    cp_preds = model.predict_proba(X)
    if cp_name == "vp_den":
        y.loc[bad_logs.index, "score_vpden_ac"] = cp_preds[:, 0]
        y.loc[bad_logs.index, "score_vpden_den"] = cp_preds[:, 1]
    elif cp_name == "vp_vs":
        y.loc[bad_logs.index, "score_vpvs_ac"] = cp_preds[:, 0]
        y.loc[bad_logs.index, "score_vpvs_acs"] = cp_preds[:, 1]
    elif cp_name == "ai_vpvs":
        y.loc[bad_logs.index, "score_aivpvs_ac"] = cp_preds[:, 0]
        y.loc[bad_logs.index, "score_aivpvs_acs"] = cp_preds[:, 1]
        y.loc[bad_logs.index, "score_aivpvs_den"] = cp_preds[:, 2]
    return y


def get_class_predictions(
    X: DataFrame, y: DataFrame, bad_logs: DataFrame, model: Any, cp_name: str
) -> DataFrame:
    """
    Add to the dataframe the class results for each of the bad anomalies.

    Args:
        X (DataFrame): dataframe for prediction on
        y (DataFrame): datafrrame with columns to populate results
        bad_logs (DataFrame): bad log samples dataframe
        models (dict): dictionary with models per cp
        cp_name (str): crossplot name

    Returns:
        y: pd.DataFrame populated with results
    """
    cp_preds = model.predict(X)
    y["tmp"] = 0
    y.loc[bad_logs.index, "tmp"] = cp_preds
    # Map predictions depending on which crossplot they come from
    if cp_name == "vp_den":
        y.loc[y.tmp.isin([1, 3]), "flag_vpden_ac"] = 1
        y.loc[y.tmp.isin([2, 3]), "flag_vpden_den"] = 1
    elif cp_name == "vp_vs":
        y.loc[y.tmp.isin([1, 3]), "flag_vpvs_ac"] = 1
        y.loc[y.tmp.isin([2, 3]), "flag_vpvs_acs"] = 1
    elif cp_name == "ai_vpvs":
        y.loc[y.tmp.isin([4, 5, 6, 7]), "flag_aivpvs_den"] = 1
        y.loc[y.tmp.isin([1, 3, 5, 7]), "flag_aivpvs_ac"] = 1
        y.loc[y.tmp.isin([2, 4, 6, 7]), "flag_aivpvs_acs"] = 1
    return y


def flag_well_crossplots(
    X: DataFrame, x: str, y: str, algo: str, cp_name: str, **kwargs
) -> Tuple[DataFrame, List]:
    """
    Returns anomalous indices of crossplots between x and y.
    Used by other methods.

    Args:
        X (DataFrame): dataframe with data to flag
        x (str): colum for x-axis in crossplot
        y (str): column for y-axis in crossplot
        algo (str): comb or specic algorithm to run
        cp_name (str): crossplot name

    Returns:
        Tuple[DataFrame, List]: dataframe with flagged samples and list
        of anamalous indices
    """
    res = dict(
        zip(
            ["anomalies", "scores", "idx"],
            find_crossplot_scores(X, x, y, algo=algo, **kwargs),
        )
    )
    for comb_method, scs in res["scores"].items():
        method_col = f"{comb_method}_{cp_name}"
        X.loc[res["idx"], method_col] = scs.values
        X[method_col].fillna(0, inplace=True)
    return X, res["anomalies"]


def flag_crossplots(
    X: DataFrame, x: str, y: str, algo: str, cp_name: str, **kwargs
) -> Tuple[DataFrame, List]:
    """
    Returns anomalous indices of crossplots between x and y

    Args:
        X (DataFrame): dataframe with data to flag
        x (str): colum for x-axis in crossplot
        y (str): column for y-axis in crossplot
        algo (str): comb or specic algorithm to run
        cp_name (str): crossplot name

    Returns:
        Tuple[DataFrame, List]: dataframe with flagged samples and list
        of anamalous indices
    """
    anomalies = []
    for lsu in X["GROUP"].unique():
        lsu_data = X[X["GROUP"] == lsu]
        res = dict(
            zip(
                ["anomalies", "scores", "idx"],
                find_crossplot_scores(lsu_data, x, y, algo=algo, **kwargs),
            )
        )
        for comb_method, scs in res["scores"].items():
            method_col = f"{comb_method}_{cp_name}"
            X.loc[res["idx"], method_col] = scs.values
            X[method_col].fillna(0, inplace=True)
        anomalies.extend(res["anomalies"])
    return X, anomalies


def classify_badlog(
    y: DataFrame, cp_name: str, ds: Dataset, model: Any
) -> DataFrame:
    """
    Returns both probabilities and class predictions of anomalous indices

    Args:
        y (DataFrame): dataframe with data to flag
        cp_name (str): crossplot name
        ds (Dataset): dataset object from akerbp.mlpet
        shift normalization
        model (Any): model form Scikit learn or XGBoost

    Returns:
        DataFrame: dataframe with columns of results added
    """
    bad_logs = ds.df_original[ds.df_original["flag_crossplot_gen"] != 0]
    # if no badlogs, dont do anything
    if len(bad_logs) <= 1:
        return y
    # update the default preprocessing pipeline with the specifics required by this model
    preprocess_kwargs = {
        "set_as_nan": {},
        "remove_outliers": {},
        "add_petrophysical_features": {
                    "rolling_window_size": 1000,
                    "quant_ss":0.02
        },
        "add_log_features": {},
        "process_wells": {},
        "fillna_with_fillers": {},
        "encode_columns": {}
    }
    feats = model.model.get_booster().feature_names
    # Preprocess data
    df_preprocessed = ds.preprocess(
        ds.df_original.loc[bad_logs.index],
        **preprocess_kwargs
    )

    # scores
    y_scores = get_proba_predictions(
        df_preprocessed[feats], y, bad_logs, model, cp_name
    )
    y[y_scores.columns] = y_scores
    # flags
    y_flags = get_class_predictions(df_preprocessed[feats], y, bad_logs, model, cp_name)
    y[y_flags.columns] = y_flags
    return y


def flag_crossplot(
    X_pred: DataFrame,
    cp_names: List,
    datasets: dict,
    models: dict,
    **kwargs,
) -> DataFrame:
    """
    Main function to flag pre defined crossplots

    Args:
        X_pred (DataFrame): dataframe with data from one well
        cp_names (List): list of crossplots to run
        datasets (dict): dictionary with Dataset obejcts for each crossplot model
        models (dict): dictionary with models for each crossplot

    Returns:
        DataFrame: dataframe with added columns with flag results
    """
    print("Method: crossplot - general...")
    # FIXME! The shouldn't preferably be hard-coded.
    outlier_methods = ["EliEnv", "SVM", "IsoFor"]
    for cp_name in cp_names:
        for method in outlier_methods:
            X_pred[f"{method}_{cp_name}"] = 0.0

    # get anomalies per crossplot and their scores
    vp_den_anomalies, ai_vpvs_anomalies, vp_vs_anomalies = [], [], []
    X_pred, vp_den_anomalies = flag_crossplots(
        X_pred, "VP", "DEN", "comb", "vp_den", **kwargs
    )
    X_pred, ai_vpvs_anomalies = flag_crossplots(
        X_pred, "AI", "VPVS", "comb", "ai_vpvs", **kwargs
    )
    X_pred, vp_vs_anomalies = flag_crossplots(
        X_pred, "VP", "VS", "comb", "vp_vs", **kwargs
    )

    y = X_pred.copy()
    y.loc[
        :,
        [
            "flag_vpden_ac",
            "flag_vpvs_ac",
            "flag_aivpvs_ac",
            "flag_vpvs_acs",
            "flag_aivpvs_acs",
            "flag_vpden_den",
            "flag_aivpvs_den",
            "score_vpden_ac",
            "score_vpden_den",
            "score_vpvs_ac",
            "score_vpvs_acs",
            "score_aivpvs_ac",
            "score_aivpvs_acs",
            "score_aivpvs_den"
        ],
    ] = 0

    pred_gen_cols = [
        "flag_crossplot_gen",
        "flag_vpden_gen",
        "flag_aivpvs_gen",
        "flag_vpvs_gen",
    ]
    y.loc[:, pred_gen_cols] = 0, 0, 0, 0
    y.loc[vp_den_anomalies, ["flag_crossplot_gen", "flag_vpden_gen"]] = 1
    y.loc[ai_vpvs_anomalies, ["flag_crossplot_gen", "flag_aivpvs_gen"]] = 1
    y.loc[vp_vs_anomalies, ["flag_crossplot_gen", "flag_vpvs_gen"]] = 1

    # Add the general crossplot flags to X_pred(to use as features in the model)
    X_pred[pred_gen_cols] = y[pred_gen_cols]

    # Run the anomalous samples through the relevant trained model and get predictions
    # Preprocessing using key_wells will need the well_name column,
    # but the value is unimportant
    X_pred["well_name"] = "dummy"
    for cp_name in cp_names:
        print(f"Method: crossplot - {cp_name}...")
        ds = datasets[cp_name]
        ds.save_df_to_cls(X_pred)
        y = classify_badlog(y, cp_name, ds, models[cp_name])
    y = y.fillna(0)
    return y
