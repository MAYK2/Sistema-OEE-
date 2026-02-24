from app import create_app
app = create_app()
with app.app_context():
    from werkzeug.routing import MapAdapter
    adapter = app.url_map.bind('localhost:5052')
    try:
        match = adapter.match('/api/orders/65/status_realtime', method='GET')
        print("Match:", match)
    except Exception as e:
        print("Error:", e)
