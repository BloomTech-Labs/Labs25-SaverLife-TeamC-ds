import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import STATE_CODE_DICT, query_utility

class Visualize():
    """
    Visualize different aspects of synthetic data 
    for SaverLife C Lambda School Labs project
    
    Usage:
    # Instantiate the class
    >>> visualize = Visualize(user_id="A USER ID")
    
    # Plot choropleth map of users by US state
    >>> visualize.categorized_time_series_transactions_for_user()
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_data_df = self.handle_user_data()
        self.transaction_data_df = self.handle_transaction_data()
        self.transaction_time_series_df = self.handle_transaction_timeseries_data()

    def handle_user_data(self):
        """
        Helper method to filter user data from AWS RDS 
        PostgreSQL DB for a single user
        """

        user_id = f"'{self.user_id}'"
        query = f'SELECT * FROM "public"."user_id" WHERE user_id={user_id}'
        return pd.read_sql("""%s""" % (query), query_utility._conn)

    def handle_transaction_data(self):
        """
        Helper method to filter transaction data from AWS RDS 
        PostgreSQL DB for a single user's transactions
        """

        user_id = f"'{self.user_id}'"
        query = f'SELECT * FROM "public"."user_transactions" WHERE user_id={user_id}'
        return pd.read_sql("""%s""" % (query), query_utility._conn)

    def handle_transaction_timeseries_data(self):
        """
        Helper method to create transaction time series data
        from transaction_data
        """

        self.transactions_time_series_df = self.transaction_data_df.sort_values("date")
        self.transactions_time_series_df["amount_cents"] = self.transactions_time_series_df["amount_cents"].astype(int)
        return self.transactions_time_series_df

    def handle_resampling_transaction_timeseries_df(self, frequency):
        """
        Helper method to resample transaction timeseries data
        to a user-specified time frequency

        Args:
            frequency: a pandas DateOffset, Timedelta or str
                See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 
                for more on dateoffset strings
        
        Returns:
            resampled_transaction_timeseries

        Usage:
        # Resample to weekly sum
        >>> resampled_data = self.handle_resampling_transaction_timeseries_df(offset_string="W")
        """

        self.resampled_transaction_timeseries = self.transactions_time_series_df.copy()
        self.resampled_transaction_timeseries["date"] = pd.to_datetime(self.resampled_transaction_timeseries["date"])
        self.resampled_transaction_timeseries.set_index("date", inplace=True)
        return self.resampled_transaction_timeseries.groupby("category_name").resample(frequency).sum().reset_index()

    def categorized_time_series_transactions_for_user(self, offset_string):
        """
        Display a user's categorized transaction history 
        
        Args:
            user_data: self.transactions_time_series_df or resampled to new datetime offset

        Returns:
            plotly line figure in JSON format
        """
        if offset_string == None:
            self.data_for_figure = self.transactions_time_series_df
        else:
            self.data_for_figure = self.handle_resampling_transaction_timeseries_df(offset_string)

        colors_for_traces = px.colors.qualitative.Safe
        columns_of_interest = self.data_for_figure["category_name"].unique().tolist()
        length_of_interest = len(columns_of_interest)
        
        fig = go.Figure()
        for i in range(length_of_interest):
            fig.add_trace(go.Scatter(x=list(self.data_for_figure[self.data_for_figure["category_name"] == columns_of_interest[i]]["date"]),
                                     y=list(self.data_for_figure[self.data_for_figure["category_name"] == columns_of_interest[i]]["amount_cents"]),
                                     name=columns_of_interest[i],
                                     line=dict(color=colors_for_traces[i])))
        
        fig.to_json()
