from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
from pydantic import BaseModel, Field, validator
from fastapi.templating import Jinja2Templates
from typing import Optional
import json
import random

import sys
import traceback

from sktime.forecasting.model_selection import temporal_train_test_split
from sktime.performance_metrics.forecasting import smape_loss
from sktime.utils.plotting.forecasting import plot_ys
from sktime.forecasting.naive import NaiveForecaster
from sktime.forecasting.compose import ReducedRegressionForecaster
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor

import plotly.graph_objects as go

from dotenv import load_dotenv
from os.path import join, dirname
import os

from app.api.utils import SaverlifeUtility, SaverlifeVisual
from app.api.basemodels import User, GraphRequest

router = APIRouter()
templates = Jinja2Templates(directory="./app/static/dist")

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)




@router.post('/dev/requesttesting', tags=["Graph"])
async def read_user(payload: GraphRequest):
    """
    Returns a visual table or graph according to input parameters.
    """

    user_id = f"{request.user_id}"
    graph_type = f"{request.graph_type}"
    start_month = f"{request.start_month}"
    end_month = f"{request.end_month}"

    return {
        'message': 'The payload sent in a 200 response.',
        'payload': {
            'user_id': user_id,
            'graph_type': graph_type,
            'optional[start_month]': start_month,
            'optional[end_month]': end_month
        }
    }


@router.post('/dev/requestvisual', tags=["Graph"])
async def read_user(payload: GraphRequest):
    """
    Returns a visual table or graph according to input parameters.
    """
    SaverlifeVisual = Visualize(user_id=payload.user_id)
    
    if SaverlifeVisual.user_transactions_df.size > 0:
        pass
    else: 
        return {
            'details': [
                {
                    'loc': 'pandas dataframe',
                    'msg': 'dataframe size 0, possible invalid user_id',
                    'type': 'internal'
                }
            ]
        }
    
    def _parse_graph(graph_type=payload.graph_type):
        if graph_type == 'TransactionTable':
            fig = SaverlifeVisual.return_all_transactions_for_user()
        if graph_type == 'CategoryBarMonth':
            fig = SaverlifeVisual.categorized_bar_chart_per_month()
        
        return fig

    return _parse_graph()


@router.get('/dev/forecast/', tags=['Forecast'])
async def return_forecast(payload: Optional[User] = None, user_id: Optional[str] = None):
    """
    Returns a dictionary forecast.
    """
    if payload:
        SaverlifeVisual = Visualize(user_id=payload.user_id)
    else:
        SaverlifeVisual = Visualize(user_id=user_id)

    forecast = SaverlifeVisual.next_month_forecast()

    cache = {}
    for key, value in forecast.items():
        cache[str(key)] = int(value)
        
    if forecast:
        return cache
    else: 
        return {
            'details': [
                {
                    'loc': [
                        'internal',
                        'model'
                    ],
                    'msg': 'return dictionary size null, possible too few model observations.',
                    'doc': {
                        'description': "Forecast next month's transactions based on historical transactions.",
                        'caveats': "Only forecasts for parent_categories for which there are at least 12 months of observations available",
                        'returns': "Dictionary of forecasts, with parent_category_name as key and forecasted amount_cents as value"
                    },
                    'type': 'internal'
                }
            ]
        }
        
@router.get('/dev/forecast/statement/', tags=['Forecast']) #
async def return_forecast(payload: Optional[User] = None, user_id: Optional[int] = None, end_year: Optional[int] = None, end_month: Optional[int] = None, goal: Optional[int] = None):
    """
    Returns a dictionary forecast.
    """
    if payload:
        SaverlifeVisual = Visualize(user_id=payload.user_id)
        forecast = SaverlifeVisual.prepare_budget_recommendation()
    else:
        SaverlifeVisual = Visualize(user_id=user_id)
        forecast = SaverlifeVisual.prepare_budget_recommendation(end_year=end_year, end_month=end_month, goal=goal)

    cache = {}
    for key, value in forecast.items():
        cache[str(key)] = int(value)

    return cache
    # cache = {}
    # for key, value in forecast.items():
    #     cache[str(key)] = int(value)
        
    # if forecast:
    #     return cache
    # else: 
    #     return {
    #         'details': [
    #             {
    #                 'loc': [
    #                     'internal',
    #                     'model'
    #                 ],
    #                 'msg': 'dictionary size 0, possible too few model observations.',
    #                 'doc': {
    #                     'description': "Forecast next month's transactions based on historical transactions.",
    #                     'caveats': "Only forecasts for parent_categories for which there are at least 12 months of observations available",
    #                     'returns': "Dictionary of forecasts, with parent_category_name as key and forecasted amount_cents as value"
    #                 },
    #                 'type': 'internal'
    #             }
    #         ]
    #     }