from app.extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=False)
    theoretical_cycle_seconds = db.Column(db.Float, nullable=False)

    work_orders = db.relationship('WorkOrder', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'
