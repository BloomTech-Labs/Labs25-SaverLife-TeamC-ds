from typing import Optional, Set
from pydantic import BaseModel, Field, validator


def valid_user_id(cls, user_id):
    """Validate that 'user_id' must contain 10 characters and be string type."""
    user_id_string = str(user_id)

    assert isinstance(user_id, str), "user id must be a string."

    return user_id

class User(BaseModel):
    """User data model to parse the request JSON body."""
    user_id: str = Field(..., 
                         example=000000, 
                         description="Valid user identification number",
                         max_length=6)
    optional01: Optional[str] = None
    optional02: Optional[str] = None

    # validators
    _valid_user_id = validator('user_id', allow_reuse=True)(valid_user_id)
    
class GraphRequest(BaseModel):
    user_id: str = Field(..., 
                         example='000000', 
                         description="Valid user identification number", 
                         max_length=6
                         )
    graph_type: str = Field(..., 
                            example='CategoryBarMonth', 
                            description="Valid graph type"
                            )
    start_month: Optional[str] = 'optional field'
    end_month: Optional[str] = 'optional field'
                                      
    # validators
    _valid_user_id = validator('user_id', allow_reuse=True)(valid_user_id)

    @validator('graph_type')
    def valid_graph_type(cls, value):
        """Validate that graph_type is valid."""
        graph_list = ['TransactionTable', 'CategoryBarMonth']

        assert value in graph_list, f"{value} is not a valid graph type. Guess I'll die."        
        return value