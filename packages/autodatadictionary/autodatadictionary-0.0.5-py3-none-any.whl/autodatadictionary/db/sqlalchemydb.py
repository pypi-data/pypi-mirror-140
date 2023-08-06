import pandas as pd
import logging
from sqlalchemy import create_engine
from box import Box

log = logging.getLogger(__name__)


class SQLAlchemyDB:
    """
    This class handles database operations related to SQLAlchemyDB
    """

    def __init__(self, config: Box):
        self.connection_string = config.db.sql_alchemy_connection_string
        self.row_limit = config.db.row_limit
        self.schema = config.db.schema

    def read_table(self, table_name: str) -> pd.DataFrame:
        """
        Reads and returns the table from database
        @param table_name: database table name
        @return: whole table
        """
        log.info(f"Started querying data source - {table_name}")
        try:
            alchemy_engine = create_engine(self.connection_string)
            if isinstance(self.row_limit, int):
                data = pd.read_sql_query(f"SELECT * FROM {self.schema}.{table_name} LIMIT {self.row_limit}",
                                         alchemy_engine)
            else:
                data = pd.read_sql_query(f"SELECT * FROM {self.schema}.{table_name}", alchemy_engine)
            return data
        except ValueError as vx:
            print(vx)
        except Exception as ex:
            print(ex)

    def get_all_table_names(self) -> [str]:
        """
        Reads and returns the table from database
        @return: List of all table names in specified schema
        """
        try:
            alchemy_engine = create_engine(self.connection_string)
            data = pd.read_sql_query(
                "SELECT table_name FROM information_schema.tables "
                f"WHERE table_schema='{self.schema}' AND table_type='BASE TABLE'",
                alchemy_engine)
            return data["table_name"].to_list()
        except ValueError as vx:
            print(vx)
        except Exception as ex:
            print(ex)

    def read_sql_query(self, sql_query: str) -> pd.DataFrame:
        """
        Return data based on custom sql query
        @return: dataframe
        """
        try:
            alchemy_engine = create_engine(self.connection_string)
            df = pd.read_sql_query(sql_query, alchemy_engine)
            return df
        except ValueError as vx:
            print(vx)
        except Exception as ex:
            print(ex)
