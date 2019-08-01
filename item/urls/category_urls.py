from rest_framework.routers import DefaultRouter
from item import views
from django.urls import path, include

router = DefaultRouter()
router.register('', views.CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]