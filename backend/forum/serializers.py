from rest_framework import serializers
from .models import Question, Comment
from user.serializers import UserSerializer
class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    # avatar = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at'] # 'avatar'
        read_only_fields = ['author', 'created_at']

    # def get_avatar(self, obj):
    #     return "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"

class QuestionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    # avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'is_sticky', 'comments', 'liked', 'likes_count'] # 'avatar'
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_likes_count(self, obj):
        return obj.likes.count()

    # def get_avatar(self, obj):
    #     return "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"