from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

import logging, time

class ProcessDurationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)
        process_duration = time.perf_counter() - start_time
        logging.basicConfig(level=logging.INFO)
        #logging.debug(await request.body())
        logging.info(f"=======this request took {process_duration} seconds=====")
        response.headers["X-Process-Duration"] = str(process_duration)
        return response