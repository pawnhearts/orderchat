from django.urls import path
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from chat.views import IndexView, ChatView, MessageViewSet, OrderViewSet
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='orders')
router.register('messages', MessageViewSet, basename='messages')


urlpatterns = [
    path('', IndexView.as_view()),
    path('chats/<int:pk>/', ChatView.as_view()),
    path('admin/', admin.site.urls),
] + router.urls + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
