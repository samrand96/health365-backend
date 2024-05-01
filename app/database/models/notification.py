from tortoise import Model,fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Notification(Model):
    id = fields.IntField(pk=True)
    sender = fields.ForeignKeyField('models.User', related_name='notifications')
    receiver = fields.ForeignKeyField('models.User', related_name='notifications')
    message = fields.CharField(max_length=255)
    read_status = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

Notification_Pydantic = pydantic_model_creator(Notification, name='Notification')
NotificationIn_Pydantic = pydantic_model_creator(Notification, name='NotificationIn', exclude_readonly=True)
