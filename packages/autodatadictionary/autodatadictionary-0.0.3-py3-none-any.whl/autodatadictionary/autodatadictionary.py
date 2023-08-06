import pandas as pd
from box import Box

from src.autodatadictionary.analysis.dictionarygenerator import DictionaryGenerator
from src.autodatadictionary.preperation.dataprep import DataPrep


def to_dictionary_from_file(paths: [str], sep: str = ',',
                            sample_value: bool = True, source: bool = True, non_null_count: bool = True,
                            unique_count: bool = True, dtype: bool = True, unique_val_list: bool = True,
                            unique_val_length: int = 15) -> pd.DataFrame:
    """
    Generates data dictionary from files, returns the dictionary as a dataframe
    @param paths: Paths of the files that will be processed
    @param sep: CSV separator character
    @param sample_value: Flag, whether to include sample value from data
    @param source: Flag, whether to include source
    @param non_null_count: Flag, whether to include non_null_count
    @param unique_count: Flag, whether to include unique_count
    @param dtype: Flag, whether to include dtypes
    @param unique_val_list: Flag, whether to include unique_val_list
    @param unique_val_length: How many unique values to show, if unique_val_list is True
    @return: Data Dictionary as a dataframe
    """
    config = Box({"feature": {"sample_value": sample_value, "source": source, 'non_null_count': non_null_count,
                              "unique_count": unique_count, "dtype": dtype, 'unique_val_list': unique_val_list},
                  "parameters": {"unique_val_length": unique_val_length},
                  "data": {"paths": paths, "separator": sep}
                  })

    dp = DataPrep(config)
    data_list = dp.load_csv_data()

    dg = DictionaryGenerator(config)
    output = dg.all_dictionary_handler(data_list)
    return output


def to_dictionary_from_db(sql_alchemy_connection_string: str, schema: str, table_names: [str] = None,
                          row_limit: int = None,
                          sample_value: bool = True, source: bool = True, non_null_count: bool = True,
                          unique_count: bool = True, dtype: bool = True, unique_val_list: bool = True,
                          unique_val_length: int = 15):
    """
    Generates data dictionary from database, returns the dictionary as a dataframe
    @param sql_alchemy_connection_string: SQL Alchemy Connection string to be used to create sql alchemy engine
    for db connection
    @param schema: DB schema to work in
    @param table_names: Names of the tables to be included in the Data Dictionary
    @param row_limit: Limit the number of rows to be processed to decrease the computational time
    @param sample_value: Flag, whether to include sample value from data
    @param source: Flag, whether to include source
    @param non_null_count: Flag, whether to include non_null_count
    @param unique_count: Flag, whether to include unique_count
    @param dtype: Flag, whether to include dtypes
    @param unique_val_list: Flag, whether to include unique_val_list
    @param unique_val_length: How many unique values to show, if unique_val_list is True
    @return: Data Dictionary as a dataframe
    """
    config = Box({"db": {"sql_alchemy_connection_string": sql_alchemy_connection_string, "schema": schema,
                         "row_limit": row_limit,
                         "table_names": table_names},
                  "feature": {"sample_value": sample_value, "source": source, 'non_null_count': non_null_count,
                              "unique_count": unique_count, "dtype": dtype, 'unique_val_list': unique_val_list},
                  "parameters": {"unique_val_length": unique_val_length},
                  })

    dp = DataPrep(config)
    data_list = dp.load_db_data()

    dg = DictionaryGenerator(config)
    output = dg.all_dictionary_handler(data_list)
    return output
