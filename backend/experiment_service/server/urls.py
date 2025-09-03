from django.urls import path, include
from experiments import urls as experiment_urls

urlpatterns = [
    path('api/', include(experiment_urls)),
]