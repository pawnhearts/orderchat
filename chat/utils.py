from channels.db import database_sync_to_async

from .exceptions import ClientError
from .models import Chat, Order


@database_sync_to_async
def get_chat_for_order_or_error(order_id, user):
    # Check if the user is logged in
    if not user.is_authenticated:
        raise ClientError("USER_HAS_TO_LOGIN")
    # Find the room they requested (by ID)
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        raise ClientError("ORDER_INVALID")
    # Check permissions
    if order.candidate and order.candidate != user:
        raise ClientError("ORDER_STOPPED")
    return order.get_chat(user)

async def get_chat_or_error(chat_id, user):
    # Check if the user is logged in
    if not user.is_authenticated:
        raise ClientError("USER_HAS_TO_LOGIN")
    # Find the room they requested (by ID)
    try:
        chat = await Chat.objects.select_related('order', 'order__candidate').aget(pk=chat_id)
    except Chat.DoesNotExist:
        raise ClientError("CHAT_INVALID")
    # Check permissions
    if chat.order.candidate_id and chat.order.candidate_id != user.id:
        raise ClientError("CHAT_STOPPED")
    return chat
