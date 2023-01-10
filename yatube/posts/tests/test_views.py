import shutil
import tempfile
from django.test import TestCase, Client
from django.conf import settings
from posts.models import Post, Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


EXPECT_QENTITY_POSTS_PAGE_1 = 10
EXPECT_QENTITY_POSTS_PAGE_2 = 2

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostsViews(TestCase):

    def add_entities_to_db(self):
        test_user1 = User.objects.create_user(username='TestUser1')
        test_user2 = User.objects.create_user(username='TestUser2')

        group1 = Group.objects.create(
            title='Тестовый заголовок группы1',
            slug='test_slug_group1',
            description='Тестовое описание группы1'
        )

        group2 = Group.objects.create(
            title='Тестовый заголовок группы2',
            slug='test_slug_group2',
            description='Тестовое описание группы2'
        )
        for i in range(0,25):
            if i < 5:
                Post.objects.create(
                    text=f'Тестовый текст{i}',
                    author=test_user1,
                    group=group1
                )
            else:
                Post.objects.create(
                    text=f'Тестовый текст{i}',
                    author=test_user2,
                    group=group2
                )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        """ Тестовая запись в БД. """
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test_slug_group',
            description='Тестовое описание группы'
        )
        small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.test_user,
            group=cls.group,
            image=uploaded
        )

    def setUp(self):
        # Неавторизованный клиент
        self.guest_client = Client()
        # Авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(TestPostsViews.test_user)

    def test_context_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={'slug': TestPostsViews.post.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': TestPostsViews.test_user}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': TestPostsViews.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': TestPostsViews.post.pk}): 'posts/create_post.html',
        }
        for namspace_name, template in templates_page_names.items():
            with self.subTest(namspace_name=namspace_name):
                response = self.authorized_client.get(namspace_name)
                self.assertTemplateUsed(response, template)

    def test_context_index(self):
        """ Считаем количество постов на странице. """
        self.add_entities_to_db()
        response = self.authorized_client.get(reverse('posts:index'))
        page_object = response.context['page_obj']
        self.assertEqual(len(page_object), EXPECT_QENTITY_POSTS_PAGE_1)

    def test_context_group_list(self):
        """ Сравниваем текст постов для определенной группы. """
        self.add_entities_to_db()
        response = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': 'test_slug_group1'}))
        result_set = set()
        for i in response.context['page_obj']:
            result_set.add(i.text)
        expect_set = {
            'Тестовый текст0',
            'Тестовый текст1',
            'Тестовый текст2',
            'Тестовый текст3',
            'Тестовый текст4'
        }
        self.assertEqual(result_set, expect_set)
    def test_context_profile(self):
        self.add_entities_to_db()
        response = self.authorized_client.get(reverse('posts:profile', kwargs={'username': 'TestUser1'}))
        result_set = set()
        for i in response.context['page_obj']:
            result_set.add(i.text)
        expect_set = {
            'Тестовый текст0',
            'Тестовый текст1',
            'Тестовый текст2',
            'Тестовый текст3',
            'Тестовый текст4'
        }
        self.assertEqual(result_set, expect_set)

    def test_context_post_detail(self):
        response = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': TestPostsViews.post.pk}))
        post_object = response.context['post']
        self.assertEqual(post_object, TestPostsViews.post)

    def test_context_post_create(self):
        """Шаблон сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_post_edit(self):
        """Шаблон сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit', kwargs={'post_id': TestPostsViews.post.pk}))
        self.assertIn('form', response.context)
        self.assertTrue(response.context['is_edit'])
        self.assertEqual(response.context['post_id'], TestPostsViews.post.pk)
        self.assertEqual(response.context.get('form').instance, TestPostsViews.post)

    def test_context_additional_check(self):
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': TestPostsViews.post.group.slug}),
            reverse('posts:profile', kwargs={'username': TestPostsViews.test_user})
        ]
        post = TestPostsViews.post
        for rev in reverse_list:
            with self.subTest(rev=rev):
                response = self.authorized_client.get(rev)
                page_object = response.context['page_obj']
                self.assertEqual(page_object[0], post)
                # self.assertContains(response, 'Тестовый текст поста')

    def test_img_in_context_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTrue(response.context['page_obj'][0].image)
        # self.assertTrue(
        #     Post.objects.filter(
        #         group=TestPostsViews.group,
        #         text='Тестовый текст поста',
        #         image='posts/small.gif'
        #     ).exists()
        # ) 

    def test_img_in_context_profile(self):
        response = self.authorized_client.get(reverse('posts:profile', kwargs={'username': TestPostsViews.test_user}))
        self.assertTrue(response.context['page_obj'][0].image)

    def test_img_in_context_grouplist(self):
        response = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': TestPostsViews.post.group.slug}))
        self.assertTrue(response.context['page_obj'][0].image)

    def test_img_in_context_detail(self):
        response = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': TestPostsViews.post.pk}))
        self.assertTrue(response.context['post'].image) 


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovyj_slug',
            description='Тестовое описание',
        )

        for i in range(12):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.page_name = {
            reverse('posts:index'): 'page_obj',
            reverse('posts:group_list', kwargs={'slug': 'testovyj_slug'}): 'page_obj',
            reverse('posts:profile', kwargs={'username': 'TestUser'}): 'page_obj'
        }

    def test_first_page_contains_ten_records(self):
        for value, expected in self.page_name.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(len(response.context[expected]), EXPECT_QENTITY_POSTS_PAGE_1)

    def test_second_page_contains_three_records(self):
        for value, expected in self.page_name.items():
            with self.subTest(value=value):
                response = self.client.get(value + '?page=2')
                self.assertEqual(len(response.context[expected]), EXPECT_QENTITY_POSTS_PAGE_2)
                