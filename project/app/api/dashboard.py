import plotly.express as px
from fastapi import APIRouter, HTTPException, Response, Request, Form
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="./app/static/dist")


@router.get("/")
async def form_post(request: Request):
    """"""
    result = "3"
    return templates.TemplateResponse('index.html', context={'request': request, 'result': result})


if __name__ == "__main__":
    fig = px.scatter(x=range(10), y=range(10))
    fig.write_html("test.html")