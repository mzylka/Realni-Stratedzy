import datetime
import unittest
from app import create_app, db
from app.models import User, Role, Game, Tag, Textfield, Link
from pathlib import Path


class AdminTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        Role.insert_roles()
        Textfield.insert_textfields()
        admin = User(email='admin@test.com', username='admin', password='123')
        test_user = User(email='testuser@example.com', username='testuser', password='1234')
        tag1 = Tag(name='tag1')
        db.session.add(admin)
        db.session.add(test_user)
        db.session.add(tag1)
        db.session.commit()
        Link.insert_links()
        self.client = self.app.test_client(use_cookies=True)
        self.resources = Path(__file__).parent / 'resources'

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    #  TEST auth/login
    def test_admin_login(self):
        #  log in
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Zalogowano jako admin' in resp.get_data(as_text=True))

    def test_login_fail(self):
        #  log in
        resp = self.client.post('/control-panel/auth/login', data={'username': "nonexist", 'password': '123'},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Nieprawidłowy username lub hasło' in resp.get_data(as_text=True))

    #  TEST auth/logout
    def test_admin_logout(self):
        #  log in
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Zalogowano jako admin' in resp.get_data(as_text=True))

        #  log out
        resp = self.client.get('/control-panel/auth/logout', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Realni' in resp.get_data(as_text=True))

    #  TEST auth/register
    def test_register_user(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'}, follow_redirects=True)

        #  register an user
        resp = self.client.post('/control-panel/auth/register', data={
            'email': 'testus@example.com',
            'username': 'user_test',
            'password': '1234',
            'password2': '1234'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Użytkownik został zarejestrowany.' in resp.get_data(as_text=True))

    def test_register_user_with_existing_mail(self):
        # log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'}, follow_redirects=True)

        #  register a user with existing email in the db
        resp = self.client.post('/control-panel/auth/register', data={
            'email': 'testuser@example.com',
            'username': 'usertest2',
            'password': '1234',
            'password2': '1234'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Email już istnieje' in resp.get_data(as_text=True))

    def test_register_user_with_existing_username(self):
        # log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'}, follow_redirects=True)

        #  register a user with existing username in the db
        resp = self.client.post('/control-panel/auth/register', data={
            'email': 'example22@ex.com',
            'username': 'testuser',
            'password': '1234',
            'password2': '1234'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Username już istnieje' in resp.get_data(as_text=True))

    # TEST auth/delete_user
    def test_delete_user(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  delete a user
        resp = self.client.get('/control-panel/auth/delete-user/2')
        self.assertEqual(resp.status_code, 302)

    # TEST auth/new_password
    def test_new_password_as_admin(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  set new password
        resp = self.client.post('/control-panel/auth/new-password/', data={
            'old_password': '123',
            'new_password': 'passw2',
            'new_password2': 'passw2'
        })
        self.assertEqual(resp.status_code, 302)

    def test_set_new_password_for_user(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  set new password for testuser
        resp = self.client.get('/control-panel/auth/set-new-password/2')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/auth/set-new-password/2', data={
            'new_password': 'passw3',
            'new_password2': 'passw3'
        })
        self.assertEqual(resp.status_code, 302)

    def test_set_new_password_but_old_for_user(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  set new password for testuser
        resp = self.client.get('/control-panel/auth/set-new-password/2')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/auth/set-new-password/2', data={
            'new_password': 'passw3',
            'new_password2': 'passw3'
        })
        self.assertEqual(resp.status_code, 302)

    def test_set_new_password_but_old(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  set new password for admin
        resp = self.client.post('/control-panel/auth/new-password/1', data={
            'old_password': '123',
            'new_password': '123',
            'new_password2': '123'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Nowe hasło nie może być takie same jak stare!' in resp.get_data(as_text=True))

    # TEST control_panel/users
    def test_users_list(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  get list of users
        resp = self.client.get('/control-panel/users', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Lista użytkowników' in resp.get_data(as_text=True))

    # TEST control_panel/user/<edit-profile>
    def test_edit_user_profile(self):
        # log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        # edit admin profile
        # test get method
        resp = self.client.get('/control-panel/edit-profile/1')
        self.assertTrue(resp.status_code, 200)
        self.assertTrue('admin' in resp.get_data(as_text=True))

        # test post method
        resp = self.client.post('/control-panel/edit-profile/1', data={'username': 'adminek', 'email': 'admin@test.com', 'role': 3}, follow_redirects=True)
        self.assertTrue(resp.status_code, 200)
        self.assertTrue('The profile has been updated.' in resp.get_data(as_text=True))

        #  edit testuser profile
        resp = self.client.post('/control-panel/edit-profile/2', data={'username': 'testuser2', 'email': 'ttt@gmail.com', 'role': 1}, follow_redirects=True)
        self.assertTrue(resp.status_code, 200)
        self.assertTrue('The profile has been updated.' in resp.get_data(as_text=True))

    # TEST control_panel/posts
    def test_posts_list_cp(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  see posts list
        resp = self.client.get('/control-panel/posts', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Lista postów' in resp.get_data(as_text=True))

    # TEST control_panel/add-post, show-post, edit-post, delete-post
    def test_post_actions(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  add post
        resp = self.client.get('/control-panel/add-post')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/add-post', data={
            'title': 'Test title',
            'thumb': (self.resources / 'picture.jpg').open('rb'),
            'short_desc': 'Short desc',
            'body': 'Testing the body of post!',
            'game': 0,
            'tags': 'tag1,tag2',  # Add one exisitng tag and one new
            'published': True},
            follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Post został dodany.' in resp.get_data(as_text=True))

        #  show post
        resp = self.client.get('/control-panel/show-post/1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Test title' in resp.get_data(as_text=True))

        #  edit post
        resp = self.client.get('/control-panel/edit-post/1')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/edit-post/1', data={
            'title': 'Test title edit',
            'thumb': (self.resources / 'picture.jpg').open('rb'),
            'short_desc': 'Short desc',
            'body': 'Testing the body of post!',
            'game': 0,
            'tags': 'tag1,tag2,tag3,tag4',
            'published': True},
            follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Post został zaktualizowany.' in resp.get_data(as_text=True))

        #  edit post's tags(remove)
        resp = self.client.get('/control-panel/edit-post/1')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/edit-post/1', data={
            'title': 'Test title edit',
            'thumb': (self.resources / 'picture.jpg').open('rb'),
            'short_desc': 'Short desc',
            'body': 'Testing the body of post!',
            'game': 0,
            'tags': 'tag1',
            'published': True},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Post został zaktualizowany.' in resp.get_data(as_text=True))

        #  delete post
        resp = self.client.get('control-panel/delete-post/1', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Post został usunięty.' in resp.get_data(as_text=True))

    #  TEST control_panel/games
    def test_games_list_cp(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  see games list
        resp = self.client.get('/control-panel/games', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Lista gier' in resp.get_data(as_text=True))

    #  TEST control_panel/add-game, show-game, edit-game, delete-game
    def test_game_actions(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  add game
        resp = self.client.get('/control-panel/add-game')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/add-game', data={
            'title': 'Test title game',
            'producer': 'Producer',
            'release_date': '2029-12-12',
            'thumb': (self.resources / 'picture.jpg').open('rb'),
            'body': 'Testing the body of game!',
            'published': True},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Gra została dodana.' in resp.get_data(as_text=True))

        #  show game
        resp = self.client.get('/control-panel/show-game/1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Test title game' in resp.get_data(as_text=True))

        #  edit game
        resp = self.client.get('/control-panel/edit-game/1')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/edit-game/1', data={
            'title': 'Test title game edited',
            'producer': 'Producer2',
            'release_date': '2025-12-12',
            'body': 'Testing the body of game edited!',
            'published': True},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Gra została zaktualizowana' in resp.get_data(as_text=True))

        #  delete game
        resp = self.client.get('control-panel/delete-game/1', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Gra została usunięta.' in resp.get_data(as_text=True))

    # TEST control_panel/tags
    def test_tags_list(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  see tags list
        resp = self.client.get('/control-panel/tags', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Lista tagów' in resp.get_data(as_text=True))

    #  TEST control_panel/add-tag, edit-tag, delete-tag
    def test_tag_actions(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': "123"},
                                follow_redirects=True)

        #  add tag
        resp = self.client.get('/control-panel/add-tag')
        self.assertEqual(resp.status_code, 308)

        resp = self.client.post('/control-panel/add-tag', data={'name': 'tag3'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('tag1' in resp.get_data(as_text=True))

        #  edit tag
        resp = self.client.get('/control-panel/edit-tag/1')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/edit-tag/1', data={'name': 'tag2'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('tag2' in resp.get_data(as_text=True))

        #  delete tag
        resp = self.client.get('/control-panel/delete-tag/1', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Tag został usunięty' in resp.get_data(as_text=True))

    #  TEST control_panel/communities
    def test_communities_list(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)
        #  see communities list
        resp = self.client.get('/control-panel/communities', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Lista społeczności' in resp.get_data(as_text=True))

    #  TEST control_panel/add-community, show-community, edit-community, delete-community
    def test_community_actions(self):
        # add the needed game for tests
        game = Game(title='Game_1', producer='testowy', release_date=datetime.datetime(2023,6,8), body="test", published=True)
        db.session.add(game)
        db.session.commit()

        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)
        #  add community
        resp = self.client.get('/control-panel/add-community')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/add-community', data={
            'name': 'Test name community',
            'thumb': (self.resources / 'picture.jpg').open('rb'),
            'body': 'Testing the body of community!',
            'game': "1",
            'published': True},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Społeczność została dodana.' in resp.get_data(as_text=True))

        #  show community
        resp = self.client.get('/control-panel/show-community/1')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Test name community' in resp.get_data(as_text=True))

        #  edit community
        resp = self.client.get('/control-panel/edit-community/1')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/control-panel/edit-community/1', data={
            'name': 'Test title game edited',
            'body': 'Testing the body of game edited!',
            'game': "1",
            'published': True},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Społeczność została zaktualizowana.' in resp.get_data(as_text=True))

        #  delete community
        resp = self.client.get('control-panel/delete-community/1', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Społeczność została usunięta' in resp.get_data(as_text=True))

    def test_edit_pages_content(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        #  attempt to edit the wrong textfield
        resp = self.client.get('/control-panel/edit-page/wrong')
        self.assertEqual(resp.status_code, 404)

        #  edit about us page
        resp = self.client.get('/control-panel/edit-page/about_us_page')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('/control-panel/edit-page/about_us_page', data={'body': 'O nas test'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        resp_text = resp.get_data(as_text=True)
        self.assertTrue('&#34;about_us_page&#34; zostało zaktualizowane.' in resp_text)
        self.assertTrue('O nas test' in resp_text)

        #  edit contact page
        resp = self.client.get('/control-panel/edit-page/contact_page')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('/control-panel/edit-page/contact_page', data={'body': 'Kontakt test'},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        resp_text = resp.get_data(as_text=True)
        self.assertTrue('&#34;contact_page&#34; zostało zaktualizowane.' in resp_text)
        self.assertTrue('Kontakt test' in resp_text)

        #  edit privacy policy page
        resp = self.client.get('/control-panel/edit-page/privacy_policy_page')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('/control-panel/edit-page/privacy_policy_page', data={'body': 'Polityka prywatności test'},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        resp_text = resp.get_data(as_text=True)
        self.assertTrue('&#34;privacy_policy_page&#34; zostało zaktualizowane.' in resp_text)
        self.assertTrue('Polityka prywatności test' in resp_text)

    def test_edit_textfield(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)
        #  attempt to edit the wrong textfield
        resp = self.client.get('/control-panel/edit-textfield/wrong')
        self.assertEqual(resp.status_code, 404)

        #  edit communities_page textfield
        resp = self.client.get('/control-panel/edit-textfield/communities_page')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('/control-panel/edit-textfield/communities_page', data={'body': 'Communities_page test'},
                                follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        resp_text = resp.get_data(as_text=True)
        self.assertTrue('Pole communities_page zostało zaktualizowane.' in resp_text)
        self.assertTrue('Communities_page test' in resp_text)

    def test_edit_links_page(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)
        resp = self.client.get('/control-panel/edit-links/')
        self.assertEqual(resp.status_code, 200)
        resp_text = resp.get_data(as_text=True)
        self.assertTrue('Discord' in resp_text)

    def test_edit_links(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)
        resp = self.client.post('/control-panel/edit-links/', data={'discord_link': 'disc_link', 'fb_link': 'testfb_link',
                                'twitter_link': 'testx_link', 'yt_link': 'testyt_link', 'twitch_link': 'testtw_link'})
        self.assertEqual(resp.status_code, 200)
        resp_text = resp.get_data(as_text=True)
        self.assertTrue('disc_link' in resp_text)
        self.assertTrue('testfb_link' in resp_text)
        self.assertTrue('testx_link' in resp_text)
        self.assertTrue('testyt_link' in resp_text)
        self.assertTrue('testtw_link' in resp_text)


    def test_gallery(self):
        #  log in as admin
        resp = self.client.post('/control-panel/auth/login', data={'username': 'admin', 'password': '123'},
                                follow_redirects=True)

        resp = self.client.get('/control-panel/gallery/thumbnails')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/control-panel/gallery/logos')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/control-panel/gallery/cke_images')
        self.assertEqual(resp.status_code, 200)
