from rest_framework import serializers

from .models import Course, Material, Comment


class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'material', 'user', 'user_username', 'content', 'parent', 'replies', 'is_approved', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class MaterialSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Material
        fields = ['id', 'course', 'title', 'content', 'owner', 'owner_username', 'comments']
        read_only_fields = ['id']


class CourseSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'owner', 'owner_username', 'materials', 'tags', 'difficulty']
        read_only_fields = ['id', 'owner']
