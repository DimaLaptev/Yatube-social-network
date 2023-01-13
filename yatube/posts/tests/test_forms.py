from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, Comment, Follow
import shutil
import tempfile
from http import HTTPStatus

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        '''Checkout create of post.'''
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(name='small.gif',
                                      content=small_gif,
                                      content_type='image/gif')
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id,
                     'image': uploaded}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.last()
        error_name_1 = 'Error! Text of post does not match.'
        self.assertEqual(
            post.text,
            form_data['text'],
            error_name_1,
        )
        error_name_2 = 'Error! Group of post does not match.'
        self.assertEqual(
            post.group.id,
            form_data['group'],
            error_name_2,
        )
        error_name_3 = 'Error! Author of post does not match.'
        self.assertEqual(
            post.author,
            self.user,
            error_name_3,
        )
        error_name_4 = 'Error! Post has not been added to the database.'
        self.assertEqual(
            Post.objects.count(),
            1,
            error_name_4,
        )
        error_name_5 = 'Error! Image of post does not match.'
        self.assertEqual(
            post.image,
            f'posts/{uploaded}',
            error_name_5,
        )

    def test_edit_post(self):
        '''Checkout editing of post'''
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(name='small_2.gif',
                                      content=small_gif,
                                      content_type='image/gif')
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image='small_2.gif',
        )
        new_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Описание'
        )
        form_data = {'text': 'Текст записанный в форму',
                     'group': new_group.id,
                     'image': uploaded}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.get(id=post.id)
        error_name_1 = 'Error! Text of post does not match.'
        self.assertEqual(
            post.text,
            form_data['text'],
            error_name_1,
        )
        error_name_2 = 'Error! Group of post does not match.'
        self.assertEqual(
            post.group.id,
            form_data['group'],
            error_name_2,
        )
        error_name_3 = 'Error! Author of post does not match.'
        self.assertEqual(
            post.author,
            self.user,
            error_name_3,
        )
        error_name_4 = 'Error! Post has not been added to the database.'
        self.assertEqual(
            Post.objects.count(),
            1,
            error_name_4,
        )
        error_name_3 = 'Error! The test post remained in the old group!'
        self.assertEqual(
            Post.objects.filter(
                group=self.group.id
            )
            .count(),
            0,
            error_name_3
        )
        error_name_5 = 'Error! Image of post does not match.'
        self.assertEqual(
            post.image,
            f'posts/{uploaded}',
            error_name_5,
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post_id=cls.post.id,
            author=cls.user,
            text='Тестовый комментарий',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment(self):
        '''Checkout the creation of a comment'''
        form_data = {'post_id': self.post.id,
                     'text': 'Тестовый комментарий_2'}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data, follow=True)
        error_name_1 = 'Error! Data of comment does not match.'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Comment.objects.filter(
                        text='Тестовый комментарий_2',
                        post=self.post.id,
                        author=self.user
                        ).exists(), error_name_1)
        error_name_2 = 'Error! Post has not been added to the database.'
        self.assertEqual(Comment.objects.count(), 2, error_name_2)

    def test_comment_auth_user(self):
        '''Checkout the comment by a registered user'''
        comment_count = Comment.objects.count()
        print(comment_count)
        form_data = {'text': 'Тестовый комментарий_2'}
        response = self.guest_client.post(reverse('posts:add_comment',
                                          kwargs={'post_id': self.post.id}),
                                          data=form_data,
                                          follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name_2 = 'Post has been added to the database with error!'
        self.assertNotEqual(Comment.objects.count(),
                            comment_count + 1,
                            error_name_2)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_1')
        cls.user_2 = User.objects.create_user(username='auth_2')
        cls.author = User.objects.create_user(username='a_author')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_user_follower_authors(self):
        '''The user can subscribe to other users.
           Posts are available to the user who subscribed to the author.'''

        data_follow = {'user': FollowViewsTest.user,
                       'author': FollowViewsTest.author}
        redirect_url = reverse(
            'posts:profile',
            kwargs={'username': FollowViewsTest.author.username}
        )
        response = self.authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': FollowViewsTest.author.username}),
            data=data_follow, follow=True,
        )
        new_follow_num = Follow.objects.filter(
            user=FollowViewsTest.user).count()
        self.assertTrue(Follow.objects.filter(
                        user=FollowViewsTest.user,
                        author=FollowViewsTest.author).exists())
        self.assertRedirects(response, redirect_url)
        self.assertEqual(1, new_follow_num)

    def test_follower_see_new_post(self):
        '''New user post appears in the subscriber's feed.'''
        new_follower = Post.objects.create(
            author=FollowViewsTest.author,
            text='Тестовый текст',
        )
        Follow.objects.create(
            user=FollowViewsTest.user,
            author=FollowViewsTest.author,
        )
        response_follower = self.authorized_client.get(
            reverse('posts:follow_index'),
        )
        new_posts = response_follower.context['page_obj']
        self.assertIn(new_follower, new_posts)

    def test_unfollower_no_see_new_post(self):
        '''New user post does not appear in the non-subscriber's feed.'''
        new_follower = Post.objects.create(
            author=FollowViewsTest.author,
            text='Тестовый текст',
        )
        Follow.objects.create(user=FollowViewsTest.user,
                              author=FollowViewsTest.author)
        response_unfollower = self.authorized_client_2.get(
            reverse('posts:follow_index'),
        )
        new_post_unfollower = response_unfollower.context['page_obj']
        self.assertNotIn(new_follower, new_post_unfollower)
