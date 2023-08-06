from typing import List, Tuple
from pandas.core.frame import DataFrame, Series
import numpy as np


def get_constant_derivatives(
    df: DataFrame, logname: str, th: float = 0.0005
) -> Tuple[List, Series]:
    """
    Returns indices of anomalous samples based on derivatives lower than a threshold,
    and the derivatives

    Args:
        df (DataFrame): dataframe with data to analyse
        logname (str): curve to be flagged, if any
        th (float, optional): threshold to which lower values will be considered
        constant. Defaults to 0.0005.

    Returns:
        Tuple[List, Series]: list if indices of constant derivatives
        and the derivative values
    """
    df["d1"] = np.gradient(df[logname], df["DEPTH"])
    df["d2"] = np.gradient(df["d1"], df["DEPTH"])
    df["derivative"] = np.abs(df["d1"] - df["d2"])
    df["cnst_derivative"] = df["derivative"] < th
    return df[df["cnst_derivative"] == True].index, df["derivative"]


def get_constant_windows(
    df: DataFrame,
    logname: str,
    window_size: int = 10,
    min_periods: int = 5,
    th: float = 0.0005
) -> Tuple[List, Series]:
    """
    Returns indices of anomalous samples based on derivatives lower than a
    threshold within a window, and the derivatives

    Args:
        df (DataFrame): dataframe with data to analyse
        logname (str): curve to be flagged, if any
        window_size (int): size of window. Defaults to 10.
        min_periods (int): min_periods of rolling window. Defaults to 5.
        th (float, optional): threshold to which lower values will be considered
        constant. Defaults to 0.0005.

    Returns:
        Tuple[List, Series]: list if indices of constant derivatives
        and the derivative values
    """
    df["minw"] = df[logname].rolling(
        window_size, min_periods=min_periods, center=True
    ).min()
    df["maxw"] = df[logname].rolling(
        window_size, min_periods=min_periods, center=True
    ).max()
    df["window_derivative"] = np.abs(df["maxw"] - df["minw"])
    df["cnst_window"] = df["window_derivative"] < th
    return df[df["cnst_window"] == True].index, df["window_derivative"]


def get_den_flatlines(df: DataFrame, th: float = 0.002) -> List:
    """
    Returns flatlines specifically for density, where threshold was decided empirically

    Args:
        df (DataFrame): dataframe with data to analyse
        th (float, optional): threshold to which lower values will be considered constant.
        Defaults to 0.002.

    Returns:
        list: indices of anomalous density samples
    """
    if len(df["DEN"]) > 1:
        df["DEN_flat"] = np.gradient(df["DEN"])
        idx = df[
            (np.abs(df["DEN_flat"].diff()) < th) &\
            (np.abs(df["DEN_flat"].diff(-1)) < th)
        ].index
    else:
        idx = []
    return idx


def get_flatlines(
    df: DataFrame,
    logname: str,
    cols: List,
    window: int = 20,
    var_window: int = 20,
    n_cols: int = 3
) -> List:
    """
    Returns indices of anomalous values indicating flatline badlog

    Args:
        df (DataFrame): data to analyze
        logname (str): logname to find anomalies
        cols (list): list of curves to analyse logname against
        window (int, optional): window size for variance calculation.
        Defaults to 5.
        var_window (int, optional): window for rolling values. Defaults to 10.
        n_cols (int, optional): number of columns to compare with. Defaults to 2.

    Returns:
        list: indices of flatlines anomlies
    """
    # get gradients and see if one gradient is not as small as at least three other curves
    cols_grad = [f"{c}_gradient" for c in cols]
    gradient_flag = (
        df[f"{logname}_gradient"] < df[f"{logname}_gradient"].rolling(
            var_window, center=True
        ).std()
    ) & (
        np.sum(df[cols_grad] > df[cols_grad].rolling(
            var_window, center=True
        ).std(), axis=1) > n_cols
    )
    # get variance
    variance = df[[logname] + cols].rolling(window).var()
    variance_flag = (
        variance[logname] < variance[logname].rolling(
            var_window, center=True
        ).std()
    ) & (
        np.sum(variance[cols] > variance[cols].rolling(
            var_window, center=True
        ).std(), axis=1) > n_cols
    )
    # flatlines
    flatlines = gradient_flag & variance_flag
    return flatlines[flatlines == True].index


def find_start_end_indices(df_well: DataFrame) -> Tuple[int, int]:
    """
    Get absolute maximum and minimum indices between AC, ACS and DEN logs

    Args:
        df_well (DataFrame): dataframe with data to analyse

    Returns:
        Tuple[int, int]: min and max indices values
    """
    min_idx = df_well.index.max()
    max_idx = df_well.index.min()
    for col in ["AC", "ACS", "DEN"]:
        min_idx = min(min_idx, df_well[df_well[col].notna()].index.min())
        max_idx = max(max_idx, df_well[df_well[col].notna()].index.max())
    return min_idx, max_idx


def flag_flatline(
    df_well: DataFrame, y_pred: DataFrame = None, **kwargs
) -> DataFrame:
    """
    Returns flatlines indices for AC, ACS and DEN

    Args:
        df_well (DataFrame): data from one well
        y_pred (DataFrame): results. Defaults to None.

    Returns:
        DataFrame: df with added column of results
    """
    print("Method: flatline...")
    expected_curves = kwargs.get(
        "expected_curves",
        set(["DEN", "AC", "ACS", "GR", "NEU", "RDEP", "RMED"])
    )
    cols = kwargs.get("cols", expected_curves)
    ncols = kwargs.get("ncols", 3)

    for col in cols:
        df_well.loc[:, col + "_gradient"] = np.abs(np.gradient(df_well[col]))

    def run_get_flatlines(df_well, cols, ncols, **kwargs):
        window_size = kwargs.get("window", 20)
        var_window_size = kwargs.get("var_window", 20)
        ac_grad_anomalies = get_flatlines(
            df=df_well,
            logname="AC",
            cols=list(set(cols) - set(["AC"])),
            window=window_size,
            var_window=var_window_size,
            n_cols=ncols
        )
        acs_grad_anomalies = get_flatlines(
            df=df_well,
            logname="ACS",
            cols=list(set(cols) - set(["ACS"])),
            window=window_size,
            var_window=var_window_size,
            n_cols=ncols
        )
        den_grad_anomalies = get_flatlines(
            df=df_well,
            logname="DEN",
            cols=list(set(cols) - set(["DEN"])),
            window=window_size,
            var_window=var_window_size,
            n_cols=ncols
        )
        return (
            ac_grad_anomalies.tolist(),
            acs_grad_anomalies.tolist(),
            den_grad_anomalies.tolist()
        )

    ac_grad_anomalies, acs_grad_anomalies, den_grad_anomalies = [], [], []

    ac_flat_grad, ac_derivatives = get_constant_derivatives(df_well, "AC")
    acs_flat_grad, acs_derivatives = get_constant_derivatives(df_well, "ACS")
    den_flat_grad, den_derivatives = get_constant_derivatives(df_well, "DEN")

    ac_grad_anomalies.extend(ac_flat_grad)
    acs_grad_anomalies.extend(acs_flat_grad)
    den_grad_anomalies.extend(den_flat_grad)

    ac_flat_window, ac_window_grad = get_constant_windows(df_well, "AC")
    acs_flat_window, acs_window_grad = get_constant_windows(df_well, "ACS")
    den_flat_window, den_window_grad = get_constant_windows(df_well, "DEN")

    ac_grad_anomalies.extend(ac_flat_window)
    acs_grad_anomalies.extend(acs_flat_window)
    den_grad_anomalies.extend(den_flat_window)

    gen_grad_anomalies = []
    gen_grad_anomalies.extend(ac_grad_anomalies)
    gen_grad_anomalies.extend(acs_grad_anomalies)
    gen_grad_anomalies.extend(den_grad_anomalies)

    # run the function on points where there was constant window or gradient flags
    ac_grad_anomalies_main, acs_grad_anomalies_main, den_grad_anomalies_main =\
        run_get_flatlines(
            df_well, cols, ncols, **kwargs
        )

    ac_grad_anomalies_main.extend(ac_grad_anomalies)
    acs_grad_anomalies_main.extend(acs_grad_anomalies)
    den_grad_anomalies_main.extend(den_grad_anomalies)

    den_grad_anomalies_main.extend(get_den_flatlines(df_well.loc[gen_grad_anomalies]))

    '''
    # pick the start and end of well
    start_end_length = 50
    start_end_window_size = 2
    start_end_var_window_size = 2
    min_idx, max_idx = find_start_end_indices(df_well)
    start_condition = (df_well.index >= min_idx) &\
        (df_well.index <= min_idx + start_end_length)
    end_condition = (df_well.index >= max_idx - start_end_length) &\
        (df_well.index <= max_idx)

    # run the function for end points only with smaller window sizes
    df_well_ends = df_well[start_condition | end_condition]
    ac_grad_anomalies_ends, acs_grad_anomalies_ends, den_grad_anomalies_ends = run_get_flatlines(
        df_well_ends,
        cols,
        ncols,
        **{'window': start_end_window_size, 'var_window': start_end_var_window_size}
    )

    ac_grad_anomalies_main.extend(ac_grad_anomalies_ends)
    acs_grad_anomalies_main.extend(acs_grad_anomalies_ends)
    den_grad_anomalies_main.extend(den_grad_anomalies_ends)
    '''
    if y_pred is None:
        y_pred = df_well.copy()

    y_pred.loc[:, [
        "flag_flatline_gen",
        "flag_flatline_ac",
        "flag_flatline_acs",
        "flag_flatline_den"
    ]] = 0, 0, 0, 0

    y_pred.loc[ac_grad_anomalies_main, ["flag_flatline_gen", "flag_flatline_ac"]] = 1
    y_pred.loc[acs_grad_anomalies_main, ["flag_flatline_gen", "flag_flatline_acs"]] = 1
    y_pred.loc[den_grad_anomalies_main, ["flag_flatline_gen", "flag_flatline_den"]] = 1

    return y_pred
