from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExperimentViewSet

router = DefaultRouter()
router.register(r'experiments', ExperimentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
