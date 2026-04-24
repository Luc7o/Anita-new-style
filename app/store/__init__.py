from flask import Blueprint

store_bp = Blueprint(
    'store',
    __name__,
    template_folder='../../templates/store',
    static_folder='../../static'
)

from app.store import routes