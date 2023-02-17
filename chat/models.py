from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


User = get_user_model()
channel_layer = get_channel_layer()


class OrderStatuses(models.IntegerChoices):
    DRAFT = 0
    PUBLISHED = 1
    STARTED = 2
    ON_HOLD = 3


class MessageTypes(models.IntegerChoices):
    MESSAGE = 0
    WARNING = 1
    STATUS = 2
    ENTER = 3
    LEAVE = 4
    TYPING = 5
    PING = 6


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=512)
    candidate = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='candidates')
    status = models.PositiveSmallIntegerField(
        choices=OrderStatuses.choices, default=OrderStatuses.DRAFT
    )

    def get_chat(self, user):
        return self.chat_set.get_or_create(order=self, candidate=user)[0]

    def to_status(self, status):
        self.status = status
        self.save(update_fields=['status'])
        if status == OrderStatuses.STARTED:
            self.group_message(msg_type=MessageTypes.STATUS, message='Выбран кандидат')
            self.chat_set.get(candidate=self.candidate).group_message(
                msg_type=MessageTypes.STATUS, message="Вас выбрали исполнителем", writable=True
            )
        elif status == OrderStatuses.ON_HOLD:
            self.group_message(msg_type=MessageTypes.STATUS, message='Заказ приостановлен')
        elif status == OrderStatuses.PUBLISHED:
            self.group_message(msg_type=MessageTypes.STATUS, message='Снова можно писать')

    def group_message(self, **kwargs):
        for chat in self.chat_set.all():
            chat.message_set.create(**kwargs)
        kwargs['timestamp'] = timezone.now().isoformat()
        async_to_sync(channel_layer.group_send)(self.group_name, kwargs)

    @property
    def group_name(self):
        return "order-%s" % self.id


class Chat(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidate_chats')
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name

    def is_writable(self, user):
        if self.order.status == OrderStatuses.STARTED.value and self.order.candidate != user and self.order.user != user:
            return False
        if self.rejected and self.order.user != user:
            return False
        if self.order.candidate and self.order.candidate != user and self.order.user != user:
            return False
        return True

    @property
    def group_name(self):
        return "chat-%s" % self.id

    def reject(self):
        self.rejected = True
        self.save(update_fields=['rejected'])
        self.message_set.create(
            msg_type=MessageTypes.STATUS, user=self.order.user, message='Вам отказали'
        ).send()

    def approve(self):
        self.order.candidate = self.candidate
        self.order.save(update_fields=['candidate'])
        self.message_set.create(
            msg_type=MessageTypes.STATUS, user=self.order.user, message='Ваc выбрали исполнителем'
        ).send()

    def group_message(self, **kwargs):
        msg = self.message_set.create(**kwargs)
        async_to_sync(channel_layer.group_send)(self.group_name, msg.to_json())


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    msg_type = models.PositiveSmallIntegerField(choices=MessageTypes.choices, default=MessageTypes.MESSAGE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(null=True, blank=True)
    unread = models.BooleanField(default=True)

    def to_json(self):
        return {
            "msg_type": self.msg_type,
            "username": self.user and self.user.username,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "unread": self.unread,
        }

    def send(self):
        async_to_sync(channel_layer.group_send)(self.chat.group_name, self.to_json())

    class Meta:
        ordering = ['timestamp']
