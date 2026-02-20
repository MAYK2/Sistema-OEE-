from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.line import Line
import datetime

catalogs_bp = Blueprint('catalogs', __name__)

@catalogs_bp.route('/lines', methods=['GET'])
def get_lines():
    lines = Line.query.all()
    return jsonify([{
        'id': l.id, 
        'name': l.name, 
        'shift_start': l.shift_start.strftime('%H:%M') if l.shift_start else None,
        'shift_end': l.shift_end.strftime('%H:%M') if l.shift_end else None
    } for l in lines])

@catalogs_bp.route('/lines/<int:id>', methods=['PUT'])
def update_line(id):
    line = Line.query.get_or_404(id)
    data = request.get_json()
    
    if 'shift_start' in data:
        try:
             # Expect "HH:MM"
             t = datetime.datetime.strptime(data['shift_start'], '%H:%M').time()
             line.shift_start = t
        except ValueError:
             return jsonify({'error': 'Invalid format for shift_start (HH:MM required)'}), 400
             
    if 'shift_end' in data:
        try:
             t = datetime.datetime.strptime(data['shift_end'], '%H:%M').time()
             line.shift_end = t
        except ValueError:
             return jsonify({'error': 'Invalid format for shift_end (HH:MM required)'}), 400
             
    if 'name' in data:
        line.name = data['name']
        
    db.session.commit()
    return jsonify({'message': 'Line updated successfully', 'id': line.id})

@catalogs_bp.route('/test', methods=['GET'])
def test_catalogs():
    return jsonify({"message": "Catalogs API working"})
