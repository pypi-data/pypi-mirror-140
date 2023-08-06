import pandas as pd
from typing import List

from feature_test.input_errors import InputError


class Utils:
    def __init__(self):
        self.get_columns()
        self.exclude_columns()
        self._check_df_operand()
        self._check_str_operand()
        self._check_str_in_df()

    @classmethod
    def get_columns(self, X: pd.DataFrame) -> List:
        """
        Returns a list of column names.
        """
        return list(X.columns)

    @classmethod
    def exclude_columns(self, X: pd.DataFrame, columns: List) -> pd.DataFrame:
        """
        Exclude a list of columns from a dataframe.
        """
        return X.drop(columns, axis=1)

    @classmethod
    def _check_df_operand(self, operand: pd.DataFrame) -> None:
        """
        Check if the operand is a dataframe.
        """
        if not isinstance(operand, pd.DataFrame):
            raise InputError(f'"{operand}" is not a dataframe.')

    @classmethod
    def _check_str_operand(self, operand: str) -> None:
        """
        Check if the operand is a string.
        """
        if not isinstance(operand, str):
            raise InputError(f'"{operand}" is not a string.')

    @classmethod
    def _check_str_in_df(self, X: pd.DataFrame, operand: str) -> None:
        """
        Check if the operand is a column in the dataframe.
        """
        if operand not in X.columns:
            raise InputError(f'"{operand}" is not a column in the dataframe.')

