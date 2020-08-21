from fastapi import APIRouter, HTTPException
import pandas as pd
import psycopg2 as ps
import plotly.express as px

from dotenv import load_dotenv
import os
load_dotenv()
# import environ
# env = environ.Env.read_env()

router = APIRouter()

@router.get('/query')
async def create_connection():
    """
    Return query requests based on path command.
    
    ### Path Parameter
    `statecode`: The [USPS 2 letter abbreviation](https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_abbreviations#Table) 
    (case insensitive) for any of the 50 states or the District of Columbia.

    ### Response
    JSON string to render with [react-plotly.js](https://plotly.com/javascript/react/) 
    """
    POSTGRES_ADDRESS = os.getenv('POSTGRES_ADDRESS')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT')
    POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DBNAME = os.getenv('POSTGRES_DBNAME')
    
    conn = ps.connect(host=POSTGRES_ADDRESS,
                    dbname=POSTGRES_DBNAME,
                    user=POSTGRES_USERNAME,
                    password=POSTGRES_PASSWORD,
                    port=POSTGRES_PORT)

    cur = conn.cursor()

    cur.execute("""SELECT * FROM "public"."transactions_data" LIMIT 10000 OFFSET 0""")

    result = cur.fetchall()

    conn.close()
    
    return result