import time, logging
from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse

from middlewares.process_duration import ProcessDurationMiddleware
from api.users import get_user_repository, router as users_router
app = FastAPI(title="rempy")
app.add_middleware(ProcessDurationMiddleware)
app.include_router(users_router)


# @app.middleware("http")
# async def add_processing_duration(request: Request, call_next):
#     start_time = time.perf_counter()
#     response = await call_next(request)
#     process_duration = time.perf_counter() - start_time
#     logging.basicConfig(level=logging.INFO)
#     logging.info(f"this request took {process_duration} seconds")
#     response.headers["X-Process-Duration"] = str(process_duration)
#     return response
#
#
# @app.middleware("http")
# async def check_header(request: Request, call_next):
#     header = request.headers.get("X-User-Type")
#     if header is None:
#         logging.error("no user type")
#         return JSONResponse(content={"error": "you are not allowed in man"},status_code=401)
#     if header != "itsme":
#         logging.error("user type is not itsme")
#         return JSONResponse(content={"error": "Not the right type of user"},status_code=401)
#
#     return await call_next(request)
#

@app.on_event("startup")
def _ensure_schema() -> None:
    get_user_repository().ensure_schema()
