from app.extensions import db

class Line(db.Model):
    __tablename__ = 'lines'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    # Configuration for Shift Hours (Default 08:00 - 17:00)
    shift_start = db.Column(db.Time, nullable=True) # Start of shift
    shift_end = db.Column(db.Time, nullable=True)   # End of shift

    products = db.relationship('Product', backref='line', lazy=True)

    def __repr__(self):
        return f'<Line {self.name}>'
