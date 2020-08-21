from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api import dashboard, predict, viz, query

app = FastAPI()

app.mount("/static", StaticFiles(directory="./app/static"), name="static")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title='Labs 25 Saverlife-C',
        version='0.0.1',
        openapi_version='3.0.2',
        routes=app.routes
    )

    openapi_schema["info"] = {
        "description": "Machine learning forecasting straight to your wallet!\n# Introduction\nWelcome to **Saverlife**!\
            \n# Version\n Sample version.\n# Authentication\n Sample authentication.\n",
        "version": "0.0.1",
        "title": "Labs 25 Saverlife-C",
        "termsOfService": "https://www.example.com",
        "contact": {
            "name": "API Support",
            "email": "http://www.example.com/",
            "url": "https://github.com/orgs/Lambda-School-Labs/teams/labs25-saverlife-teamc/repositories"
        },
        "x-logo": {
            "url": "https://raw.githubusercontent.com/Lambda-School-Labs/Labs25-SaverLife-TeamC-ds/aws-testing/project/app/static/img/saverlife.png",
            "altText: Saverlife logo"
            "backgroundColor": "#FAFAFA"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
    
app.openapi = custom_openapi

### Standard app creation
# app = FastAPI(
#     title='Labs 25 Saverlife-C',
#     version='0.0.1',
#     description='Machine Learning straight to your pockets.',
#     docs_url='/',
# )

app.include_router(dashboard.router)
app.include_router(predict.router)
app.include_router(viz.router)
app.include_router(query.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)
