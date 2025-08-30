from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}  # 确保密码不会在响应中返回
        }

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')
        extra_kwargs = {
            'role': {'required': True}
        }

    def validate(self, attrs):
        # 密码强度验证
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        
        # 角色合法性验证
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if attrs['role'] not in valid_roles:
            raise serializers.ValidationError({
                "role": f"无效的角色选择，可选值: {', '.join(valid_roles)}"
            })
        
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        token['student_id'] = user.student_id
        token['faculty'] = user.faculty
        return token
    
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            data.update({
                'email': self.user.email,
                'student_id': self.user.student_id,
                'faculty': self.user.faculty,
                'role': self.user.role,
                'username': self.user.username
            })
            return data
        except Exception as e:
            raise serializers.ValidationError({
                "detail": "用户名或密码错误，请重新输入"
            })