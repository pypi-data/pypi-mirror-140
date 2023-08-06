from box import Box
import pandas as pd

from ..db.sqlalchemydb import SQLAlchemyDB
from ..utils.dataloader import DataLoader


class DataPrep:
    def __init__(self, config: Box):
        self.config = config

    def load_csv_data(self) -> [pd.DataFrame]:
        dl = DataLoader(self.config)
        data_list = []
        for file in self.config.data.paths:
            data = dl.get_data(file)
            data.attrs["source"] = file.split('/')[-1]
            data_list.append(data)

        return data_list

    def load_db_data(self) -> [pd.DataFrame]:
        sqlalchemydb = SQLAlchemyDB(config=self.config)

        if self.config.db.table_names is None:
            table_names = sqlalchemydb.get_all_table_names()
        else:
            table_names = self.config.db.table_names

        data_list = []
        for table in table_names:
            data = sqlalchemydb.read_table(table_name=table)
            data.attrs["source"] = table
            data_list.append(data)

        return data_list
