"""
INPUT HANDLER CLASS

This class serves as the main data getter class.
All data loading should come from this class to ensure standardised and structured data loading across scripts.
"""

import pandas as pd
from base.data_connectors import PandasFileConnector

pd.set_option("max.columns", 20)
pd.set_option("display.width", 2000)


class InputHandler:
    
    @classmethod
    def get_data_customers(cls):

        data_df = PandasFileConnector.load(
            "data/01_raw/customer_data.csv",
            file_type='csv'
        )
        return data_df

    @classmethod
    def get_data_cluster(cls):

        data_df = PandasFileConnector.load(
            "data/01_raw/cluster_data.csv",
            file_type='csv'
        )
        return data_df

    @classmethod
    def get_data_product(cls):

        data_df = PandasFileConnector.load(
            "data/01_raw/product_data.csv",
            file_type='csv'
        )
        return data_df

    @classmethod
    def get_data_product_cost(cls):

        data_df = PandasFileConnector.load(
            "data/01_raw/product_cost.csv",
            file_type='csv'
        )
        return data_df

    @classmethod
    def get_data_product_profit(cls):

        data_df = PandasFileConnector.load(
            "data/01_raw/product_profit.csv",
            file_type='csv'
        )
        return data_df