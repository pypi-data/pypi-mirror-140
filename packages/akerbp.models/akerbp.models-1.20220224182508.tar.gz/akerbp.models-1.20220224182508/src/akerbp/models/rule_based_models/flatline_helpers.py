from typing import List
import pandas as pd
from pandas.core.frame import DataFrame, Series
import numpy as np


def keepNLargestGroups(df_: pd.DataFrame, n: int) -> List:
    """
    Returns flatlines indices for AC, ACS and DEN

    Args:
        df_ (Series): series with flags
        n (int): number of large groups of consecutive anomalies to keep

    Returns:
        List: processed flags
    """
    df = pd.DataFrame(df_.astype(int).values, columns=['flatline'])
    df['groups'] = df['flatline'].ne(df['flatline'].shift()).cumsum()
    count_groups = df[df.flatline == 1].groups.value_counts()
    count_groups = count_groups[:n].index.tolist()
    df['large_group'] = False
    df.loc[df.groups.isin(count_groups), 'large_group'] = True
    return df.large_group.values


def detect_flatlines(
    df: pd.DataFrame,
    col: str,
    lim: float,
    window: int = 5,
    n_largest_groups: int = 10
) -> List:
    """
    Returns flatlines indices given log

    Args:
        df (DataFrame): dataframe with log to be processed(col) and depth
        col (str): column to which find flags
        lim (float): threshold for consedeiring anomalous derivatives
        window (int): size of window to compared single point to
        n_largest_groups (int): number of large groups of consecutive anomalies to keep

    Returns:
        List: flags flor given column
    """

    # get sampling rate
    vc = df.DEPTH.diff().value_counts(normalize=True)
    sampling_rate = (vc * vc.index).sum()
    # get second derivative
    df['d2'] = df[col].diff().diff().abs() / sampling_rate
    # detect flatlines based on derivative
    df['d2'] = ((df['d2'] < lim).multiply(
        df['d2'].rolling(window, center=True).median().isnull())
    ) | (
        df['d2'].rolling(window, center=True).median() < lim
    )
    # get largest groups to avoid false positives
    df['d2'] = keepNLargestGroups(df['d2'], n_largest_groups)
    df['d2'] = np.where(df['d2'], 1, 0)
    return df['d2'].values  # which values are correct, d2 or v2? is v2 coming from d2?


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
    default_kwargs = {
        "n_largest_groups": 10,
        "den_lim": 0.01,
        "ac_lim": 0.005,
        "acs_lim": 0.01
    }
    user_kwargs = kwargs.get("flatline_params", {})
    kwargs = {}
    for k, v in default_kwargs.items():
        kwargs[k] = user_kwargs.get(k, v)

    if y_pred is None:
        y_pred = df_well.copy()

    y_pred.loc[:, [
        "flag_flatline_gen",
        "flag_flatline_ac",
        "flag_flatline_acs",
        "flag_flatline_den"
    ]] = 0, 0, 0, 0

    for col in ["AC", "ACS", "DEN"]:
        y_pred.loc[:, [f"flag_flatline_{col.lower()}"]] = detect_flatlines(
            df_well[["DEPTH", col]],
            col,
            kwargs[f"{col.lower()}_lim"],
            n_largest_groups=kwargs["n_largest_groups"]
        )
        y_pred.loc[:, "flag_flatline_gen"] =\
            y_pred["flag_flatline_gen"] | y_pred[f"flag_flatline_{col.lower()}"]
    return y_pred
