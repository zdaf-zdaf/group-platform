from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ValidationError
from user.models import User
from user.permissions import IsStudent, IsTeacher
from user.serializers import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer
)


# Create your views here.
class RegisterView(generics.CreateAPIView):
    authentication_classes = []  # 禁用所有认证
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "success": True,
                "message": "用户注册成功"
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                "success": False,
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            response.data.update({
                "success": True,
                "message": "登录成功",
                "role": response.data.get('role', '')  # 添加角色信息
            })
            return response
        except ValidationError as e:
            return Response({
                "success": False,
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

class TeacherTestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request):
        return Response({"message": "教师专属接口"})


class StudentTestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get(self, request):
        return Response({"message": "学生专属接口"})
    
class UserProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request):
        user = request.user
        # 只允许更新学工号和学院
        student_id = request.data.get('student_id', '').strip()
        faculty = request.data.get('faculty', '').strip()
        
        # 验证并更新数据
        if student_id:
            user.student_id = student_id
        if faculty:
            user.faculty = faculty
        
        try:
            user.save()
            return Response({
                "success": True,
                "message": "个人信息更新成功",
                "data": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=400)

class StudentListView(generics.ListAPIView):
        queryset = User.objects.filter(role='student') # 只筛选学生角色的用户
        serializer_class = UserSerializer
        permission_classes = [permissions.IsAuthenticated, IsTeacher]# 假设只有教师可以查看学生列表