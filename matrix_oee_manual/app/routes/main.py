from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from app.extensions import db
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.product import Product
from app.models.client import Client

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('main.create_order'))
    
    orders = WorkOrder.query.filter(
        WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.EXECUTION])
    ).all()
    
    return render_template('index.html', orders=orders)

@main_bp.route('/orders/new', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            
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
            
            estimated_finish_str = data.get('estimated_finish')
            estimated_finish = None
            if estimated_finish_str:
                try:
                    estimated_finish = datetime.strptime(estimated_finish_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    pass

            items = data.get('items', [])
            created_count = 0
            
            year = datetime.now().year
            last_order = WorkOrder.query.filter(WorkOrder.ot_number.like(f'OT-{year}-%'))\
                                        .order_by(WorkOrder.id.desc())\
                                        .first()
            
            last_seq = 0
            if last_order:
                try:
                    last_seq = int(last_order.ot_number.split('-')[-1])
                except ValueError:
                    pass

            for item in items:
                new_seq = last_seq + 1 + created_count
                ot_number = f"OT-{year}-{new_seq:04d}"
                
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
        
        return redirect(url_for('main.index'))

    products = Product.query.all()
    clients = Client.query.all()
    today_date = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('create_order.html', products=products, clients=clients, today_date=today_date)

from datetime import timedelta

@main_bp.route('/general-analytics')
@login_required
def general_analytics():
    window_days = 30
    last_30_days_date = datetime.now() - timedelta(days=window_days)
    
    orders_30d = WorkOrder.query.filter(
        WorkOrder.status == WorkOrderStatus.FINISHED,
        WorkOrder.end_time >= last_30_days_date
    ).all()
    
    total_products = {} 
    total_liters_30d = 0
    category_stats = {'sodas': 0, 'bidones_10': 0, 'bidones_20': 0}

    for o in orders_30d:
        if o.product:
            p_name = o.product.name
            qty = o.total_produced or 0
            name_lower = p_name.lower()
            volume = 0
            
            if "soda" in name_lower or "sifon" in name_lower: 
                volume = 1
                category_stats['sodas'] += qty
            elif "bidon" in name_lower or "botellon" in name_lower:
                if "10" in name_lower:
                    volume = 10
                    category_stats['bidones_10'] += qty
                else:
                    volume = 20
                    category_stats['bidones_20'] += qty
            
            total_liters_30d += (qty * volume)

            if p_name not in total_products:
                total_products[p_name] = 0
            total_products[p_name] += qty

    return render_template('general_analytics.html', 
                           total_liters_30d=int(total_liters_30d), 
                           category_stats=category_stats)
