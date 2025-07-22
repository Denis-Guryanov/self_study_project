import pytest
from django.db import models

from courses.models import Material
from users.models import User


class Test(models.Model):
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name='tests'
    )
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=1024)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers'
    )
    text = models.CharField(max_length=512)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.text


class TestResult(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='test_results'
    )
    score = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.user.username} - {self.test.title} ({self.score})"
