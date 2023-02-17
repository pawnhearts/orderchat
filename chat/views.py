from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import TemplateView, DetailView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated

from chat.models import Order, Message, OrderStatuses, Chat


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = None

    @action(detail=True)
    def start_chat(self, request, pk=None):
        obj = self.get_object()
        if obj.status != OrderStatuses.PUBLISHED.value and (obj.status == OrderStatuses.STARTED.value and self.request.user not in (obj.user, obj.candidate)) and obj.user != self.request.user:
            raise PermissionDenied
        return HttpResponseRedirect(f'/chats/{obj.get_chat(self.request.user).pk}/')


class MessageViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    filterset_fields = ['chat']
    filter_backends = [DjangoFilterBackend]
    pagination_class = None

    def get_queryset(self):
        return Message.objects.filter(Q(chat__user=self.request.user) | Q(chat__order__user=self.request.user))

    @action(detail=True)
    def mark_read(self, request, pk=None):
        qs = self.filter_queryset(self.get_queryset())
        if pk:
            qs = qs.filter(pk=pk)
        return Response({'updated': qs.update(unread=False)})

    @action(detail=False)
    def mark_read_all(self, request):
        qs = self.filter_queryset(self.get_queryset())
        return Response({'updated': qs.update(unread=False)})


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        return {'orders': Order.objects.all(), 'chats': Chat.objects.filter(Q(candidate=self.request.user) | Q(order__user=self.request.user))}


class ChatView(LoginRequiredMixin, DetailView):
    template_name = 'chat.html'

    def get_queryset(self):
        return Chat.objects.filter(Q(candidate=self.request.user) | Q(order__user=self.request.user))
