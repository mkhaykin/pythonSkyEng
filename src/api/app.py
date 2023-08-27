from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from src.api.v1.handlers.routes import router
from src.app import create_app as get_flask_app


fastapi_app = FastAPI()
fastapi_app.include_router(router)
fastapi_app.mount(
    path='/',
    app=WSGIMiddleware(get_flask_app())
)
