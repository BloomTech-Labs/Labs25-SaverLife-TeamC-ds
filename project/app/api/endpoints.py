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

import plotly.graph_objects as go

from dotenv import load_dotenv
from os.path import join, dirname
import os

from app.api.utils import SaverlifeUtility, SaverlifeVisual
from app.api.basemodels import User, GraphRequest

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

router = APIRouter()
templates = Jinja2Templates(directory="./app/static/dist")


@router.post('/dev/requestvisual', tags=["Graph"])
async def read_user(payload: GraphRequest):
    """Saverlife C account graph generation route
        
    ### Status
    #### *Deployed!*

    ### Get
    #### Secondary index point used for development and testing purposes
    -   **description**: 
        -   copy of the primary index point serving as a staging environment
    
    -   **parameters**:
        -   **name**: GraphRequest
        -   **in**: payload
        -   **description**: payload that includes a user identification number and a graph type from a valid list.
        -   **required**: *true*
    
    -   **responses**:
        - **200**:
            - success
            - **schema**: *none*
        - **404**:
            - not found
    """  
    visual = SaverlifeVisual(user_id=payload.user_id)
    
    # invalid user_id handling
    if visual.user_transactions_df.size > 0:
        raise HTTPException(
            status_code=500,
            detail="internal dataframe size 0, this is likely due to an invalid user id"
        )

    def _parse_graph(graph_type=payload.graph_type):
        if graph_type == 'TransactionTable':
            fig = visual.return_all_transactions_for_user()
        if graph_type == 'CategoryBarMonth':
            fig = visual.categorized_bar_chart_per_month()
        
        return fig

    return _parse_graph()


@router.post('/dev/requestvisual/payload', tags=["Graph"])
async def read_user(payload: GraphRequest):
    """Developer payload testing route
    
    ### Status
    #### *Deployed!*

    ### Get
    #### Secondary post point used for development and testing purposes
    -   **description**: 
        -   staging route that returns the body of the request.
    
    -   **parameters**:
        -   **name**: GraphRequest
        -   **in**: payload
        -   **description**: payload that includes a user identification number and a graph type from a valid list.
        -   **required**: *true*
    
    -   **responses**:
        - **200**:
            - success
            - **schema**: *none*
        - **404**:
            - not found
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


@router.get('/dev/forecast/', tags=['Forecast'])
async def return_forecast(payload: Optional[User] = None, user_id: Optional[str] = None):
    """Saverlife C transaction forecast route
    
    ### Status
    #### *Deployed!*

    ### Get
    #### Secondary post point used for development and testing purposes
    -   **description**: 
        -   staging route that returns the body of the request.
    
    -   **parameters**:
        -   **name**: GraphRequest
        -   **in**: payload
        -   **description**: payload that includes a user identification number and a graph type from a valid list
        -   **required**: *true*
        
    - **path parameters**:
        - **name**: user_id
        - **in**: path
        - **description**: user identification number path parameter
        - **required**: *false*
    
    -   **responses**:
        - **200**:
            - success
            - **schema**: *none*
        - **404**:
            - not found
    """
    if payload:
        visual = SaverlifeVisual(user_id=payload.user_id)
    else:
        visual = SaverlifeVisual(user_id=user_id)

    forecast = visual.next_month_forecast()

    cache = {}
    for key, value in forecast.items():
        cache[str(key)] = int(value)
        
    if forecast:
        return cache
    else: 
        # invalid observation count handling
        raise HTTPException(
            status_code=500,
            detail="internal dataframe size 0, this is likely due from having too few model observations"
        )


@router.get('/dev/forecast/statement/', tags=['Forecast']) #
async def return_forecast(payload: Optional[User] = None, user_id: Optional[int] = None, end_year: Optional[int] = None, end_month: Optional[int] = None, goal: Optional[int] = None):
    """Developer payload testing route
    
    ### Status
    #### *Deployed!*

    ### Get
    #### Secondary post point used for development and testing purposes
    -   **description**: 
        -   staging route that returns the body of the request.
    
    -   **parameters**:
        -   **name**: GraphRequest
        -   **in**: payload
        -   **description**: payload that includes a user identification number and a graph type from a valid list
        -   **required**: *true*
        
    - **path parameters**:
        - **name**: user_id
        - **in**: path
        - **description**: user identification number path parameter
        - **required**: *false*
    
    -   **responses**:
        - **200**:
            - success
            - **schema**: *none*
        - **404**:
            - not found
    """
    if payload:
        visual = SaverlifeVisual(user_id=payload.user_id)
        forecast = visual.prepare_budget_recommendation()
    else:
        visual = SaverlifeVisual(user_id=user_id)
        forecast = visual.prepare_budget_recommendation(end_year=end_year, end_month=end_month, goal=goal)

    cache = {}
    for key, value in forecast.items():
        cache[str(key)] = int(value)

    return cache