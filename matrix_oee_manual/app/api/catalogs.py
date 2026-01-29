from flask import Blueprint, jsonify

catalogs_bp = Blueprint('catalogs', __name__)

@catalogs_bp.route('/test', methods=['GET'])
def test_catalogs():
    return jsonify({"message": "Catalogs API working"})
