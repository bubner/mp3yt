from app import app
from waitress import serve
serve(app, host="0.0.0.0")