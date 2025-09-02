from rest_framework import serializers
from .models import Notice

class NoticeSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    experiment_info = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    read_count = serializers.SerializerMethodField()
    
    # 添加 author_id 字段并设置为只读
    author_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content', 'type', 'date', 'is_top',
            'author_name', 'formatted_date', 'experiment_info',
            'is_read', 'read_count', 'author_id'
        ]
        read_only_fields = ['date', 'read_count', 'is_read', 'author_id']  # 添加 author_id 到只读字段

    def get_author_name(self, obj):
        # 实际实现中通过调用用户服务API获取
        return f"用户-{obj.author_id}"

    def get_formatted_date(self, obj):
        return obj.date.strftime('%Y-%m-%d %H:%M') if obj.date else None

    def get_experiment_info(self, obj):
        if obj.experiment_id:
            # 实际实现中通过调用实验服务API获取
            return {'id': obj.experiment_id, 'name': f"实验-{obj.experiment_id}"}
        return None

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'id'):
            return obj.is_read_by(request.user.id)
        return False

    def get_read_count(self, obj):
        return len(obj.readers)

    def create(self, validated_data):
        """创建公告时自动设置作者ID"""
        # 从请求上下文中获取用户
        user = self.context['request'].user
        
        # 确保用户对象存在
        if not hasattr(user, 'id'):
            raise serializers.ValidationError("无法获取用户信息")
        
        # 自动设置作者ID
        validated_data['author_id'] = user.id
        
        # 调用父类方法创建对象
        return super().create(validated_data)