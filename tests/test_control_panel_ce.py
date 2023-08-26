import unittest
from app import create_app, db
from app.models import User, Role, Post


class CETestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        Role.insert_roles()
        admin = User(email='admin@test.com', username='admin', password='123')
        test_user = User(email='testuser@example.com', username='testuser', password='1234')
        post = Post(title='Test title', thumb_name='picture.jpg', short_desc='Short desc', author=admin)
        db.session.add(admin)
        db.session.add(test_user)
        db.session.commit()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_content_editor_login(self):
        #  log in as content editor user
        resp = self.client.post('/control-panel/auth/login', data={"username": "testuser", "password": "1234"},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Zalogowano jako testuser' in resp.get_data(as_text=True))

    def test_new_password_as_ce(self):
        #  log in as content editor user
        resp = self.client.post('/control-panel/auth/login', data={"username": "testuser", "password": "1234"},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Zalogowano jako testuser' in resp.get_data(as_text=True))

        #  set new password
        resp = self.client.post('/control-panel/auth/new-password/', data={
            'old_password': '1234',
            'new_password': 'passw3',
            'new_password2': 'passw3'
        })
        self.assertEqual(resp.status_code, 302)

    def test_new_password_page_unautho(self):
        #  log in as content editor user
        resp = self.client.post('/control-panel/auth/login', data={"username": "testuser", "password": "1234"},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Zalogowano jako testuser' in resp.get_data(as_text=True))

        #  Attempt to change password for admin
        resp = self.client.get('/control-panel/auth/new-password/1')
        self.assertEqual(resp.status_code, 403)

    def test_edit_post_unautho(self):
        # log in as content editor user
        resp = self.client.post('/control-panel/auth/login', data={"username": "testuser", "password": "1234"},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Zalogowano jako testuser' in resp.get_data(as_text=True))

        #  Attempt to edit post as unauthorized user
        resp = self.client.get('/control-panel/edit-post/1')
        self.assertEqual(resp.status_code, 403)
