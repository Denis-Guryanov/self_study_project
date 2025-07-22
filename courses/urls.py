from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, MaterialViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'materials', MaterialViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
