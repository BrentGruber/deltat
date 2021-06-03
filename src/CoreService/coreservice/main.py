import time
import uvicorn
from fastapi import FastAPI, Request

from router import router as v1_router
from config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(v1_router, prefix=settings.API_V1_STR)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Adds an X-Process-Time header to response with how long the call took to execute
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

if __name__ == "__main__":
    if settings.ENVIRONMENT.upper() == "LOCAL":
        uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, log_level=settings.LOGLEVEL, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, log_level=settings.LOGLEVEL)