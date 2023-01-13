from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel


User = get_user_model()

TEXT_LEN: int = 15


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
    )

    def __str__(self) -> str:
        return f'{self.text[:TEXT_LEN]}'

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'posts'


class Comment(models.Model):

    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'comment by {} on {}'.format(self.author, self.post)

    class Meta:
        ordering = ['-created']
        default_related_name = 'comments'


class Follow(models.Model):
    user = models.ForeignKey(User, related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='following',
                               on_delete=models.CASCADE)

    class Meta:
        ordering = ('-author',)
        verbose_name = 'Лента автора'
        verbose_name_plural = 'Лента авторов'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_members')]