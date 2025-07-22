import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        TEACHER = 'teacher', 'Преподаватель'
        STUDENT = 'student', 'Студент'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    email_confirmed = models.BooleanField(default=False)
    email_confirmation_token = models.UUIDField(default=uuid.uuid4, unique=True)

    class Meta:
        ordering = ['id']
