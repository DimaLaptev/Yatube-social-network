from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.urls import reverse
from django import forms
from ..models import Post, Group
from ..utils import NUMBER_OF_POSTS
from django.conf import settings
from django.core.cache import cache

User = get_user_model()
TEST_OF_POST: int = NUMBER_OF_POSTS
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Сообщество',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
    def test_views_correct_template(self):
        """Checkout views uses the correct template."""
        templates_pages_names = {
            reverse('posts:index'):
            'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': f'{self.group.slug}'}
            ):
            'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}
            ):
            'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
            ):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}
            ):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                error_name: str = (f'Error! {reverse_name} '
                                   f'expected template {template}')
                self.assertTemplateUsed(response, template, error_name)

    def test_post_detail_show_correct_context(self):
        """post_detail formed with correct context-dict."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        post_text = {
            response.context['post'].text: 'Тестовый пост',
            response.context['post'].group: self.group,
            response.context['post'].author: self.user.username
        }
        for value, expected in post_text.items():
            self.assertEqual(post_text[value], expected)

    def test_post_create_show_correct_context(self):
        """post_create formed with correct context-dict."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_correct_add(self):
        """Checkout post added correct in main-, group- and profile-page."""
        test_post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        response_index = self.authorized_client.get(
            reverse('posts:index'),
        )
        response_group = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug':
                    f'{self.group.slug}'})
        )
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username':
                    f'{self.user.username}'})
        )
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(test_post, index, 'Post not found in main page!')
        self.assertIn(test_post, group, 'Post not found in profile!')
        self.assertIn(test_post, profile, 'Post not found in group!')

    def test_cache_context(self):
        '''Checkout cache of index-page.'''
        before_create_post = self.authorized_client.get(
            reverse('posts:index'))
        before_first_item = before_create_post.content
        Post.objects.create(
            author=self.user,
            text='Тестировани кэша',
            group=self.group)
        after_create_post = self.authorized_client.get(reverse('posts:index'))
        after_first_item = after_create_post.content
        self.assertEqual(after_first_item, before_first_item)
        cache.clear()
        after_clear_cache = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(after_first_item, after_clear_cache)
