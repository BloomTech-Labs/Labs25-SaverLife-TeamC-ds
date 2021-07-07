# Deprecated Visualize methods kept for reference
    def DEPRECATED_choropleth_of_users_by_state(self):
        """
        Display user count by US State as a choropleth map
        
        Returns:
            Displayed plotly figure
        """
        # Prepare data for visualization
        ### Group users by state
        self.user_count_by_state = self.user_data_df.groupby("user_location").count().reset_index()
        ### Rename the column reflecting user count per state
        self.user_count_by_state.rename(columns={"Unnamed: 0":"user_count"}, 
                                        inplace=True)
        ### Add two letter abbreviations for each administrative boundary
        self.user_count_by_state["code"] = self.user_count_by_state["user_location"].map(STATE_CODE_DICT)
        # Leverage plotly to build interactive choropleth map
        self.choropleth_fig = go.Figure(data=go.Choropleth(locations=self.user_count_by_state['code'],
                                                z=self.user_count_by_state['user_count'].astype(float),
                                                locationmode='USA-states',
                                                colorscale='Reds',
                                                autocolorscale=False,
                                                text=self.user_count_by_state['user_location'], # hover text
                                                marker_line_color='white', # line markers between states
                                                colorbar_title="# of users"))
        self.choropleth_fig.update_layout(title_text='Generated SaverLife Users',
                               geo = dict(scope='usa',
                                          projection=go.layout.geo.Projection(type ='albers usa'),
                                          showlakes=True,
                                          lakecolor='rgb(255, 255, 255)'))
        self.choropleth_fig.show()

    def DEPRECATED_categorized_time_series_transactions_for_user(self):
        def helper_function_for_trace_visibility(len_array, i):
            intermediate_array = [False] * len_array
            intermediate_array[i] = True
            return intermediate_array
        
        df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv")
        df.columns = [col.replace("AAPL.", "") for col in df.columns]
        
        colors_for_traces = px.colors.qualitative.Alphabet
        columns_of_interest = ["High","Low", "Open", "Close","Adjusted"]
        length_of_interest = len(columns_of_interest)
        
        fig = go.Figure()

        for i in range(length_of_interest):
            fig.add_trace(go.Scatter(x=list(df.index),
                                     y=list(df[columns_of_interest[i]]),
                                     name=columns_of_interest[i],
                                     line=dict(color=colors_for_traces[i])))

        fig.update_layout(
            updatemenus=[
                dict(buttons=list([
                dict(label="All",
                             method="update",
                             args=[{"visible": [True] * length_of_interest},
                                   {"title": "Yahoo All",
                                    "annotations": []}])]))])

        fig.update_layout(
            updatemenus=[
                dict(buttons=list([
                        dict(label=columns_of_interest[i],
                             method="update",
                             args=[{"visible": helper_function_for_trace_visibility(length_of_interest, i)},
                                   {"title": "Yahoo {}".format(columns_of_interest[i]),
                                    "annotations": []}]) for i in range(length_of_interest)]))])

        fig.update_layout(title_text="Yahoo")
        fig.show()

def DEPRECATED_handle_transaction_data(self):
        """
        Helper method to filter transaction data from AWS RDS 
        PostgreSQL DB for a single user's transactions
        """

        user_id = f"'{self.user_id}'"
        query = f'SELECT * FROM "public"."user_transactions" WHERE user_id={user_id}'
        return pd.read_sql("""%s""" % (query), query_utility._conn)

def BUGGY_categorized_time_series_transactions_for_user(self, offset_string=None):
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

        
        columns_of_interest = self.data_for_figure["category_id"].unique().tolist()
        length_of_interest = len(columns_of_interest)
        colors_for_traces = px.colors.qualitative.Alphabet * (length_of_interest)
        
        fig = go.Figure()
        for i in range(length_of_interest):
            fig.add_trace(go.Scatter(x=list(self.data_for_figure[self.data_for_figure["category_id"] == columns_of_interest[i]]["date"]),
                                     y=list(self.data_for_figure[self.data_for_figure["category_id"] == columns_of_interest[i]]["amount_cents"]),
                                     name=columns_of_interest[i],
                                     line=dict(color=colors_for_traces[i])))
        
        #fig.to_json()
        fig.write_html("testing_categorized_time_series_transactions.html")

def BUGGY_most_recent_developer_specified_timeframe_of_transactions(self, timeframe="W"):
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
                                                "Category Name"],
                            fill_color='lightgray',
                            align='left'),
                        cells=dict(values=[self.recent_transactions.date, 
                                           self.recent_transactions.amount_cents, 
                                           self.recent_transactions.category_name],
                        fill_color='whitesmoke',
                        align='left'))])

        fig.update_layout(title_text="Recent Transactions: User {}".format(self.user_id),
                  title_font_size=30)

        fig.to_json()
        
        
STATE_CODE_DICT = {
    'Alaska': 'AK',
     'Alabama': 'AL',
     'Arkansas': 'AR',
     'American Samoa': 'AS',
     'Arizona': 'AZ',
     'California': 'CA',
     'Colorado': 'CO',
     'Connecticut': 'CT',
     'District of Columbia': 'DC',
     'Delaware': 'DE',
     'Florida': 'FL',
     'Georgia': 'GA',
     'Guam': 'GU',
     'Hawaii': 'HI',
     'Iowa': 'IA',
     'Idaho': 'ID',
     'Illinois': 'IL',
     'Indiana': 'IN',
     'Kansas': 'KS',
     'Kentucky': 'KY',
     'Louisiana': 'LA',
     'Massachusetts': 'MA',
     'Maryland': 'MD',
     'Maine': 'ME',
     'Michigan': 'MI',
     'Minnesota': 'MN',
     'Missouri': 'MO',
     'Northern Mariana Islands': 'MP',
     'Mississippi': 'MS',
     'Montana': 'MT',
     'National': 'NA',
     'North Carolina': 'NC',
     'North Dakota': 'ND',
     'Nebraska': 'NE',
     'New Hampshire': 'NH',
     'New Jersey': 'NJ',
     'New Mexico': 'NM',
     'Nevada': 'NV',
     'New York': 'NY',
     'Ohio': 'OH',
     'Oklahoma': 'OK',
     'Oregon': 'OR',
     'Pennsylvania': 'PA',
     'Puerto Rico': 'PR',
     'Rhode Island': 'RI',
     'South Carolina': 'SC',
     'South Dakota': 'SD',
     'Tennessee': 'TN',
     'Texas': 'TX',
     'Utah': 'UT',
     'Virginia': 'VA',
     'Virgin Islands': 'VI',
     'Vermont': 'VT',
     'Washington': 'WA',
     'Wisconsin': 'WI',
     'West Virginia': 'WV',
     'Wyoming': 'WY'
}