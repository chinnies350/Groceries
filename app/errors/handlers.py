from flask import Blueprint, jsonify
from werkzeug.exceptions import HTTPException
errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    # return render_template('errors/404.html'), 404
    return jsonify({"message": "Page Not Found", "statusCode": 0}), 404


@errors.app_errorhandler(403)
def error_403(error):
    # return render_template('errors/403.html'), 403
    return jsonify({"message": "Access Denied or restricted", "statusCode": 0}), 403


@errors.app_errorhandler(405)
def error_405(error):
    # return render_template('errors/403.html'), 403
    return jsonify({"message": "Access Denied or restricted", "statusCode": 0}), 405


@errors.app_errorhandler(500)
def error_500(error):
    print("error")
    # return render_template('errors/500.html'), 500
    return jsonify({"message": "Sorry some error occurred", "statusCode": 0}), 500


@errors.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
            code = e.code
    return {"message": e, "statusCode": 0}
