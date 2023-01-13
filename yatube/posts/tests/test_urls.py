from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
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
        cls.group_url: str = f'/group/{cls.group.slug}/'
        cls.profile_url: str = f'/profile/{cls.user.username}/'
        cls.post_url: str = f'/posts/{cls.post.id}/'

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_url_not_authorized(self):
        pages: tuple = (
            '/',
            self.group_url,
            self.profile_url,
            self.post_url,
        )
        for page in pages:
            response = self.guest_client.get(page)
            error_name = f'Error! No access to {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_urls_redirect_guest_client(self):
        pages = {
            '/create/':
            '/auth/login/?next=/create/',
            f'{self.post_url}edit/':
            f'/auth/login/?next={self.post_url}edit/'
        }
        for page, value in pages.items():
            response = self.guest_client.get(page)
            self.assertRedirects(response, value)

    def test_urls_authorized_client(self):
        pages: tuple = ('/create/',
                        f'{self.post_url}edit/')
        for page in pages:
            response = self.authorized_client.get(page)
            error_name = f'Error! No access to {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            self.group_url: 'posts/group_list.html',
            self.profile_url: 'posts/profile.html',
            self.post_url: 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'{self.post_url}edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                error_name: str = (
                    f'Error! {address} '
                    f'expected template {template}'
                )
                self.assertTemplateUsed(response, template, error_name)

    def test_404(self):
        """Checout of request the 404-page"""
        response = self.guest_client.get('/test_404', follow=True)
        error_name = 'Error! Redirect on 404-page not working.'
        self.assertEquals(response.status_code,
                          HTTPStatus.NOT_FOUND,
                          error_name)
