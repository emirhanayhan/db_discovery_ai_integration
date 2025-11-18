from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

class AppException(Exception):
    def __init__(self, error_message, error_code, status_code):
        self.error_message = error_message
        self.error_code = error_code
        self.status_code = status_code

def init_exception_handler(app):
    @app.exception_handler(Exception)
    async def exception_handler(rq, exc: Exception):
        if isinstance(exc, AppException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"error_msg": exc.error_message, "error_code": exc.error_code}
            )
        elif isinstance(exc, IntegrityError):
            return JSONResponse(
                status_code=409,
                content={"error_code": "errors.uniqueViolation"}
            )
        return JSONResponse(
            status_code=getattr(exc, "status_code", 500),
            content={
                "error_msg": "internal server error {}".format(type(exc).__name__),
                "error_code": "exceptions.internalServerError"
            }
        )
