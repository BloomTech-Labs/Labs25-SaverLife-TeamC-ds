# Deprecated Visualize methods kept for reference
def DEPRECATED_time_series_transactions_for_user(self):
        """
        Display a user's transaction history 
        
        Returns:
            plotly line figure in JSON format
        """
        
        fig = go.Figure([go.Scatter(x=self.transactions_time_series_df['date'], 
                                    y=self.transactions_time_series_df['amount_cents'])])
        fig.update_xaxes(rangeslider_visible=False,
                         rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                                                          dict(count=6, label="6m", step="month", stepmode="backward"),
                                                          dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                          dict(count=1, label="1y", step="year", stepmode="backward"),
                                                          dict(step="all")])))
        return fig.to_json()

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
