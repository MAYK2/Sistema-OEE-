import unittest
from app import create_app, db
from app.models.user import User

class RoleAccessTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for easier testing
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Ensure users exist (Assuming database is already seeded/migrated)
        self.admin = User.query.filter_by(username='admin').first()
        self.operator = User.query.filter_by(username='operario1').first()

        if not self.admin:
            self.admin = User(username='admin', role='admin')
            self.admin.set_password('admin')
            db.session.add(self.admin)
        else:
            # Force update for test reliability
            self.admin.role = 'admin'
            self.admin.set_password('admin')
        
        if not self.operator:
            # Create if not exists
            self.operator = User(username='operario1', role='operator')
            self.operator.set_password('operario1')
            db.session.add(self.operator)
        else:
            # Enforce operator role if it was changed
            if self.operator.role != 'operator':
                self.operator.role = 'operator'

        db.session.commit()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_admin_access(self):
        """Admin should access dashboard and config"""
        self.login('admin', 'admin') # Assuming pass is admin
        
        # Dashboard
        resp = self.client.get('/dashboard')
        self.assertEqual(resp.status_code, 200, "Admin should access dashboard")
        self.assertIn(b'Dashboard', resp.data)

        # Config
        resp = self.client.get('/config/lines')
        self.assertEqual(resp.status_code, 200, "Admin should access config")

    def test_operator_access_restrictions(self):
        """Operator should NOT access dashboard or config"""
        # Reset password to known value if check fails (optional, assuming 'operario1' is the pass)
        # But we can't easily reset it without knowing it or force setting it.
        # Let's assume the user created it with 'operario1'. If not, we might fail login.
        # Force set password for test reliability
        self.operator.set_password('operario1')
        db.session.commit()
        
        self.login('operario1', 'operario1')
        
        # Dashboard -> Should redirect to index or 403
        resp = self.client.get('/dashboard', follow_redirects=True)
        # Our implementation redirects to index with a flash message
        self.assertIn(b'Acceso denegado', resp.data)
        # self.assertIn(b'Iniciando Produccion', resp.data) # Wrong content guess

        # Config -> Should redirect
        resp = self.client.get('/config/lines', follow_redirects=True)
        self.assertIn(b'Acceso denegado', resp.data)

    def test_operator_allowed_routes(self):
        """Operator SHOULD access index and tutorial"""
        self.login('operario1', 'operario1')
        
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        
        resp = self.client.get('/tutorial')
        self.assertEqual(resp.status_code, 200)

    def tearDown(self):
        db.session.remove()
        self.ctx.pop()

if __name__ == '__main__':
    unittest.main()
