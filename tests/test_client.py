import unittest
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        Role.insert_roles()
        admin = User(email="admin@test.com", username="admin", password="123")
        test_user = User(email="testuser@example.com", username="testuser", password="1234")
        db.session.add(admin)
        db.session.add(test_user)
        db.session.commit()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Artykuł' in resp.get_data(as_text=True))

    def test_control_panel_redirect(self):
        resp = self.client.get('/control-panel/')
        self.assertEquals(resp.status_code, 302)
        self.assertTrue('/control-panel/auth/login' in resp.get_data(as_text=True))

    def test_login_page(self):
        resp = self.client.get('/control-panel/auth/login')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Log in' in resp.get_data(as_text=True))
