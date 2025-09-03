from django.urls import path
from . import views

urlpatterns = [
    path('questions/', views.QuestionListCreateView.as_view(), name='question-list'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<int:pk>/toggle-sticky/', views.ToggleStickyView.as_view(), name='toggle-sticky'),
    path('questions/<int:pk>/toggle-like/', views.ToggleLikeView.as_view(), name='toggle-like'),
    path('questions/<int:question_id>/comments/', views.CommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:pk>/', views.CommentDeleteView.as_view(), name='comment-delete'),
]