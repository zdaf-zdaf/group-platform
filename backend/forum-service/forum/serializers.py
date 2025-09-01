from rest_framework import serializers
from .models import Question, Comment
# 移除对UserSerializer的依赖

class CommentSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author_id', 'author_info', 'created_at']
        read_only_fields = ['created_at']

    def get_author_info(self, obj):
        # 这里需要调用用户微服务API获取用户信息
        # 暂时返回模拟数据
        return {
            "id": obj.author_id,
            "username": f"user{obj.author_id}",
            "avatar": "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
        }

class QuestionSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'author_id', 'author_info', 'created_at', 
                 'updated_at', 'is_sticky', 'comments', 'liked', 'likes_count']
        read_only_fields = ['created_at', 'updated_at']

    def get_author_info(self, obj):
        # 这里需要调用用户微服务API获取用户信息
        # 暂时返回模拟数据
        return {
            "id": obj.author_id,
            "username": f"user{obj.author_id}",
            "avatar": "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
        }

    def get_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user_id'):  # 假设请求中有user_id
            return request.user_id in obj.likes
        return False

    def get_likes_count(self, obj):
        return len(obj.likes)