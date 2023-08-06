from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import load_next_fase

app = FastAPI(title="load_next_fase_service")


@app.exception_handler(Exception)
def exceptions_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=400,
        content={"message": "Error inesperado. " + str(exc)},
    )


@app.get("/load_next_fase")
def load_next_fase_handler():
    resp = load_next_fase.main()

    return JSONResponse(
        status_code=200,
        content=resp
    )
