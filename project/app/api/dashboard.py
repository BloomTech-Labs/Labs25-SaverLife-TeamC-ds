import plotly.express as px
from fastapi import APIRouter, HTTPException, Response, Request, Form
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="./app/static/dist")


@router.get("/")
async def form_post(request: Request):
    """"""
    result = None
    return templates.TemplateResponse('index.html', context={'request': request, 'result': result})


@router.get("/index/testing_blank")
async def form_post(request: Request):
    """"""
    result = None
    return templates.TemplateResponse('blank_test.html', context={'request': request, 'result': result})