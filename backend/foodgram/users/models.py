from django.contrib.auth.models import AbstractUser
from django.db import models

from users.utils import username_validator


class User(AbstractUser):

    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='электроннная почта',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        verbose_name='никнейм',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='фамилия',
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.username


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='following',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='follow_unique'
            )
        ]

    def __str__(self):
        return f'follower - {self.user} following - {self.author}'
