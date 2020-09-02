import plotly.express as px
from fastapi import APIRouter, HTTPException, Response, Request, Form
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="./app/static/dist")


class SaverlifeDashboard(object):
    """Main dashboard class."""
    def __init__(self):
        self.model = None
        self.cursor = self._handle_cursor() 
 

@router.get("/")
async def form_post(request: Request):
    """"""
    result = None
    return templates.TemplateResponse('index.html', context={'request': request, 'result': result})

@router.get("/index/testing")
async def form_post(request: Request):
    """"""
    result = None
    return templates.TemplateResponse('index_test.html', context={'request': request, 'result': result})

@router.get("/index/testing_blank")
async def form_post(request: Request):
    """"""
    result = None
    return templates.TemplateResponse('blank_test.html', context={'request': request, 'result': result})


if __name__ == "__main__":
    pass