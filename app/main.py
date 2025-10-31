from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from routers import predict, kaggle_router
from services.scheduler import scheduler
import asyncio

app = FastAPI(title="Used Cars Price Prediction API (Ollama)")


@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(scheduler())

app.include_router(predict.router)
app.include_router(kaggle_router.router)


@app.get("/")
def root():
    return {"message": "Used Cars Prediction API running"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": f"Internal Server Error: {str(exc)}"})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "body": exc.body})
