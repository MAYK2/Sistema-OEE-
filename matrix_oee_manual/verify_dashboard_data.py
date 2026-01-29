from app import create_app
from app.views import get_timeline_data, get_downtime_pareto, get_oee_gauge
from datetime import datetime

app = create_app()

with app.app_context():
    print("--- Verifying Timeline Data ---")
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    timeline = get_timeline_data(today)
    print(f"Timeline Events found: {len(timeline)}")
    if len(timeline) > 0:
        print(f"Sample Event: {timeline[0]}")

    print("\n--- Verifying Pareto Data ---")
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    pareto = get_downtime_pareto(month_start)
    print(f"Pareto Labels: {pareto.get('labels')}")
    print(f"Pareto Data: {pareto.get('data')}")

    print("\n--- Verifying OEE Gauge ---")
    oee = get_oee_gauge(month_start)
    print(f"OEE Availability: {oee}%")
