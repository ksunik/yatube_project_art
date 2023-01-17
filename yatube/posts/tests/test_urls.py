# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post
from django.core.cache import cache


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovyj_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # # Создаем пользователя
        # self.user = User.objects.create_user(username='TestUser')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        cache.clear()


    def test_url_exist_at_desired_location_main(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_url_exist_at_desired_location_group(self):
        response = self.guest_client.get(f'/group/{PostURLTests.post.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_url_exist_at_desired_location_profile(self):
        response = self.guest_client.get(f'/profile/{PostURLTests.post.author}/')
        self.assertEqual(response.status_code, 200)

    def test_url_exist_at_desired_location_postid(self):
        response = self.guest_client.get(f'/posts/{PostURLTests.post.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_url_unexist_at_desired_location(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_url_unexist_at_desired_location_postid(self):
        response = self.guest_client.get(f'/posts/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_url_unexist_at_desired_location_create(self):
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)


    def test_url_exists_at_desired_location_authorized(self):
        """Страница /task/test-slug/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_url_unexist_at_desired_location_postid_authorized(self):
        response = self.authorized_client.get(f'/posts/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_url_unexist_at_desired_location_postid_authorized_not_author(self):
        self.user = User.objects.create_user(username='TestUser2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(f'/posts/{PostURLTests.post.id}/edit/')
        self.assertRedirects(response, (f'/posts/{PostURLTests.post.id}/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/':'posts/index.html',
            f'/group/{PostURLTests.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.post.author}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template  in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)