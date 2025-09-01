from rest_framework import serializers
from .models import Notice
from .services import NoticeService  # 使用服务层而非直接调用客户端

class NoticeSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    experiment_info = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    read_count = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content', 'type', 'date', 'is_top',
            'author_name', 'formatted_date', 'experiment_info',
            'is_read', 'read_count'
        ]
        read_only_fields = ['date', 'read_count', 'is_read']

    def get_author_name(self, obj):
        """通过服务层获取作者名称"""
        return NoticeService.get_author_name(obj.author_id, self.context.get('request'))
    
    def get_formatted_date(self, obj):
        """格式化日期时间"""
        return obj.date.strftime('%Y-%m-%d %H:%M') if obj.date else None

    def get_experiment_info(self, obj):
        """通过服务层获取实验信息"""
        return NoticeService.get_experiment_info(obj.experiment_id, self.context.get('request'))

    def get_is_read(self, obj):
        """检查当前用户是否已读此公告"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_read_by(request.user.id)
        return False

    def get_read_count(self, obj):
        """获取已读用户数量"""
        return len(obj.reader_ids)