from django.db import models

from users.models import User

# Create your models here.


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title


class Material(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='materials'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title
