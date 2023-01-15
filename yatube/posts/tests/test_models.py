from django.contrib.auth import get_user_model
from django.test import TestCase
from ..forms import PostForm, CommentForm
from ..models import Group, Post, Comment, TEXT_LEN


User = get_user_model()


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Это текст тестового поста',
        )
        cls.comment = Comment.objects.create(
            post_id=cls.post.id,
            author=cls.user,
            text='Тестовый комментарий',
        )
        cls.form_post = PostForm()
        cls.form_comment = CommentForm()

    def test_models_have_correct_object_names(self):
        """Checkout models correct __str__."""
        mapping = {
            self.post.text[:TEXT_LEN]:
            str(self.post),
            self.group.title:
            str(self.group),
            'comment by {} on {}'.format(self.user, self.post):
            str(self.comment),
        }
        for field, expected_value in mapping.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_label(self):
        text_label = PostModelTests.form_post.fields['text'].label
        group_label = PostModelTests.form_post.fields['group'].label
        image_label = PostModelTests.form_post.fields['image'].label
        comment_text_label = PostModelTests.form_comment.fields['text'].label
        self.assertEqual(text_label, 'Текст поста')
        self.assertEqual(group_label, 'Сообщество')
        self.assertEqual(image_label, 'Изображение')
        self.assertEqual(comment_text_label, 'Комментарий')

    def test_help_text(self):
        text_help_text = PostModelTests.form_post.fields['text'].help_text
        group_help_text = PostModelTests.form_post.fields['group'].help_text
        image_help_text = PostModelTests.form_post.fields['image'].help_text
        com_help_text = PostModelTests.form_comment.fields['text'].help_text
        self.assertEqual(
            text_help_text,
            'Текст нового поста',
        )
        self.assertEqual(
            group_help_text,
            'Сообщество, в котором будет опубликован пост',
        )
        self.assertEqual(
            image_help_text,
            'Загрузите изображение',
        )
        self.assertEqual(
            com_help_text,
            'Оставьте комментарий',
        )
