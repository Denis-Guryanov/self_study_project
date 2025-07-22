from rest_framework import serializers

from .models import Course, Material


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'course', 'title', 'content']
        read_only_fields = ['id']


class CourseSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'owner', 'materials']
        read_only_fields = ['id', 'owner']
