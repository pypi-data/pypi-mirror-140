from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from exodusutils import internal


def to_numeric_features_df(df: pd.DataFrame, target: str) -> pd.DataFrame:
    """
    Extracts the numeric features from the dataframe, and return them as a new dataframe.

    The numeric features include:
        - Columns declared with `data_type == DataType.double` in `feature_types`
        - The encoded columns (i.e. the dummy columns in one-hot encoding, or the
                columns that have been label encoded)

    This is the `X` dataframe used in TPOT.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe.
    target : str
        Target column name.

    Returns
    -------
    The numeric features as a dataframe.
    """
    return pd.DataFrame(df[internal.get_numeric_features(df, target)])


def apply_label_encoders(
    df: pd.DataFrame, encoders: Dict[str, LabelEncoder]
) -> pd.DataFrame:
    """
    Apply label encoders to `df`. If your model makes use of `label_encoding` method during training,
    then during prediction this should be performed on the prediction dataframe.
    """
    df = df.copy()
    for col, encoder in encoders.items():
        df.loc[
            ~df[col].isin(encoder.classes_), [col]
        ] = np.nan  # unseen values in training data
        df.loc[df[col].notnull(), [col]] = encoder.transform(
            df.loc[df[col].notnull()][col]
        )
        df[col] = pd.to_numeric(pd.Series(df[col]), errors="coerce")
    return df


def apply_one_hot_encoding(
    df: pd.DataFrame, categorical_columns_in_training: List[str]
) -> pd.DataFrame:
    """
    Apply one-hot encoding to `df`. If your model makes use of `one_hot_encoding` method during training,
    then during prediction this should be performed on the prediction dataframe.
    """
    categorical_columns_in_testing = internal.get_columns(df, object)
    dummy = pd.get_dummies(df, columns=categorical_columns_in_testing, dtype=np.int64)
    for c in categorical_columns_in_training:
        if c not in categorical_columns_in_testing:
            dummy[c] = 0
    return dummy

def remove_invalid_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes the invalid values from the dataframe.

    The invalid values are:
    - `float("nan")` or `np.nan` in numeric columns
    - `""` in other types of columns
    """
    return pd.DataFrame(df.replace("", np.nan).dropna())

def remove_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes all columns of dtype `datetime64`
    """
    return df.drop(internal.get_columns(df, np.datetime64), axis=1)
