import logging
from box import Box
import pandas as pd

log = logging.getLogger(__name__)


class DataLoader:
    """
    This class has methods to load and write data.
    """

    def __init__(self, config: Box):
        self.separator = config.data.separator

    def get_data(self, filename: str, dtype: dict = None):
        log.info(f"Started loading data source - {filename}")
        data = pd.read_csv(filename, sep=self.separator, dtype=dtype).applymap(
            lambda x: x.strip() if isinstance(x, str) else x)
        return data.loc[:, ~data.columns.str.contains('^Unnamed')]
