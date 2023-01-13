from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..utils import NUMBER_OF_POSTS
from ..models import Post, Group

TEST_OF_POST: int = NUMBER_OF_POSTS
User = get_user_model()


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        bulk_post: list = []
        for i in range(TEST_OF_POST):
            bulk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(bulk_post)

    def test_correct_context_guest_and_authorized_client(self):
        '''Checkout number of posts in first and second pages.'''
        pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_list',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            # checkout by guest client
            response_guest_1 = self.guest_client.get(page)
            response_guest_2 = self.guest_client.get(page + '?page=2')
            count_posts_guest_1 = len(response_guest_1.context['page_obj'])
            count_posts_guest_2 = len(response_guest_2.context['page_obj'])
            error_name_1 = (f'Guest client error! {count_posts_guest_1} ',
                            f'of posts, should be {NUMBER_OF_POSTS}')
            error_name_2 = (f'Guest client error! {count_posts_guest_2} ',
                            f'of posts, should be {NUMBER_OF_POSTS}')
            self.assertEqual(count_posts_guest_1,
                             NUMBER_OF_POSTS,
                             error_name_1)
            self.assertEqual(count_posts_guest_2,
                             NUMBER_OF_POSTS,
                             error_name_2)
            # checkout by authorized client
            response_auth_1 = self.authorized_client.get(page)
            response_auth_2 = self.authorized_client.get(page + '?page=2')
            count_posts_auth_1 = len(response_auth_1.context['page_obj'])
            count_posts_auth_2 = len(response_auth_2.context['page_obj'])
            error_name_3 = (f'Authorized client error! {count_posts_auth_1} ',
                            f'posts, should be {NUMBER_OF_POSTS}')
            error_name_4 = (f'Authorized client error! {count_posts_auth_2} ',
                            f'posts, should be {NUMBER_OF_POSTS}')
            self.assertEqual(count_posts_auth_1,
                             NUMBER_OF_POSTS,
                             error_name_3)
            self.assertEqual(count_posts_auth_2,
                             TEST_OF_POST,
                             error_name_4)
