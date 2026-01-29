from app.extensions import db

class Line(db.Model):
    __tablename__ = 'lines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    products = db.relationship('Product', backref='line', lazy=True)

    def __repr__(self):
        return f'<Line {self.name}>'
