from app.extensions import db
from datetime import datetime
import enum

class WorkOrderStatus(enum.Enum):
    PENDING = 'Pendiente'
    PREPARATION = 'Preparacion'
    EXECUTION = 'Ejecucion'  # Este es el que usa el views.py
    FINISHED = 'Finalizada'

class WorkOrder(db.Model):
    __tablename__ = 'work_orders'

    id = db.Column(db.Integer, primary_key=True)
    # CORREGIDO: Eliminada la línea duplicada de ot_number
    ot_number = db.Column(db.String(50), unique=True, nullable=False)
    
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    status = db.Column(db.Enum(WorkOrderStatus), default=WorkOrderStatus.PENDING, nullable=False)
    
    # Critical: Defined at start
    operator_count = db.Column(db.Integer, nullable=True)
    planned_quantity = db.Column(db.Integer, default=0)
    
    # Timestamps (CORREGIDO: Nombres estandarizados para coincidir con views.py)
    created_at = db.Column(db.DateTime, default=datetime.now)
    estimated_finish = db.Column(db.DateTime, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True) # Antes start_time_real
    end_time = db.Column(db.DateTime, nullable=True)   # Antes end_time_real
    
    # Counters
    total_produced = db.Column(db.Integer, default=0)
    total_defective = db.Column(db.Integer, default=0)
    sensor_count = db.Column(db.Integer, default=0)
    manual_count_modified = db.Column(db.Boolean, default=False)

    # Relaciones
    downtime_events = db.relationship('DowntimeEvent', backref='work_order', lazy=True)

    def __repr__(self):
        return f'<WorkOrder {self.ot_number}>'

    # --- OEE Properties ---
    
    @property
    def total_time_seconds(self):
        """Total elapsed time since start (including downtimes)."""
        # CORREGIDO: Referencia a self.start_time
        if not self.start_time:
            return 0
        end = self.end_time if self.end_time else datetime.now()
        return max(0, int((end - self.start_time).total_seconds()))

    @property
    def total_downtime_seconds_calc(self):
        """Sum of all CLOSED downtimes."""
        return sum(d.duration_seconds for d in self.downtime_events if d.duration_seconds)

    @property
    def run_time_seconds(self):
        """Productive time (Total - Downtime)."""
        # Evitar números negativos si el downtime es mayor al total por error de milisegundos
        return max(0, self.total_time_seconds - self.total_downtime_seconds_calc)

    @property
    def availability(self):
        """Availability % = Run Time / Total Time"""
        if self.total_time_seconds == 0:
            return 100.0 
        return round((self.run_time_seconds / self.total_time_seconds) * 100, 2)



    @property
    def compliance(self):
        """Plan Compliance % = (Produced / Planned) * 100"""
        if self.planned_quantity <= 0:
            return 0.0
        return round((self.total_produced / self.planned_quantity) * 100, 1)