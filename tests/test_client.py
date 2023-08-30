import unittest
from app import create_app, db
from app.models import User, Role, Game, Community, Textfield, Post, Tag


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        Role.insert_roles()

        admin = User(email='admin@test.com', username='admin', password='123')
        test_user = User(email='testuser@example.com', username='testuser', password='1234')
        game = Game(title='Gra1', producer='Producer1', thumb_name='picture.jpg', body='Game test body', published=True)
        communities_page_desc = Textfield(name='communities_page', body='Test description')
        community = Community(title='Community1', thumb_name='picture.jpg', body='Test community body', published=True, game=game)
        tag = Tag(name='tag1')
        post = Post(title='Post1', short_desc='post1 short', thumb_name='picture.jpg', body='Test post body', published=True, game=game)
        post.tags.append(tag)

        objs = [admin, test_user, game, community, communities_page_desc, post]

        db.session.add_all(objs)
        db.session.commit()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Realni' in resp.get_data(as_text=True))

    def test_games_page(self):
        resp = self.client.get('/gry/')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Gra1' in resp.get_data(as_text=True))

    def test_communities_page(self):
        resp = self.client.get('/spolecznosci/')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Community1' in resp.get_data(as_text=True))

    def test_contact_page(self):
        contact_page = Textfield(name='contact_page', body='Test contact body')
        db.session.add(contact_page)
        db.session.commit()
        resp = self.client.get('/kontakt/')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Test contact body' in resp.get_data(as_text=True))

    def test_contact_page_404(self):
        resp = self.client.get('/kontakt/')
        self.assertEquals(resp.status_code, 404)

    def test_about_us_page(self):
        about_us_page = Textfield(name='about_us_page', body='Test about-us body')
        db.session.add(about_us_page)
        db.session.commit()
        resp = self.client.get('/o-nas/')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Test about-us body' in resp.get_data(as_text=True))

    def test_about_us_page_404(self):
        resp = self.client.get('/o-nas/')
        self.assertEquals(resp.status_code, 404)

    def test_privacy_policy_page(self):
        privacy_policy_page = Textfield(name='privacy_policy_page', body='Test privacy-policy body')
        db.session.add(privacy_policy_page)
        db.session.commit()
        resp = self.client.get('/polityka-prywatnosci/')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Test privacy-policy body' in resp.get_data(as_text=True))

    def test_privacy_policy_404(self):
        resp = self.client.get('/polityka-prywatnosci/')
        self.assertEquals(resp.status_code, 404)

    def test_control_panel_redirect(self):
        resp = self.client.get('/control-panel/')
        self.assertEquals(resp.status_code, 302)
        self.assertTrue('/control-panel/auth/login' in resp.get_data(as_text=True))

    def test_login_page(self):
        resp = self.client.get('/control-panel/auth/login')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Log in' in resp.get_data(as_text=True))

    def test_searching_fail(self):
        resp = self.client.post('/szukaj', data={
            'searched': 'test post1 body'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertFalse('test post1 body' in resp.get_data(as_text=True))

    def test_searching(self):
        resp = self.client.get('/?search=body')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Post1' in resp.get_data(as_text=True))

    def test_posts_by_game(self):
        resp = self.client.get('/posty/gra1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Post1' in resp.get_data(as_text=True))

        resp = self.client.get('/posty/gra2')
        self.assertEqual(resp.status_code, 404)

    def test_posts_by_tag(self):
        resp = self.client.get('/tag/tag1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Post1' in resp.get_data(as_text=True))

        resp = self.client.get('/tag/tag2')
        self.assertEqual(resp.status_code, 404)

    def test_post_page(self):
        resp = self.client.get('/post/post1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Post1' in resp.get_data(as_text=True))

        resp = self.client.get('/post/unknown')
        self.assertEqual(resp.status_code, 404)

    def test_game_page(self):
        resp = self.client.get('/gra/gra1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Gra1' in resp.get_data(as_text=True))

        resp = self.client.get('/gra/unknown')
        self.assertEqual(resp.status_code, 404)

    def test_community_page(self):
        resp = self.client.get('/spolecznosc/community1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Community1' in resp.get_data(as_text=True))

        resp = self.client.get('/spolecznosc/unknown')
        self.assertEqual(resp.status_code, 404)

    def test_community_by_game(self):
        resp = self.client.get('/spolecznosci/gra1')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Community1' in resp.get_data(as_text=True))

    def test_filtering_games(self):
        resp = self.client.post('/gry/', data={'filtr': 0})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Gra1' in resp.get_data(as_text=True))

        resp = self.client.post('/gry/', data={'filtr': 1})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Gra1' in resp.get_data(as_text=True))

        resp = self.client.post('/gry/', data={'filtr': 2})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Gra1' in resp.get_data(as_text=True))

        resp = self.client.post('/gry/', data={'filtr': 3})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Gra1' in resp.get_data(as_text=True))

        resp = self.client.post('/gry/', data={'filtr': 4})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Gra1' in resp.get_data(as_text=True))

        resp = self.client.post('/gry/', data={'filtr': 5})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Gra1' in resp.get_data(as_text=True))

    def test_filtering_communities(self):
        resp = self.client.post('/spolecznosci/', data={'filtr': 0})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Community1' in resp.get_data(as_text=True))

        resp = self.client.post('/spolecznosci/', data={'filtr': 1})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Community1' in resp.get_data(as_text=True))

        resp = self.client.post('/spolecznosci/', data={'filtr': 2})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Community1' in resp.get_data(as_text=True))

        resp = self.client.post('/spolecznosci/', data={'filtr': 3})
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('Community1' in resp.get_data(as_text=True))
