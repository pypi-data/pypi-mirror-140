from typing import List
import numpy as np
from pandas.core.frame import DataFrame
from akerbp.models.rule_based_models import BS_helpers


def flag_bad_den_shallow(df_well: DataFrame) -> List[int]:
    """
    Looks for parial DEN measurement for the same BS
    in the shallow end of the well and mark those DEN measurements as bad

    Args:
        df_well (DataFrame): well data

    Returns:
        list: indices with bad DEN
    """
    df_well = BS_helpers.find_BS_jumps(df_well)
    dencorr_casing = []
    # get the index of the first DEN value
    first_DEN_idx = df_well[df_well["DEN"].notna()].index.min()
    if not np.isnan(first_DEN_idx):
        first_BS_region = df_well.loc[first_DEN_idx, "BS_region"]
        first_region_idx = df_well[df_well["BS_region"] == first_BS_region].index.min()
        bad_region_length = len(
            df_well[df_well["BS_region"] == first_BS_region]["DEN"].dropna()
        )
        if (first_region_idx < first_DEN_idx) and (bad_region_length < 1000):
            dencorr_casing = df_well[df_well["BS_region"] == first_BS_region].index
    return dencorr_casing


def flag_bad_den_at_jump(df_well: DataFrame) -> List[int]:
    """
    Looks around the regions where BS value changes, if there are missing DEN
    measurements, marks X measurements before and after that as potentioally bad

    Args:
        df_well (DataFrame): well data

    Returns:
        list: indices with bad DEN
    """
    df_well = BS_helpers.find_BS_jumps(df_well)
    bad_den_idx = []
    for region in df_well["BS_region"].unique():
        min_region_idx = df_well[df_well["BS_region"] == region].index.min()
        min_den_idx = df_well[
            df_well["BS_region"] == region
        ]["DEN"].dropna().index.min()
        if min_den_idx > min_region_idx:
            bad_den_idx.extend(df_well[
                df_well["BS_region"] == region]["DEN"].dropna().head(20).index.tolist()
            )
        max_region_idx = df_well[df_well["BS_region"] == region].index.max()
        max_den_idx = df_well[
            df_well["BS_region"] == region
        ]["DEN"].dropna().index.max()
        if max_den_idx < max_region_idx:
            bad_den_idx.extend(df_well[
                df_well["BS_region"] == region]["DEN"].dropna().tail(20).index.tolist()
            )
    return bad_den_idx


def flag_casing(df_well: DataFrame, y_pred: DataFrame = None, **kwargs) -> DataFrame:
    """
    Returns anomalous DEN due to invalid measurements inside the casing
    combining the findings of flag_bad_den_shallow() and flag_bad_den_at_jump()
    function

    Args:
        df_well (DataFrame): well data
        y_pred (DataFrame): dataframe to append the flag columns
        ("flag_casing_gen" and "flag_casing_den") to.
        If set to None, the columns are added to a copy of df_well - default: None

    Returns:
        DataFrame: y_pred
    """
    print("Method: casing...")
    bad_den_casing = []
    bad_den_casing.extend(flag_bad_den_shallow(df_well))
    bad_den_casing.extend(flag_bad_den_at_jump(df_well))
    if y_pred is None:
        y_pred = df_well.copy()
    y_pred.loc[:, ["flag_casing_gen", "flag_casing_den"]] = 0, 0
    y_pred.loc[bad_den_casing, ["flag_casing_gen", "flag_casing_den"]] = 1
    return y_pred
