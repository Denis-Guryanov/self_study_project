from django.db import models

from users.models import User

# Create your models here.


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    tags = models.JSONField(default=list, blank=True, help_text='Теги для рекомендаций')
    difficulty = models.CharField(max_length=20, choices=[
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый')
    ], default='beginner')

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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='materials', null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title


class Comment(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.material.title}'


class UserActivity(models.Model):
    """Модель для отслеживания активности пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_activities')
    activity_type = models.CharField(max_length=50, choices=[
        ('view', 'Просмотр'),
        ('complete', 'Завершение'),
        ('test_passed', 'Тест пройден'),
        ('comment', 'Комментарий')
    ])
    score = models.FloatField(null=True, blank=True, help_text='Результат теста')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'course', 'activity_type', 'created_at']

    def __str__(self):
        return f'{self.user.username} - {self.activity_type} - {self.course.title}'


class Recommendation(models.Model):
    """Модель для хранения рекомендаций"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='recommendations')
    score = models.FloatField(help_text='Оценка релевантности курса для пользователя')
    reason = models.TextField(blank=True, help_text='Причина рекомендации')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']
        unique_together = ['user', 'course']

    def __str__(self):
        return f'Recommendation for {self.user.username}: {self.course.title} ({self.score})'
