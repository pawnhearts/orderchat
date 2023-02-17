from django.urls import path
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from chat.views import IndexView, ChatView, MessageViewSet, OrderViewSet
from django.contrib.auth.views import LoginView

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='orders')
router.register('messages', MessageViewSet, basename='messages')



urlpatterns = [
    path('', IndexView.as_view()),
    path('chats/<int:pk>/', ChatView.as_view()),
    path('accounts/login/', LoginView.as_view()),
    path('admin/', admin.site.urls),
] + router.urls
