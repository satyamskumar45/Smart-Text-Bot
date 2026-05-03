from flask import current_app
from werkzeug.exceptions import HTTPException

from utils.response import error


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(exc):
        return error(str(exc.description), status_code=getattr(exc, 'code', 500))

    @app.errorhandler(ValueError)
    def handle_value_error(exc):
        current_app.logger.info("Validation error: %s", exc)
        return error(str(exc), status_code=400)

    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        current_app.logger.exception("Unhandled exception: %s", exc)
        return error("Internal server error", status_code=500)
