from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta, date
from app.extensions import db
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.product import Product
from app.models.client import Client
from app.models.downtime import DowntimeEvent
from app.models.user import User

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('views.create_order'))
    # Solo buscamos órdenes que el operario pueda ver para trabajar
    # PENDING: Creadas pero no iniciadas
    # EXECUTION: Órdenes que ya están corriendo (cronómetro activo)
    orders = WorkOrder.query.filter(
        WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.EXECUTION])
    ).all()
    
    return render_template('index.html', orders=orders)

@views_bp.route('/orders/new', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            
            # --- Lógica de Cliente (Tu código original) ---
            client_mode = data.get('client_mode')
            client_id = None
            
            if client_mode == 'existing':
                client_id = data.get('existing_client_id')
            elif client_mode == 'new':
                new_client_name = data.get('new_client_name')
                new_client_phone = data.get('new_client_phone')
                new_client_email = data.get('new_client_email')
                new_client = Client(name=new_client_name, phone=new_client_phone, email=new_client_email)
                db.session.add(new_client)
                db.session.commit()
                client_id = new_client.id
            
            # --- Fecha Estimada ---
            estimated_finish_str = data.get('estimated_finish')
            estimated_finish = None
            if estimated_finish_str:
                try:
                    estimated_finish = datetime.strptime(estimated_finish_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    pass

            # --- Crear Órdenes ---
            items = data.get('items', [])
            created_count = 0
            
            for item in items:
                count = WorkOrder.query.count()
                year = datetime.now().year
                ot_number = f"OT-{year}-{count + 1 + created_count:04d}" # Ajuste para que no repita si creas varias
                
                planned_quantity = item.get('quantity')
                
                new_order = WorkOrder(
                    ot_number=ot_number,
                    client_id=client_id,
                    product_id=item.get('product_id'),
                    planned_quantity=planned_quantity,
                    estimated_finish=estimated_finish,
                    status=WorkOrderStatus.PENDING
                )
                db.session.add(new_order)
                created_count += 1
            
            db.session.commit()
            return jsonify({'message': f'{created_count} órdenes creadas correctamente'}), 200
        
        return redirect(url_for('views.index'))

    # GET request
    products = Product.query.all()
    clients = Client.query.all()
    today_date = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('create_order.html', products=products, clients=clients, today_date=today_date)

@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('views.index'))
        else:
            error = "Usuario o contraseña incorrectos"
            
    return render_template('login.html', error=error)

@views_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))

@views_bp.route('/operate/<int:order_id>')
@login_required
def operate(order_id):
    # FORCE FRESH SESSION to ensure we see the latest downtimes/status changes
    db.session.remove()
    
    order = WorkOrder.query.get_or_404(order_id)
    
    # Calcular Tiempos de Parada
    downtimes = DowntimeEvent.query.filter_by(work_order_id=order.id).all()
    total_downtime_seconds = sum(d.duration_seconds for d in downtimes if d.duration_seconds)
    
    # Verificar si hay una pausa activa ahora mismo (Prioritize latest if multiple exist)
    open_downtimes = [d for d in downtimes if d.end_time is None]
    open_downtimes.sort(key=lambda x: x.start_time, reverse=True)
    current_pause = open_downtimes[0] if open_downtimes else None
    
    pause_start_iso = None
    is_changeover = False
    
    if current_pause and current_pause.start_time:
        pause_start_iso = current_pause.start_time.isoformat()
        if current_pause.reason == "Cambio de Paso":
            is_changeover = True

    # CORRECCIÓN: Usar 'start_time' estándar en lugar de '_real'
    # Calculate elapsed seconds server-side for robust stopwatch
    initial_elapsed_seconds = 0
    now_time = datetime.now()
    
    # SELF-HEALING: If order is EXECUTION but has no start_time (Data Corruption Fix)
    if order.status == WorkOrderStatus.EXECUTION and not order.start_time:
         from datetime import timedelta
         # Recovery: Set start time to now so timer resumes/starts
         order.start_time = now_time
         db.session.commit()

    if order.start_time:
         # If order is finished, clamp to end_time
         if order.status == WorkOrderStatus.FINISHED and order.end_time:
             now_time = order.end_time
             
         # If we are currently paused, the clock shouldn't be "ticking" past the pause start
         # But the total_downtime calculation already sums CLOSED downtimes.
         # So: Elapsed = (Now - Start) - ClosedDowntimes - CurrentOpenDowntimeDuration
         
         total_duration = (now_time - order.start_time).total_seconds()
         
         current_pause_duration = 0
         if current_pause and current_pause.start_time:
              current_pause_duration = (now_time - current_pause.start_time).total_seconds()
              
         initial_elapsed_seconds = int(max(0, total_duration - total_downtime_seconds - current_pause_duration))
         
         initial_elapsed_seconds = int(max(0, total_duration - total_downtime_seconds - current_pause_duration))
         
    # Log unconditionally to debug why start_time is missing
    try:
         with open('/tmp/matrix_debug.log', 'a') as f:
             f.write(f"DEBUG_VIEW: OT={order.ot_number} ID={order.id}\n")
             f.write(f"   Status={order.status.name} StartTime={order.start_time}\n")
             f.write(f"   Now={now_time} Elapsed={initial_elapsed_seconds}\n")
    except Exception as e:
         pass

    return render_template('operator.html', 
                           order=order, 
                           initial_elapsed_seconds=initial_elapsed_seconds,
                           pause_start_iso=pause_start_iso,
                           is_changeover=is_changeover)

# --- API ENDPOINTS ---

@views_bp.route('/api/orders/<int:id>/start', methods=['POST'])
@login_required
def start_order(id):
    # FORCE FRESH SESSION to avoid stale reads (Isolation Level issues)
    # Ensure any previous transaction state is cleared so we see updates from other requests (like verify/pause)
    db.session.remove() 

    order = WorkOrder.query.get_or_404(id)
    data = request.get_json() or {}
    
    # ROBUSTNESS: Always check for open downtimes and close them when starting
    # This ensures that even if status transition logic was bypassed/buggy, we don't leave open pauses ticking
    # Get the LATEST open downtime (in case of multiple zombies)
    open_downtime = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None)\
                                       .order_by(DowntimeEvent.start_time.desc())\
                                       .first()
    
    if open_downtime:
        open_downtime.end_time = datetime.now()
        # Calculate duration
        delta = open_downtime.end_time - open_downtime.start_time
        open_downtime.duration_seconds = int(delta.total_seconds())
        # Commit immediately to ensure consistency
        db.session.add(open_downtime)
        db.session.commit()

    # Logic to start order if PENDING (New or Paused)
    if order.status == WorkOrderStatus.PENDING:
        # Change status to EXECUTION
        order.status = WorkOrderStatus.EXECUTION
        
        # Record start time only if it's the first start
        if not order.start_time: 
            order.start_time = datetime.now()
            
        # Save operators count if provided
        if 'operators_count' in data:
            order.operators_count = int(data['operators_count'])
            
        db.session.commit()
        
        with open('/tmp/matrix_debug.log', 'a') as f:
             f.write(f"DEBUG_START: OT={order.ot_number} ID={order.id}\n")
             f.write(f"   Set StartTime={order.start_time}\n")
        
        return jsonify({
            "message": "Order started", 
            "status": order.status.value, 
            "start_time": order.start_time.isoformat()
        })
    
    # Si la orden ya estaba en ejecución, no hacemos nada
    return jsonify({"error": "Invalid status transition"}), 400

@views_bp.route('/api/orders/<int:id>/pause', methods=['POST'])
@login_required
def pause_order(id):
    order = WorkOrder.query.get_or_404(id)
    data = request.get_json()
    reason = data.get('reason', 'Sin motivo especificado')

    if order.status == WorkOrderStatus.EXECUTION or order.status == WorkOrderStatus.IN_PROGRESS:
        order.status = WorkOrderStatus.PENDING # Usamos PENDING como estado de Pausa visual
        
        # Crear evento de parada
        downtime = DowntimeEvent(
            work_order_id=order.id,
            reason=reason,
            comment=data.get('comment'),
            start_time=datetime.now()
        )
        db.session.add(downtime)
        db.session.commit()
        return jsonify({"message": "Order paused", "status": order.status.value})
        
    return jsonify({"error": "Order must be in EXECUTION to pause"}), 400

@views_bp.route('/api/orders/<int:id>/finish', methods=['POST'])
@login_required
def finish_order(id):
    order = WorkOrder.query.get_or_404(id)
    data = request.get_json() or {}
    
    # Guardar cantidad final ingresada por el usuario
    if 'produced_quantity' in data:
         order.total_produced = int(data['produced_quantity'])

    order.status = WorkOrderStatus.FINISHED
    # CORRECCIÓN: Usar 'end_time' estándar
    order.end_time = datetime.now()
    
    # Cerrar pausas abiertas si quedaron
    downtime = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None).first()
    if downtime:
        downtime.end_time = order.end_time
        downtime.duration_seconds = int((downtime.end_time - downtime.start_time).total_seconds())

    db.session.commit()
    return jsonify({"message": "Order finished", "status": order.status.value})

# --- CHANGEOVER ENDPOINTS ---
@views_bp.route('/api/orders/<int:id>/changeover/start', methods=['POST'])
@login_required
def start_changeover(id):
    # Force Session Refresh
    db.session.remove()

    order = WorkOrder.query.get_or_404(id)
    
    # Check if already in changeover or running
    if order.status != WorkOrderStatus.PENDING:
         return jsonify({"error": "Order must be PENDING to start changeover"}), 400

    # Check for open events
    open_event = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None).first()
    if open_event:
        return jsonify({"error": "An event is already in progress"}), 400

    # Create Changeover Event
    event = DowntimeEvent(
        work_order_id=order.id,
        reason="Cambio de Paso",
        start_time=datetime.now()
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"message": "Changeover started", "start_time": event.start_time.isoformat()})

@views_bp.route('/api/orders/<int:id>/changeover/stop', methods=['POST'])
@login_required
def stop_changeover(id):
    # Force Session Refresh
    db.session.remove()

    order = WorkOrder.query.get_or_404(id)
    
    # Find the open changeover event
    open_event = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None).first()
    
    if not open_event:
        return jsonify({"message": "No active changeover found"}), 200
        
    open_event.end_time = datetime.now()
    delta = open_event.end_time - open_event.start_time
    open_event.duration_seconds = int(delta.total_seconds())
    
    db.session.commit()
    
    return jsonify({"message": "Changeover stopped", "duration": open_event.duration_seconds})

# --- REPORTES ---

@views_bp.route('/history')
@login_required
def history():
    orders = WorkOrder.query.filter_by(status=WorkOrderStatus.FINISHED)\
                            .order_by(WorkOrder.end_time.desc())\
                            .all()
    return render_template('history.html', orders=orders)

@views_bp.route('/report/<int:id>')
@login_required
def report_detail(id):
    order = WorkOrder.query.get_or_404(id)
    
    # Generate Chronological Activity Log
    timeline = []
    
    # Start point
    current_pivot = order.start_time
    
    # Sort events just in case
    events = sorted(order.downtime_events, key=lambda x: x.start_time)
    
    order_end = order.end_time if order.end_time else datetime.now()

    for dt in events:
        # 1. Identify Production Block before this downtime
        # If there is a gap between current_pivot and dt.start_time, that's Production
        if dt.start_time > current_pivot:
            prod_duration = (dt.start_time - current_pivot).total_seconds()
            if prod_duration > 1: # Ignore micro-gaps
                timeline.append({
                    'type': 'production',
                    'start_time': current_pivot,
                    'end_time': dt.start_time,
                    'reason': 'Producción (En Ejecución)',
                    'duration_seconds': int(prod_duration),
                    'color': 'success',
                    'icon': 'bi-gear-fill spin-slow'
                })
        
        # 2. Add the Downtime Block
        dt_end = dt.end_time if dt.end_time else order_end
        timeline.append({
            'type': 'downtime',
            'start_time': dt.start_time,
            'end_time': dt.end_time, # Can be None if active
            'reason': dt.reason,
            'comment': dt.comment,
            'duration_seconds': dt.duration_seconds if dt.end_time else int((datetime.now() - dt.start_time).total_seconds()),
            'color': 'info' if dt.reason == 'Cambio de Paso' else 'danger',
            'icon': 'bi-tools' if dt.reason == 'Cambio de Paso' else 'bi-pause-circle-fill'
        })
        
        # Move pivot
        current_pivot = dt_end
    
    # 3. Check for final Production Block (after last downtime)
    if current_pivot and current_pivot < order_end:
         prod_duration = (order_end - current_pivot).total_seconds()
         if prod_duration > 1:
             timeline.append({
                    'type': 'production',
                    'start_time': current_pivot,
                    'end_time': order.end_time, # None if running
                    'reason': 'Producción (En Ejecución)',
                    'duration_seconds': int(prod_duration),
                    'color': 'success',
                    'icon': 'bi-gear-fill spin-slow'
            })
            
    return render_template('report_detail.html', order=order, timeline=timeline)

@views_bp.route('/reports')
@login_required
def reports():
    # Filtros
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    client_id = request.args.get('client_id')

    query = WorkOrder.query.filter_by(status=WorkOrderStatus.FINISHED)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(WorkOrder.end_time >= start_date)
        except ValueError:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query = query.filter(WorkOrder.end_time <= end_date)
        except ValueError:
            pass

    if client_id:
        query = query.filter_by(client_id=int(client_id))

    orders = query.all()
    clients = Client.query.all()

    # Lógica de Agregación para Reportes
    final_report = get_report_data_helper(orders)
    
    return render_template('reports.html', report_data=final_report, clients=clients)

def get_report_data_helper(orders):
    report_data = {} 
    for order in orders:
        pid = order.product_id
        if pid not in report_data:
            report_data[pid] = {
                'product_name': order.product.name,
                'orders_count': 0,
                'total_produced': 0,
                'total_run_time': 0,
                'total_downtime': 0
            }
        
        # Usamos propiedades seguras del modelo o cálculo manual si falla
        run_time = getattr(order, 'run_time_seconds', 0)
        dt_seconds = sum(d.duration_seconds for d in order.downtime_events if d.duration_seconds)
        
        report_data[pid]['orders_count'] += 1
        report_data[pid]['total_produced'] += order.total_produced
        report_data[pid]['total_run_time'] += run_time
        report_data[pid]['total_downtime'] += dt_seconds

    final_report = []
    for pid, data in report_data.items():
        final_report.append({
            'product_name': data['product_name'],
            'orders_count': data['orders_count'],
            'total_produced': data['total_produced'],
            'run_time_minutes': round(data['total_run_time'] / 60, 1),
            'downtime_minutes': round(data['total_downtime'] / 60, 1)
        })
    return final_report

@views_bp.route('/reports/export')
@login_required
def export_reports():
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    from io import BytesIO
    from flask import send_file

    # --- Reusing Filter Logic (Duplicated slightly for standalone nature, or extract to helper if used 3+ times) ---
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    client_id = request.args.get('client_id')

    query = WorkOrder.query.filter_by(status=WorkOrderStatus.FINISHED)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(WorkOrder.end_time >= start_date)
        except ValueError:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query = query.filter(WorkOrder.end_time <= end_date)
        except ValueError:
            pass

    if client_id:
        query = query.filter_by(client_id=int(client_id))

    orders = query.all()
    data = get_report_data_helper(orders)

    # --- Create Excel ---
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte Matrix OEE"

    # Add Period Info Row
    period_text = "Periodo: Historial Completo"
    if start_date_str and end_date_str:
        period_text = f"Periodo: {start_date_str} al {end_date_str}"
    elif start_date_str:
        period_text = f"Periodo: Desde {start_date_str}"
    elif end_date_str:
        period_text = f"Periodo: Hasta {end_date_str}"

    ws.append([period_text])
    ws.merge_cells('A1:E1') # Merge across 5 columns
    
    title_cell = ws['A1']
    title_cell.font = Font(size=12, bold=True, italic=True)
    title_cell.alignment = Alignment(horizontal="center")

    # Headers (Now on Row 2)
    headers = ["Producto", "N° Órdenes", "Total Producido", "Tiempo Ejecución (min)", "Tiempo Paradas (min)"]
    ws.append(headers)

    # Style Header
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1a1a2e", end_color="1a1a2e", fill_type="solid") # Dark Blue
    
    for cell in ws[2]: # Row 2 is headers now
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # Data
    for row in data:
        ws.append([
            row['product_name'],
            row['orders_count'],
            row['total_produced'],
            row['run_time_minutes'],
            row['downtime_minutes']
        ])

    # Auto-adjust columns
    for col in ws.columns:
        max_length = 0
        # Use Row 2 (Header) to get column letter to avoid MergedCell in Row 1
        # col[0] is Row 1, col[1] is Row 2
        try:
            column = get_column_letter(col[1].column)
        except:
             column = get_column_letter(col[0].column)

        for cell in col:
            # Skip Row 1 (Title) so it doesn't mess up widths for columns A-E
            if cell.row == 1:
                continue
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Generate Stream
    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)
    
    filename = f"Reporte_Produccion_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

    return send_file(
        excel_stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

from app.services.time_sync import get_network_time

@views_bp.route('/dashboard')
@login_required
def dashboard():
    # Use Network Time for accurate Dashboard Date/Day
    now_network = get_network_time()
    today = now_network.date()
    
    start_day = datetime.combine(today, datetime.min.time())
    start_week = start_day - timedelta(days=today.weekday())
    start_month = start_day.replace(day=1)
    
    # Helper to aggregate production by product
    def get_stats(start_date):
        orders = WorkOrder.query.filter(
            WorkOrder.status == WorkOrderStatus.FINISHED,
            WorkOrder.end_time >= start_date
        ).all()
        
        stats = {}
        for order in orders:
            p_name = order.product.name
            if p_name not in stats:
                stats[p_name] = 0
            stats[p_name] += order.total_produced
        return stats

    # Helper for Downtime Reason Stats (Aggregated for ALL time or this Month?)
    # User asked for "estadistica de pausas", usually monthly is a good default for dashboards.
    def get_downtime_stats(start_date):
        # We query DowntimeEvents directly that have a reason
        downtimes = DowntimeEvent.query.filter(
            DowntimeEvent.start_time >= start_date,
            DowntimeEvent.reason != None
        ).all()

        reason_counts = {}
        total_events = 0

        for dt in downtimes:
            # Clean up reason string if it starts with "Otro: "
            # Or just group raw. Let's group raw first, or group "Otro: ..." as "Otro" if too diverse?
            # User wants to know specific causes... so full string is better, 
            # maybe truncate if too long in UI.
            r = dt.reason
            
            # Allow grouping "Otro: xyz" into "Otro" if requested, but user said "aclarar que motivo fue".
            # So unique reasons are good.
            if r.startswith("Otro:"):
                # Clean up display? Maybe just "Otro" for the chart if there are too many unique ones?
                # For now let's keep the full text so the boss knows.
                pass

            if r not in reason_counts:
                reason_counts[r] = 0
            reason_counts[r] += 1
            total_events += 1
            
        # Calculate percentages
        reason_stats = {}
        if total_events > 0:
            for r, count in reason_counts.items():
                reason_stats[r] = round((count / total_events) * 100, 1)
        
        return reason_stats

    # Helper for Time Stats (Run Time vs Downtime)
    def get_time_stats(start_date):
        orders = WorkOrder.query.filter(
            WorkOrder.status == WorkOrderStatus.FINISHED,
            WorkOrder.end_time >= start_date
        ).all()
        
        sum_run_seconds = 0
        sum_changeover_seconds = 0
        sum_stops_seconds = 0
        
        for order in orders:
            # Safely get run_time_seconds property
            sum_run_seconds += getattr(order, 'run_time_seconds', 0)
            
            # Calculate downtime sums
            for d in order.downtime_events:
                if d.duration_seconds:
                    if d.reason == "Cambio de Paso":
                        sum_changeover_seconds += d.duration_seconds
                    else:
                        sum_stops_seconds += d.duration_seconds
            
        # Convert to Minutes for display/chart
        # RETURN ORDER MATTERS FOR CHART COLORS: Green, Blue, Red
        return {
            'T. Ejecución': round(sum_run_seconds / 60, 1),
            'T. Cambio de Paso': round(sum_changeover_seconds / 60, 1),
            'T. Paradas': round(sum_stops_seconds / 60, 1)
        }

    # --- ADVANCED ANALYTICS (Timeline, Pareto, OEE) ---
    def get_timeline_data(target_date):
        next_day = target_date + timedelta(days=1)
        # Fetch orders active during this day
        orders = WorkOrder.query.filter(
            WorkOrder.start_time < next_day,
            (WorkOrder.end_time >= target_date) | (WorkOrder.end_time == None)
        ).all()
        
        timeline_events = []
        
        for order in orders:
            # Clamp event to the target day for clearer visualization
            effective_start = max(order.start_time, target_date)
            effective_end = order.end_time if order.end_time else datetime.now()
            effective_end = min(effective_end, next_day)
            
            if effective_end <= effective_start:
                continue

            # 1. Base Block: Production (Green)
            timeline_events.append({
                'x': [effective_start.isoformat(), effective_end.isoformat()],
                'y': 'Línea 1', # Single lane for now
                'fillColor': '#27ae60', # Green
                'label': f"{order.product.name if order.product else 'N/A'} (OT-{order.id})",
                'type': 'Production'
            })
            
            # 2. Overlay Downtime Events (Red/Blue)
            for d in order.downtime_events:
                d_start = max(d.start_time, target_date)
                d_end = d.end_time if d.end_time else datetime.now()
                d_end = min(d_end, next_day)
                
                if d_end <= d_start:
                    continue
                
                # Define Color Map
                fill_color = '#95a5a6' # Default Grey
                
                r_lower = d.reason.lower() if d.reason else "otro"
                
                if "cambio" in r_lower:
                    fill_color = '#2980b9' # Blue
                elif "falla" in r_lower:
                    fill_color = '#c0392b' # Red
                elif "insumo" in r_lower:
                    fill_color = '#e67e22' # Orange
                elif "limpieza" in r_lower or "descanso" in r_lower:
                    fill_color = '#f1c40f' # Yellow
                elif "otro" in r_lower:
                    fill_color = '#9b59b6' # Purple
                
                timeline_events.append({
                    'x': [d_start.isoformat(), d_end.isoformat()],
                    'y': 'Línea 1',
                    'fillColor': fill_color,
                    'label': d.reason,
                    'type': 'Downtime'
                })
        
        return timeline_events

    def get_downtime_pareto(start_date):
        orders = WorkOrder.query.filter(WorkOrder.end_time >= start_date).all()
        reasons = {}
        
        for order in orders:
            for d in order.downtime_events:
                if d.duration_seconds and d.reason != "Cambio de Paso": # Exclude changeover from Pareto? usually yes.
                    if d.reason not in reasons:
                        reasons[d.reason] = 0
                    reasons[d.reason] += d.duration_seconds
        
        # Sort by duration DESC
        sorted_reasons = sorted(reasons.items(), key=lambda item: item[1], reverse=True)
        
        total_downtime = sum(reasons.values())
        
        return {
            'labels': [r[0] for r in sorted_reasons],
            'data': [round(r[1] / 60, 1) for r in sorted_reasons], # Minutes
            'total_minutes': round(total_downtime / 60, 1)
        }

    def get_oee_gauge(start_date):
         # Creating a simplified OEE (Availability only)
        time_stats = get_time_stats(start_date)
        run = time_stats['T. Ejecución']
        # Total Available Time = Run + Stops + Changeover
        total = run + time_stats['T. Cambio de Paso'] + time_stats['T. Paradas']
        
        if total == 0:
            return 0
        
        return round((run / total) * 100, 1)

    # Calculate dates
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    stats = {
        'day': get_stats(start_day),
        'week': get_stats(start_week),
        'month': get_stats(start_month),
        'downtime_month': get_downtime_stats(start_month),
        'time_week': get_time_stats(start_week),
        'time_month': get_time_stats(start_month),
        # New Stats
        'timeline': get_timeline_data(today_start),
        'pareto': get_downtime_pareto(month_start_date),
        'oee_percent': get_oee_gauge(month_start_date)
    }

    # --- ANALÍTICA DE PRODUCCIÓN (INCREMENTAL/PROMEDIOS) ---
    # Usamos los últimos 30 días como ventana, pero calculamos el promedio
    # basado en el tiempo REAL transcurrido desde la primera orden en ese periodo.
    # Esto evita diluir los promedios cuando se tienen pocos días de datos (ej: día 1).
    
    window_days = 30
    last_30_days_date = datetime.now() - timedelta(days=window_days)
    
    orders_30d = WorkOrder.query.filter(
        WorkOrder.status == WorkOrderStatus.FINISHED,
        WorkOrder.end_time >= last_30_days_date
    ).all()
    
    product_stats = {}
    first_order_dates = {}
    total_products = {} # Restored missing dict
    
    total_liters_30d = 0

    for o in orders_30d:
        if o.product:
            p_name = o.product.name
            
            # --- Liter Calculation Logic ---
            qty = o.total_produced or 0
            name_lower = p_name.lower()
            volume = 0
            
            if "soda" in name_lower or "sifon" in name_lower:
                volume = 1 # User specified 1L for sodas
            elif "bidon" in name_lower or "botellon" in name_lower:
                if "10" in name_lower:
                    volume = 10
                else:
                    volume = 20 # Default to 20L if not specified
            
            total_liters_30d += (qty * volume)
            # -------------------------------

            if p_name not in total_products:
                total_products[p_name] = 0
                first_order_dates[p_name] = o.end_time # Start calculating from first finished order
            
            total_products[p_name] += qty
            
            # Keep track of the oldest order for this product in the window
            if o.end_time < first_order_dates[p_name]:
                first_order_dates[p_name] = o.end_time

    product_analytics = []
    now = datetime.now()

    # Calcular métricas dinámicas
    for p_name, total in total_products.items():
        # Calcular días activos desde la primera orden encontrada
        delta_days = (now - first_order_dates[p_name]).days
        days_active = max(1, delta_days + 1) # Mínimo 1 día para evitar división por cero
        
        # Semanas activas (si pasaron 1 a 7 días -> 1 semana)
        import math
        weeks_active = max(1, math.ceil(days_active / 7))
        
        daily_avg = int(total / days_active)
        weekly_avg = int(total / weeks_active)
        monthly_avg = total # El total del periodo (Max 30 días)
        
        product_analytics.append({
            'name': p_name,
            'daily': daily_avg,
            'weekly': weekly_avg,
            'monthly': monthly_avg
        })
    
    # Translate Date Names to Spanish
    weekdays_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    current_day_name = weekdays_es[today.weekday()]
    current_month_name = months_es[today.month]

    # --- Company Target Logic (Placeholder) ---
    monthly_target = 100000 # Example target from "The Boss"
    current_production = sum(stats['month'].values())
    target_compliance = int((current_production / monthly_target) * 100) if monthly_target > 0 else 0
    target_data = {
        'target': monthly_target,
        'current': current_production,
        'percentage': target_compliance,
        'status': 'En Camino' if target_compliance >= 50 else 'Atrasado' # Simple logic
    }
    
    return render_template('dashboard.html', 
                           stats=stats, 
                           product_analytics=product_analytics, 
                           total_liters_30d=int(total_liters_30d), 
                           target_data=target_data,
                           date_names={'day': current_day_name, 'month': current_month_name})
