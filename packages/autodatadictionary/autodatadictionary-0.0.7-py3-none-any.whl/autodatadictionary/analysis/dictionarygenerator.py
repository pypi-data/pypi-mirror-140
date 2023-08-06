from box import Box
import numpy as np
import pandas as pd


class DictionaryGenerator:
    """
    This class has two main methods, that handles single table data dictionary operation and combines
    the data dictionaries.
    """

    def __init__(self, config: Box):
        self.feature = config.feature
        self.unique_val_length = config.parameters.unique_val_length

    def dictionary_handler(self, df: pd.DataFrame, source: str):
        """
        More comprehensive info func
        @param source: source file name
        @param df: related dataframe
        @return: result
        """
        output = []
        for col in df.columns:
            vals = [col]  # initialize values with colname

            # Sample Value
            if self.feature.sample_value:
                idx = df[col].first_valid_index()
                sample_value = df[col].iloc[idx] if idx is not None else None
                vals.append(sample_value)

            # Source
            if self.feature.source:
                vals.append(source)

            # Non Null value count
            if self.feature.non_null_count:
                non_null_count = len(df) - np.sum(pd.isna(df[col]))
                vals.append(non_null_count)

            # Unique value count
            if self.feature.unique_count:
                unique_count = df[col].nunique()
                vals.append(unique_count)

            # Data types
            if self.feature.dtype:
                dtype = str(df[col].dtype)
                vals.append(dtype)

            # Unique val list
            if self.feature.unique_val_list:
                unique_val_list = df[col].unique()
                if len(unique_val_list) == 0:
                    unique_val_list = None
                elif len(unique_val_list) > self.unique_val_length:
                    unique_val_list = unique_val_list[0:self.unique_val_length]
                unique_val_list = ', '.join(map(str, unique_val_list))
                vals.append(unique_val_list)

            output.append(vals)

        output = pd.DataFrame(output)
        cols = ['column_name']
        if self.feature.sample_value:
            cols.append("sample_value")
        if self.feature.source:
            cols.append("source")
        if self.feature.non_null_count:
            cols.append("non_null_count")
        if self.feature.unique_count:
            cols.append("unique_count")
        if self.feature.dtype:
            cols.append("dtype")
        if self.feature.unique_val_list:
            cols.append("unique_val_list")

        output.columns = cols
        return output

    def all_dictionary_handler(self, df_list) -> pd.DataFrame:
        """
        Gets the tables and generates data dictionary
        @param df_list: List of dataframes that will be processed
        @return: Data Dictionary of the selected tables
        """
        results = pd.DataFrame()
        for df in df_list:
            source = df.attrs["source"] if "source" in df.attrs else None
            results = results.append(self.dictionary_handler(df=df, source=source))

        return results
