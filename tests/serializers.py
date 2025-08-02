from rest_framework import serializers

from .models import Answer, Question, Test, TestResult


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'is_correct']
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'test', 'text', 'answers']
        read_only_fields = ['id']


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ['id', 'material', 'title', 'questions']
        read_only_fields = ['id']


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ['id', 'test', 'user', 'score', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']
