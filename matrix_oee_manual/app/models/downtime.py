from app.extensions import db
from datetime import datetime

# --- CLASES AUXILIARES (Estas se quedan) ---
class DowntimeStage:
    PENDING = 'PENDING'
    RESOLVED = 'RESOLVED'

class DowntimeType:
    STOP = 'STOP'
    PAUSE = 'PAUSE'
    CHANGEOVER = 'CHANGEOVER'
# -----------------------------------------

class DowntimeEvent(db.Model):
    __tablename__ = 'downtime_events'

    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    
    reason = db.Column(db.String(255), nullable=False)
    
    # Time Tracking
    start_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, default=0)
    comment = db.Column(db.String(500), nullable=True)

    # --- ELIMINAMOS LA LÍNEA QUE DABA ERROR ---
    # La relación ya existe desde el lado de WorkOrder, así que no la definimos aquí.
    
    def __repr__(self):
        return f'<Downtime {self.reason}>'