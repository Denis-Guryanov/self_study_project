from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, MaterialViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
