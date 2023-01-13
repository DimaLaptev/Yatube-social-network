from django import forms

from .models import Post, Comment, Follow


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст поста',
                  'group': 'Сообщество',
                  'image': 'Изображение',
        }
        help_texts = {
            'text':
            'Текст нового поста',
            'group':
            'Сообщество, в котором будет опубликован пост',
            'image':
            'Загрузите изображение',
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Комментарий',
        }
        help_texts = {
            'text': 'Оставьте комментарий',
        }


class VollowForm(forms.ModelForm):

    class Meta:
        model = Follow
        fields = ('user', 'author',)
        labels = {
            'user': 'vollower',
            'author': 'vollowing',
        }
