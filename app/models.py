import uuid
from datetime import datetime
from tortoise.models import Model
from tortoise import fields


class Payment(Model):

    uuid = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    date = fields.DatetimeField(null=True, default=datetime.now)
    document = fields.CharField(max_length=200, null=True, unique=True)
    beneficiary = fields.CharField(max_length=200)
    amount = fields.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        table = "payments"


class User(Model):

    uuid = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True, null=True)
    hashed_password = fields.CharField(max_length=128)
    disabled = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def dict(self, *args, **kwargs):
        return {
            "username": self.username,
            "email": self.email,
        }

    def full_dict(self, *args, **kwargs):
        return {
            "id": self.uuid,
            "username": self.username,
            "email": self.email,
            "disabled": self.disabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class ApiKey(Model):

    uuid = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="apikeys")
    hashed_key = fields.CharField(max_length=128)
    key_prefix = fields.CharField(max_length=10)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "apikeys"
