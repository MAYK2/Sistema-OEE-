from flask import Flask
from config import Config
from app.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from app.api.orders import orders_bp
    from app.api.catalogs import catalogs_bp

    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(catalogs_bp, url_prefix='/api/catalogs')

    # Register Frontend Blueprint
    from app.views import views_bp
    app.register_blueprint(views_bp)

    # Import models so they are registered with SQLAlchemy
    from app.models.line import Line
    from app.models.product import Product
    from app.models.client import Client
    from app.models.work_order import WorkOrder
    from app.models.downtime import DowntimeEvent
    from app.models.downtime import DowntimeEvent

    return app
