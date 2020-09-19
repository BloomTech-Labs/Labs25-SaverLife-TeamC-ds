import pandas as pd
import plotly.graph_objects as go
from utils import query_utility

import numpy as np
import matplotlib.pyplot as plt
from sktime.forecasting.model_selection import temporal_train_test_split
from sktime.performance_metrics.forecasting import smape_loss
from sktime.utils.plotting.forecasting import plot_ys
from sktime.forecasting.naive import NaiveForecaster
from sktime.forecasting.compose import ReducedRegressionForecaster
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor


class Visualize():
    """
    Visualize different aspects of synthetic data 
    for SaverLife C Lambda School Labs project
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_transactions_df = self.handle_user_transaction_data()
        self.transaction_time_series_df = self.handle_transaction_timeseries_data()

    def handle_user_transaction_data(self):
        """
        Helper method to filter user data from SaverLife DB 
        """
        df = query_utility._generate_dataframe(bank_account_id=self.user_id, table='transactions')
        return df

    def handle_transaction_timeseries_data(self):
        """
        Helper method to clean transaction time series data
        """
        self.transactions_time_series_df = self.user_transactions_df.sort_values("date")
        self.transactions_time_series_df["amount_cents"] = self.transactions_time_series_df["amount_cents"].astype(int)
        self.transactions_time_series_df["formatted_date"] = self.transactions_time_series_df.date.dt.strftime('%Y-%m-%d')
        self.transactions_time_series_df.sort_values("formatted_date", ascending=False, inplace=True)
        return self.transactions_time_series_df

    def handle_resampling_transaction_timeseries_df(self, offset_string):
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
        return self.resampled_transaction_timeseries.groupby("category_name").resample(offset_string).sum().reset_index()
    
    def handle_resampling_transaction_timeseries_df_parent_categories(self, offset_string):
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
        return self.resampled_transaction_timeseries.groupby("parent_category_name").resample(offset_string).sum().reset_index()[["parent_category_name","date","amount_cents"]]

    def return_all_transactions_for_user(self):
        """
        Plotly Table Object of all transactions for a user
        Usage:
        # Instantiate the class
        >>> visualize = Visualize(user_id=4923847023975)
    
        # Plotly table of all transactions for a single user
        >>> visualize.return_all_transactions_for_user()
        """
        fig = go.Figure(data=[go.Table(header=dict(values=["Date", 
                                                           "Amount cents", 
                                                           "Category",
                                                           "Parent Category",
                                                           "Grandparent Category"],
                                                   fill_color='lightgray',
                                                   align='left'),
                                       cells=dict(values=[self.transaction_time_series_df.formatted_date, 
                                                          self.transaction_time_series_df.amount_cents, 
                                                          self.transaction_time_series_df.category_name,
                                                          self.transaction_time_series_df.parent_category_name,
                                                          self.transaction_time_series_df.grandparent_category_name],
                                                  fill_color='whitesmoke',
                                                  align='left'))])
        fig.update_layout(title_text="Transactions: User {}".format(self.user_id),
                          title_font_size=30)
        return fig.to_json()

    def categorized_bar_chart_per_month(self):
        """
        Plotly Bar Chart Object of monthly sum transactions for a user
        Usage:
        # Instantiate the class
        >>> visualize = Visualize(user_id=4923847023975)
    
        # Plotly bar chart of monthly sum transactions
        >>> visualize.categorized_bar_chart_per_month()
        """
        def helper_function_for_trace_visibility(len_array, i):
            intermediate_array = [False] * len_array
            intermediate_array[i] = True
            return intermediate_array
        self.monthly_sum_transactions_time_series_df = self.handle_resampling_transaction_timeseries_df("M").sort_values("date")
        self.monthly_sum_transactions_time_series_df.drop(columns=["bank_account_id","id","lat","lon"], inplace=True)
        months_of_interest = self.monthly_sum_transactions_time_series_df.date.dt.strftime('%Y-%m').unique().tolist()
        length_of_interest = len(months_of_interest)
        list_of_monthly_dfs = []
        for month in months_of_interest:
            list_of_monthly_dfs.append(self.monthly_sum_transactions_time_series_df[self.monthly_sum_transactions_time_series_df.date.dt.strftime('%Y-%m') == month])
        fig = go.Figure()
        for i in range(len(list_of_monthly_dfs)-1):
            fig.add_trace(go.Bar(x=list(list_of_monthly_dfs[i].category_name), 
                                 y=list(list_of_monthly_dfs[i].amount_cents), 
                                 name=str(list_of_monthly_dfs[i].date.dt.strftime('%Y-%m').iloc[0]), 
                                 visible=False))
        fig.add_trace(go.Bar(x=list(list_of_monthly_dfs[-1].category_name), 
                             y=list(list_of_monthly_dfs[-1].amount_cents), 
                             name=str(list_of_monthly_dfs[-1].date.dt.strftime('%Y-%m').iloc[0]), 
                             visible=True))

        fig.update_layout(
            updatemenus=[
                dict(active=length_of_interest-1, buttons=list([
                        dict(label=months_of_interest[i],
                             method="update",
                             args=[{"visible": helper_function_for_trace_visibility(length_of_interest, i)},
                                   {"annotations": []}]) for i in range(length_of_interest)]))])

        fig.write_html("testing_barchars.html")

    def next_month_forecast(self, model="kNeighbors"):
        """
        Forecast next month's transactions based on historical transactions

        Caveats:
            Only forecasts for parent_categories for which 
            there are at least 12 months of observations available

        Returns:
            Dictionary of forecasts, with parent_category_name 
            as key and forecasted amount_cents as value
        
        Usage:
            # Instantiate the class
        >>> visualize = Visualize(user_id=45153)
    
        # Forecast transactiosn for next month
        >>> visualize.next_month_forecast()
        """
        # Resample to monthly sum per parent_category_name
        self.monthly_parent_category_total = self.handle_resampling_transaction_timeseries_df_parent_categories("M")
        # Filter for parent_categories with at least 12 months of data
        self.df12 = self.monthly_parent_category_total[self.monthly_parent_category_total['parent_category_name'].map(self.monthly_parent_category_total['parent_category_name'].value_counts()) > 12]
        # Container to store forecasting results
        self.forecasting_results = {}
        # Loop through each parent category and forecast month ahead with Naive Baseline
        for parent_cat in self.df12.parent_category_name.unique().tolist():
            # Select relevant transaction data for training the model
            y = self.df12[self.df12.parent_category_name == parent_cat]["amount_cents"]
            # Set forecasting horizon
            fh = np.arange(len(y)) + 1 
            # Initialize a forecaster, seasonal periodicity of 12 (months per year)   
            if model == "Naive":
                forecaster = NaiveForecaster(strategy="seasonal_last", sp=12)
            else:
                regressor = KNeighborsRegressor(n_neighbors=1)
                forecaster = ReducedRegressionForecaster(regressor=regressor, window_length=12, strategy="recursive")        
            # Fit forecaster to training data
            forecaster.fit(y)
            # Forecast prediction to match size of forecasting horizon
            y_pred = forecaster.predict(fh)
            # Store results in a dictionary
            self.forecasting_results[parent_cat] = y_pred.values[0]
        # Return the results for use in other parts of app
        return self.forecasting_results

    def calculate_monthly_total(self):
        forecasted_expenses = self.next_month_forecast()
        sum_of_forecasts = sum(forecasted_expenses.values())
        return sum_of_forecasts

    def handle_savings_goal_end_date(self, end_year, end_month):
        self.end_date = pd.to_datetime(pd.Timestamp(end_year, end_month, 1))
        self.today = pd.to_datetime(pd.Timestamp.today())
        months_to_end_date = (self.end_date - self.today)/pd.Timedelta(weeks=4)
        return months_to_end_date

    def handle_savings_goal(self, goal):
        return goal

    def prepare_budget_recommendation(self, end_year=(pd.Timestamp.today() + pd.Timedelta(weeks=78)).year, end_month=(pd.Timestamp.today() + pd.Timedelta(weeks=78)).month, goal=400):
        desired_months_until_goal_is_reached = self.handle_savings_goal_end_date(end_year, end_month)
        monthly_total = self.calculate_monthly_total() / 100
        savings_goal = self.handle_savings_goal(goal)
        savings_rate = savings_goal / desired_months_until_goal_is_reached
        return f"To reach your savings goal of ${savings_goal} by {self.end_date.strftime('%Y-%m')}, you should aim to save ${int(savings_rate + 1)} next month. We anticipate your net monthly expenses to be approximately ${int(monthly_total)}."

if __name__ == "__main__":
    program = Visualize(user_id=45153)
    program.prepare_budget_recommendation(2021, 8, 500)
    program.prepare_budget_recommendation()
