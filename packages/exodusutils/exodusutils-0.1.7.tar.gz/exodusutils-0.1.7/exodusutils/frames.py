from typing import List, Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel

from exodusutils import internal


class TrainFrames(BaseModel):
    """
    A collection of dataframes. The validation frame and test frame are optional.
    """

    train: pd.DataFrame
    validation: Optional[pd.DataFrame]
    test: Optional[pd.DataFrame]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def iid_without_test(cls, df: pd.DataFrame, validation_percentage: float):
        """
        Create `TrainFrames` for an IID model algoritghm.

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to split into train and test.
        validation_percentage : float
            validation percentage

        Returns
        -------
        TrainFrames, without test frame. Useful when training the final model.
        """
        train, validation = internal.train_validation_split(df, validation_percentage)
        return cls(train=train, validation=validation, test=None)


class CVFrames(BaseModel):
    """
    A list of `TrainFrames`. User should not initialize this class directly, instead they should \
use the classmethod `iid`.
    """

    frames: List[TrainFrames]

    @classmethod
    def iid(
        cls,
        df: pd.DataFrame,
        nfolds: int,
        validation_percentage: float,
        shuffle: bool = False,
    ):
        """
        Create CV frames for an IID experiment.

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to split to CV frames.
        nfolds : int
            nfolds
        validation_percentage : float
            validation percentage
        shuffle : bool
            Whether we want to shuffle the frame before splitting it.

        Returns
        -------
        CVFrames
        """
        if shuffle:
            df = df.sample(frac=1.0).reset_index(drop=True)
        frames = []
        # TODO use sklearn.model_selection.KFold?
        for fold_indices in np.array_split(np.arange(df.shape[0]), nfolds):
            test_range = df.index.isin(fold_indices)
            train, validation = internal.train_validation_split(
                pd.DataFrame(df[~test_range]), validation_percentage
            )
            frames.append(
                TrainFrames(train=train, validation=validation, test=df[test_range])
            )
        return cls(frames=frames)
