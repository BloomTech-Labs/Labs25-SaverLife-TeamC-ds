from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api import dashboard, endpoints
from app.api.utils import SaverlifeUtility, SaverlifeVisual


app = FastAPI(docs_url="/docs", redoc_url="/documentation")
app.mount("/static", StaticFiles(directory="./app/static"), name="static")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title='Labs 25 Saverlife-C',
        version='1.0.0',
        openapi_version='3.0.2',
        routes=app.routes
    )

    openapi_schema["info"] = {
        "version": "0.0.1",
        "description": "Machine learning forecasting straight to your wallets!\n# Introduction\n Welcome to the\
            **Saverlife** API! We use engaging technologies to inspire, and inform anyone who need help saving Money. \
            We give the working people the methods and motivation to take control of their financial future.\n# Version\
            \nVersion 0.0.1",
        "title": "Labs 25 Saverlife-C",
        "termsOfService": "https://www.example.com",
        "contact": {
            "name": "API Support",
            "email": "http://www.example.com/",
            "url": "https://github.com/orgs/Lambda-School-Labs/teams/labs25-saverlife-teamc/repositories"
        },
        "x-logo": {
            "url": "https://github.com/Lambda-School-Labs/Labs25-SaverLife-TeamC-ds/blob/main/project/app/static/images/saverlife_logo.png",
            "altText: Saverlife logo"
            "backgroundColor": "#FAFAFA"
        },
        "license": {
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(endpoints.router)
app.include_router(dashboard.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)