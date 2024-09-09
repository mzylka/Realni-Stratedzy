import unittest
from flask import current_app
from app import create_app, db
from pathlib import Path


class BasicsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.resources = Path(__file__).parent / 'resources'

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.app = None
        self.app_context = None
        self.client = None

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_home_page_redirect(self):
        response = self.client.get("/", follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.request.path, '/')

    def test_upload_cke(self):
        resp = self.client.post("/upload-cke", data={'upload': (self.resources / 'picture.jpg').open('rb')})
