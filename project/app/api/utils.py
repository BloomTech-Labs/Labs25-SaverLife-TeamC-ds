from fastapi import APIRouter, HTTPException
import pandas as pd
import psycopg2
import plotly.express as px
from pydantic import BaseModel, Field, validator
from fastapi.templating import Jinja2Templates
from typing import Optional

from dotenv import load_dotenv
from os.path import join, dirname
import os


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


router = APIRouter()
templates = Jinja2Templates(directory="./app/static/dist")


class SaverlifeUtility(object):
    """Main utility class."""
    def __init__(self):
        self.model = None
        self.cursor = self._handle_cursor() 

    def _handle_connection(self):
        return psycopg2.connect(
           host=os.getenv('POSTGRES_ADDRESS'),
           dbname=os.getenv('POSTGRES_DBNAME'),
           user=os.getenv('POSTGRES_USER'), 
           password=os.getenv('POSTGRES_PASSWORD'), 
           port=os.getenv('POSTGRES_PORT') 
        )
        
    def _handle_cursor(self):
        conn = self._handle_connection()
        
        cur = conn.cursor()
        
        return conn, cur
    
    def query_constructor(self, limit, offset, user_id=None):
        if user_id:
            user_id = f"'{user_id}'"
            return f'SELECT * FROM "public"."transactions_data" WHERE bank_account_id={user_id} LIMIT {limit} OFFSET {offset}'
        else:
            return f'SELECT * FROM "public"."transactions_data" LIMIT {limit} OFFSET {offset}'


utility = SaverlifeUtility()    

    
@router.get('/transactions/', tags=["Database"])
async def read_transactions(user_id: Optional[str] = None, limit: int = 100, offset: int = 0):
    """
    Returns transaction data from query parameters
    
    """

    query = utility.query_constructor(user_id=user_id, limit=limit, offset=offset)
    
    conn, cur = utility._handle_cursor()
    
    cur.execute("""%s""" % (query))
    
    result = cur.fetchall()
    
    return result