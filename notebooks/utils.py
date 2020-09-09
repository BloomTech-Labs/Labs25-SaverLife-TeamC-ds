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

import pandas as pd
import psycopg2
import plotly.express as px
from typing import Optional
import json
from dotenv import load_dotenv
from os.path import join, dirname
import os
load_dotenv()
class SaverlifeUtility(object):
    """Main utility class."""
    def __init__(self):
        self.model = None
        self.cursor = self._handle_cursor() 

    def _handle_connection(self):
        return psycopg2.connect(
           host=os.getenv("POSTGRES_ADDRESS"),
           dbname=os.getenv("POSTGRES_DBNAME"),
           user=os.getenv("POSTGRES_USER"), 
           password=os.getenv("POSTGRES_PASSWORD"), 
           port=os.getenv("POSTGRES_PORT")) 
        
    def _handle_cursor(self):
        self._conn = self._handle_connection()
        self._cur = self._conn.cursor()
        return self._conn, self._cur
    
query_utility = SaverlifeUtility()
