from django.dispatch import Signal

notification_received = Signal()  # webhook message v0
"""
Sent when received new webhook message.

Deprecated.

    Args:
        - sender: set to None
        - name: Webhook message type
        - data: Webhook message received payload
"""

webhook_message_received = Signal()  # webhook message v1
"""
Sent when received new webhook message

    Args:
        - sender: set to None
        - type: Webhook message type
        - data: Webhook message data
        - id: Webhook message id
        - created_at: Webhook message creation datetime
"""
