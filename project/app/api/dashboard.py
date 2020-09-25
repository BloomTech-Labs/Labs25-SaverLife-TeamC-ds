import plotly.express as px
from fastapi import APIRouter, HTTPException, Response, Request, Form
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="./app/static/dist")


@router.get("/", tags=['Dashsboard'])
async def dashboard_landing(request: Request):
    """Saverlife C main index route
    
    ### Status
    #### *Work in progress!*

    ### Get
    #### Primary index point that returns a landing dashboard
    -   **description**: index point that parses a payload and displays miscellaneous data regarding the 
        integrity of the application and its associated database. This includes information about the different models,
        functions, and endpoints with their respective documentation.
    
    -   **parameters**: *none*
    
    -   **responses**:
        - **200**:
            - success
            - schema: *none*
        - **404**:
            - not found
    """
    result = None

    return templates.TemplateResponse('index.html', context={'request': request, 'result': result})


@router.get("/dev/", tags=['Dashsboard'])
async def dashboard_landing_dev(request: Request):
    """Saverlife C developer index route
    
    ### Status
    #### *Work in progress!*

    ### Get
    #### Secondary index point used for development and testing purposes
    -   **description**: 
        -   copy of the primary index point serving as a staging environment
    
    -   **parameters**:
        -   **name**: parameter01
        -   **in**: payload
        -   **description**: empty parameter for development testing purposes
        -   **required**: *true*
    
    -   **responses**:
        - **200**:
            - success
            - **schema**: *none*
        - **404**:
            - not found
    """
    result = None

    return templates.TemplateResponse('blank_test.html', context={'request': request, 'result': result})