from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnswerViewSet,
    QuestionViewSet,
    TestCheckAPIView,
    TestResultViewSet,
    TestViewSet,
)

router = DefaultRouter()
router.register(r'tests', TestViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'test-results', TestResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('tests/<int:pk>/check/', TestCheckAPIView.as_view(), name='test-check'),
]
