from typing import Optional, Set

from fastapi import FastAPI
from pydantic import BaseModel


class Transaction(BaseModel):
    index: str
    category_id: str
    plaid_account_id: str
    bank_account_id: str
    id_PMT: str
    amount_cents: str
    purpose: str
    date: str
    created_at_PMT: str
    updated_at_PMT: str
    plaid_category_id: str
    category_name: str
    parent_category_name: str
    grandparent_category_name: str
    id_BA: str
    current_balance_cents: str
    updated_at_BA: str
    created_at_BA: str
    name: str
    account_subtype: str
    plaid_account_id_BA: str
    plaid_financial_authentication_id: str
    available_balance_cents: str
    id_PFA: str
    institution_name: str
    user_id: str
    updated_at_PFA: str
    created_at_PFA: str
    last_status_update_at: str
    
    
    

