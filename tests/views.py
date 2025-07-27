from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdminOrTeacher, IsStudent, IsOwnerOrAdmin

from .models import Answer, Question, Test, TestResult
from .serializers import (
    AnswerSerializer,
    QuestionSerializer,
    TestResultSerializer,
    TestSerializer,
)
from .services import check_test_answers

# Create your views here.


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    search_fields = ['title']
    ordering_fields = ['title', 'id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    search_fields = ['text']
    ordering_fields = ['id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    search_fields = ['text']
    ordering_fields = ['id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]


class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    ordering_fields = ['score', 'submitted_at', 'id']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [IsAdminOrTeacher()]


class TestCheckAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def post(self, request, pk):
        test = Test.objects.get(pk=pk)
        answers_data = request.data.get('answers', {})
        result = check_test_answers(test, request.user, answers_data)
        return Response(
            {'score': result.score, 'test_result_id': result.id},
            status=status.HTTP_200_OK,
        )
