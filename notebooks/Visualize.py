import pandas as pd
import plotly.graph_objects as go
from utils import query_utility

class Visualize():
    """
    Visualize different aspects of synthetic data 
    for SaverLife C Lambda School Labs project
    
    Usage:
    # Instantiate the class
    >>> visualize = Visualize(user_id="A USER ID")
    
    # Plotly table of all transactions for a single user
    >>> visualize.return_all_transactions_for_user()
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_transactions_df = self.handle_user_transaction_data()
        self.transaction_time_series_df = self.handle_transaction_timeseries_data()

    def handle_user_transaction_data(self):
        """
        Helper method to filter user data from AWS RDS 
        PostgreSQL DB for a single user
        """

        df = query_utility._generate_dataframe(bank_account_id=self.user_id, table='transactions')
        return df

    def handle_transaction_timeseries_data(self):
        """
        Helper method to create transaction time series data
        from transaction_data
        """

        self.transactions_time_series_df = self.user_transactions_df.sort_values("date")
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

    def most_recent_developer_specified_timeframe_of_transactions(self, timeframe="W"):
        """
        Display most recent timeframe of transaction data
        Defaults to 1W but can be adjusted with args

        Args:
            timeframe: pandas datetime stampe for reverse sorting data

        Returns:
            plotly graph object table of recent transactions
        """

        self.recent_transactions = self.transaction_time_series_df.copy()
        self.recent_transactions["date"] = pd.to_datetime(self.recent_transactions["date"])
        self.recent_transactions.set_index("date", inplace=True)
        self.recent_transactions = self.recent_transactions.last("1{}".format(timeframe)).reset_index()
        
        fig = go.Figure(data=[go.Table(
                            header=dict(values=["Date", 
                                                "Amount cents", 
                                                "Category ID"],
                            fill_color='lightgray',
                            align='left'),
                        cells=dict(values=[self.recent_transactions.date, 
                                           self.recent_transactions.amount_cents, 
                                           self.recent_transactions.category_id],
                        fill_color='whitesmoke',
                        align='left'))])

        fig.update_layout(title_text="Recent transactions for user {}".format(self.user_id),
                  title_font_size=30)

        fig.to_json()

    def return_all_transactions_for_user(self):
        
        fig = go.Figure(data=[go.Table(
                            header=dict(values=["Date", 
                                                "Amount cents", 
                                                "Category ID"],
                            fill_color='lightgray',
                            align='left'),
                        cells=dict(values=[self.transaction_time_series_df.date, 
                                           self.transaction_time_series_df.amount_cents, 
                                           self.transaction_time_series_df.category_id],
                        fill_color='whitesmoke',
                        align='left'))])

        fig.update_layout(title_text="Transactions: User {}".format(self.user_id),
                  title_font_size=30)

        fig.to_json()


if __name__ == "__main__":
    program = Visualize(user_id=147254)
    program.return_all_transactions_for_user()
    program.most_recent_developer_specified_timeframe_of_transactions(pffset_string="M")