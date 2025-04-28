from flask import Flask
from .routes import main

def create_app():
    # app = Flask(__name__)
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    
    app.config.from_object('config.Config')
    app.register_blueprint(main, url_prefix='/')
    return app
