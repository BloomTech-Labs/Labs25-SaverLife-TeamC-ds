import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
from typing import Optional
import json
from dotenv import load_dotenv
from os.path import join, dirname
import os
load_dotenv()

class SaverlifeUtility(object):
    """General utility class to handle database cursor objects and other miscellaneous functions."""
    def __init__(self):
        self._cursor = self._handle_cursor()
    def _handle_connection(self):
        """Connect to a database."""
        return psycopg2.connect(
           host=os.getenv('POSTGRES_ADDRESS_EXTERNAL'),
           dbname=os.getenv('POSTGRES_DBNAME_EXTERNAL'),
           user=os.getenv('POSTGRES_USER_EXTERNAL'), 
           password=os.getenv('POSTGRES_PASSWORD_EXTERNAL'), 
           port=os.getenv('POSTGRES_PORT_EXTERNAL') 
        )
    def _handle_cursor(self):
        """Create a cursor to perform database operations."""
        conn = self._handle_connection()
        cur = conn.cursor()
        return conn, cur
    def handle_query(self, query: str):
        """Handle simple query operations."""
        try:
            conn, cur = self._handle_cursor()
            cur.execute(query)
        except BaseException:
            traceback.print_exc()
        finally:
            if cur:
                result = cur.fetchall()
                cur.close()
                conn.close()
        return result
    def _generate_dataframe(self, bank_account_id: str, table: str, sample_size: int = 1):
        """Support utility function to handle database manipulation and other miscellaneous functions."""
        dataframe = None
        if table is 'transactions':
            dataframe = self._configure_transactions_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        if table is 'account':
            dataframe = self._configure_account_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        if table is 'miscellaneous':
            dataframe = self._configure_miscellaneous_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        return dataframe
    def _configure_transactions_dataframe(self, bank_account_id: str, sample_size: int = 1):
        df = self._fetch_transactions_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        df = self._wrangle_transactions(df)
        return df
    def _configure_account_dataframe(self, bank_account_id: str, sample_size: int = 1):
        df = self._fetch_account_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        df = self._wrangle_account(df)
        return df
    def _configure_miscellaneous_dataframe(self, bank_account_id: str, sample_size: int = 1):
        df = self._fetch_miscellaneous_dataframe(bank_account_id=bank_account_id, sample_size=sample_size)
        df = self._wrangle_miscellaneous(df)
        return df
    def _fetch_transactions_dataframe(self, bank_account_id: str = None, sample_size: int = 1):
        random_list = []
        feature_list = []
        primary_features = [
            'bank_account_id',
            'id', 
            'date', 
            'amount_cents',
            'category_id',
            'created_at',
        ]
        secondary_features = [
            'plaid_transaction_id',
            'merchant_city',
            'merchant_state',
            'lat', 
            'lon',
            'purpose'
        ]
        drop_features = [
            'merchant_address',
            'merchant_zip',
            'pending',
            'tenant_id',
            'iso_currency_code',
            'updated_at',
            'plaid_account_id'
        ]
        empty_features = [
            'atlas_id', 
            'atlas_parent_id',
            'program_month',
            'by_order_of',
            'payment_method', 
            'payment_processor', 
            'ppd_id', 
            'reason', 
            'reference_number', 
            'store_number',
            'unofficial_currency_code'
        ]
        feature_list = primary_features + secondary_features
        feature_query = ", ".join(feature_list)
        if sample_size is 1:
            query_operation = f"""
            SELECT {feature_query}
            FROM plaid_main_transactions
            WHERE bank_account_id = {bank_account_id}
            """
        else:
            for _ in range(sample_size):
                random_list.append(random.randrange(1, 255915))
            random_query = ", ".join(repr(i) for i in random_list)
            query_operation = f"""
            SELECT {feature_query}
            FROM plaid_main_transactions
            WHERE bank_account_id IN ({random_query})
            """
        query_fetch = self.handle_query(query_operation)
        df = pd.DataFrame(query_fetch, columns=feature_list)
        return df
    def _wrangle_transactions(self, x):
        """Wrangle incoming transaction data."""
        # Prevent SettingWithCopyWarning
        X = x.copy()
        # remove empty or 'None' values
        X.replace('', np.nan, inplace=True)
        X = X.fillna(value=np.nan)
        # test datetime features
        datetime_features = ['date', 'created_at']
        for i in datetime_features:
            X[i] = pd.to_datetime(X[i],
                                format="%m/%d/%Y, %H:%M:%S",
                                errors='raise') 
        # remove duplicate entries !WARNING (may affect resulting table)
        X = X.drop_duplicates(subset='plaid_transaction_id').reset_index(drop=True)
        return X
    def _fetch_account_dataframe(self):
        random_list = []
        feature_list = []
        primary_features = [
            'id',
            'current_balance_cents',
            'created_at',
            'updated_at',
            'name',
            'account_type',
            'available_balance_cents',
            'last_balance_update_at',
            'plaid_state',
            'initial_balance_cents',
            'main_saving'
        ]
        secondary_features = [
            'account_subtype',
            'plaid_account_id',
            'plaid_financial_authentication_id'
        ]
        drop_features = [
            'official_name',
            'type',
            'mask',
            'rewards_basis',
            'tenant_id', 
            'atlas_id',
            'atlas_parent_id'
        ]
        feature_list = primary_features + secondary_features
        feature_query = ", ".join(feature_list)
        if sample_size is 1:
            query_operation = f"""
            SELECT {feature_query}
            FROM bank_accounts
            WHERE id = {bank_account_id}
            """
        else:
            for _ in range(sample_size):
                random_list.append(random.randrange(1, 255915))
            random_query = ", ".join(repr(i) for i in random_list)
            query_operation = f"""
            SELECT {feature_query}
            FROM bank_accounts
            WHERE id IN ({random_query})
            """
        query_fetch = self.handle_query(query_operation)
        df = pd.DataFrame(query_fetch, columns=feature_list)
        return df
    def _wrangle_account(self, x):
        pass
    def _fetch_miscellaneous_dataframe(self):
        pass
    def _wrangle_miscellaneous(self, x):
        pass

query_utility = SaverlifeUtility()