from app import create_app, db
from app.models.line import Line
from app.models.product import Product
from app.models.client import Client

def seed_db():
    app = create_app()
    with app.app_context():
        print("🌱 Seeding Database...")
        
        # 1. Ensure Lines Exist
        lines_data = [
            {'id': 1, 'name': 'Linea 1 - Embotellado'},
            {'id': 2, 'name': 'Linea 2 - Sodas'}
        ]
        
        for l_data in lines_data:
            line = Line.query.get(l_data['id'])
            if not line:
                line = Line(id=l_data['id'], name=l_data['name'])
                db.session.add(line)
                print(f"   + Linea Created: {line.name}")
            else:
                line.name = l_data['name'] # Update name if changed
                print(f"   . Linea Exists: {line.name}")

        db.session.commit()

        # 2. Ensure Products Exist
        # Format: (ID, Name, LineID, CycleSeconds)
        products_data = [
            (1, 'Bidon 20L', 1, 45.0),
            (2, 'Bidon 10L', 1, 35.0),
            (3, 'Soda 500ml', 2, 10.0)
        ]

        for p_id, p_name, l_id, cycle in products_data:
            product = Product.query.get(p_id)
            if not product:
                product = Product(id=p_id, name=p_name, line_id=l_id, theoretical_cycle_seconds=cycle)
                db.session.add(product)
                print(f"   + Product Created: {product.name}")
            else:
                # Update attributes to ensure they match specs
                product.name = p_name
                product.line_id = l_id
                product.theoretical_cycle_seconds = cycle
                print(f"   . Product Updated/Exists: {product.name}")

        # 3. Ensure Default Client Exists (Optional but good for testing)
        client = Client.query.get(1)
        if not client:
             client = Client(id=1, name="Grammar", phone="555-0199")
             db.session.add(client)
             print(f"   + Client Created: Grammar")

        db.session.commit()
        print("✅ Database Seeded Successfully!")

if __name__ == '__main__':
    seed_db()
