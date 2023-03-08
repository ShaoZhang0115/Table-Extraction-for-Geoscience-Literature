import logging
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

import consts, settings
from api import router
from core.exceptions import *

logger = logging.getLogger(__name__)


class ErrorModel(BaseModel):
    detail: str = Field(..., example="error")


app = FastAPI(
    title=settings.prefix,
    openapi_tags=[
        {"name": "file", "description": "用户上传和获取文件API"},
        {"name": "table", "description": "表格服务"},
    ],
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for arg in consts.__dict__.keys():
    if arg.endswith("_DIR"):
        os.makedirs(consts.__dict__[arg], exist_ok=True)

app.mount(consts.IMG_BASE_URL, StaticFiles(directory=consts.IMG_DIR), name="img")

app.include_router(
    router,
    prefix="/api",
    responses={
        403: {
            "description": "用户上传的信息有误，导致无法处理。",
            "model": ErrorModel,
        },
        500: {
            "description": "服务器内部错误",
            "content": {"text/plain": {"example": "Internal Server Error"}},
        },
    },
)


@app.exception_handler(HTTPException)
@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    data = None
    try:
        data = await request.body()
    except:
        pass

    logger.error(f"error request: {request.client} {request.method} {request.url} {data}", exc_info=exc)
    status_code = getattr(exc, "status_code", 500)
    if isinstance(exc, ServerError):
        status_code = 500
    elif isinstance(exc, UserError):
        status_code = 400
    elif isinstance(exc, UnknownError):
        status_code = 500
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": getattr(exc, "detail", None) or getattr(exc, "msg", None) or str(exc),
            "code": getattr(exc, "code", None) or "",
        },
    )


# heartbeat api
@app.get("/ping")
def ping():
    return "pong"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # log_config="log.yaml",
        log_level=settings.LOG_LEVEL,
    )
