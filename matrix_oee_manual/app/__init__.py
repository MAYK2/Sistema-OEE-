from flask import Flask
from config import Config
from app.extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'views.login'

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
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Context Processor for Global Active Order
    @app.context_processor
    def inject_global_active_order():
        from flask_login import current_user
        from app.models.work_order import WorkOrder, WorkOrderStatus
        
        active_order = None
        if current_user.is_authenticated:
            # Logic: Find ONE active order. 
            # If multiple lines are running, we might need a list or just pick the first one.
            # For now, let's pick the first one in EXECUTION status.
            active_order = WorkOrder.query.filter_by(status=WorkOrderStatus.EXECUTION).first()
            
        return dict(global_active_order=active_order)

    return app
