from django.contrib import admin
from .models import Message, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, Message
from django.contrib.auth import get_user_model

User = get_user_model()

admin.site.unregister(Group)

admin.site.register(User)
admin.site.register(Message)
