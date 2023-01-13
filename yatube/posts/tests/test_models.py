from django.contrib.auth import get_user_model
from django.test import TestCase
from ..forms import PostForm
from ..models import Group, Post, TEXT_LEN


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
        cls.form = PostForm()

    def test_models_have_correct_object_names(self):
        """Checkout models correct __str__."""
        mapping = {
            self.post.text[:TEXT_LEN]: str(self.post),
            self.group.title: str(self.group),
        }
        for field, expected_value in mapping.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)

    def test_label(self):
        text_label = PostModelTests.form.fields['text'].label
        group_label = PostModelTests.form.fields['group'].label
        image_label = PostModelTests.form.fields['image'].label
        self.assertEqual(text_label, 'Текст поста')
        self.assertEqual(group_label, 'Сообщество')
        self.assertEqual(image_label, 'Изображение')

    def test_help_text(self):
        text_help_text = PostModelTests.form.fields['text'].help_text
        group_help_text = PostModelTests.form.fields['group'].help_text
        image_help_text = PostModelTests.form.fields['image'].help_text
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
