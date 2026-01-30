from app.extensions import db

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    work_orders = db.relationship('WorkOrder', backref='client', lazy=True)

    def __repr__(self):
        return f'<Client {self.name}>'
