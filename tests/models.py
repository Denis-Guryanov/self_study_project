import pytest
from django.db import models

from courses.models import Material
from users.models import User

# Create your models here.


class Test(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='tests')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=[
        ('multiple_choice', 'Множественный выбор'),
        ('essay', 'Эссе'),
        ('code', 'Код')
    ], default='multiple_choice')
    max_score = models.IntegerField(default=1)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.text[:50]


class TestResult(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    score = models.FloatField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.user.username} - {self.test.title} - {self.score}'


class EssayQuestion(models.Model):
    """Модель для вопросов типа эссе"""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='essay_config')
    keywords = models.JSONField(default=list, help_text='Ключевые слова для автоматической оценки')
    min_length = models.IntegerField(default=50, help_text='Минимальная длина ответа')
    max_length = models.IntegerField(default=500, help_text='Максимальная длина ответа')
    ai_evaluation_enabled = models.BooleanField(default=True, help_text='Включить AI оценку')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'Essay config for {self.question.text[:30]}'


class CodeQuestion(models.Model):
    """Модель для вопросов с кодом"""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='code_config')
    language = models.CharField(max_length=20, choices=[
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('cpp', 'C++')
    ], default='python')
    test_cases = models.JSONField(default=list, help_text='Тестовые случаи для проверки кода')
    ai_evaluation_enabled = models.BooleanField(default=True, help_text='Включить AI оценку кода')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'Code config for {self.question.text[:30]}'


class EssayAnswer(models.Model):
    """Модель для ответов типа эссе"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='essay_answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='essay_answers')
    answer_text = models.TextField()
    ai_score = models.FloatField(null=True, blank=True, help_text='Оценка AI')
    human_score = models.FloatField(null=True, blank=True, help_text='Оценка преподавателя')
    final_score = models.FloatField(null=True, blank=True, help_text='Итоговая оценка')
    ai_feedback = models.TextField(blank=True, help_text='Комментарий AI')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'Essay answer by {self.user.username} for {self.question.text[:30]}'


class CodeAnswer(models.Model):
    """Модель для ответов с кодом"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='code_answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_answers')
    code_text = models.TextField()
    ai_score = models.FloatField(null=True, blank=True, help_text='Оценка AI')
    human_score = models.FloatField(null=True, blank=True, help_text='Оценка преподавателя')
    final_score = models.FloatField(null=True, blank=True, help_text='Итоговая оценка')
    ai_feedback = models.TextField(blank=True, help_text='Комментарий AI')
    test_results = models.JSONField(default=list, help_text='Результаты тестовых случаев')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'Code answer by {self.user.username} for {self.question.text[:30]}'
