from email import message
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate
import pytz

from .models import User, Message

from uuid import uuid4
from datetime import datetime, timedelta


###################
# User Serializer #
###################
class UserSerializer(serializers.ModelSerializer):

    id          = serializers.UUIDField(format="hex_verbose", read_only=True)
    email_id    = serializers.EmailField()
    first_name  = serializers.CharField(max_length=20)
    last_name   = serializers.CharField(max_length=20)
    password    = serializers.CharField(max_length=50,write_only=True)
    is_active   = serializers.BooleanField()
    admin       = serializers.BooleanField()
    staff       = serializers.BooleanField()

    class Meta:
        model=User
        fields=[

            'id',
            'email_id',
            'first_name',
            'last_name',
            'password',
            'is_active',
            'admin',
            'staff'
        ]

    #######################
    # Validation of Email #
    #######################
    def validate_email_id(self,value:str)->str:
        queryset=None

        if self.context.get('view').request.method =="POST":

            queryset=User.objects.filter(email_id=value)

        if queryset.exists():
            raise serializers.ValidationError("User With this Email already exists")

        return value

    def create(self, validated_data):
        validated_data['id']=uuid4()
        return User.objects.create(**validated_data)


#####################
# SignIn Serializer #
#####################
class SignInSerializer(serializers.ModelSerializer):

    id         = serializers.UUIDField(read_only=True,format="hex_verbose")
    email_id   = serializers.EmailField(max_length=255)
    password   = serializers.CharField(max_length=50, write_only=True)
    token      = serializers.SerializerMethodField()
    message    = serializers.SerializerMethodField()

    class Meta:
        model=User
        fields=['id','email_id','password','token','message']

    ###############################
    # Authenticating User #
    ###############################
    def validate(self,data):
        request=self.context.get('view').request

        self.user=authenticate(request,email_id=data.get('email_id').lower(),password=data.get('password'))

        if self.user is None:
            raise serializers.ValidationError("Please Enter Valid Credentials")

        return data

    def get_token(self, instance:User)->str:
        return instance.auth_token.key

    def get_message(self, instance)->str:
        return 'Singin Successfully'

    def create(self, validated_data):

        if hasattr(self.user, 'auth_token'):

            self.user.auth_token.delete()

        Token.objects.create(user=self.user)

        return self.user


##########################
# Serializer For Message #
##########################
class MessageSerializer(serializers.ModelSerializer):

    id                 = serializers.UUIDField(read_only=True, format="hex_verbose")
    message: str       = serializers.CharField(max_length=500)
    created_at: str    = serializers.DateTimeField(read_only=True)
    updated_at: str    = serializers.DateTimeField(read_only=True)
    created_by         = serializers.SerializerMethodField()

    class Meta:
        model=Message
        fields=['id','message','created_at','updated_at', 'created_by']

    def validate(self, data):

        one_hours_ago = (datetime.now() - timedelta(hours=1)).astimezone(pytz.utc)

        no_of_message = Message.objects.filter(
            my_user=self.context.get('view').request.user,
            created_at__gte=one_hours_ago
        ).count()

        if no_of_message>=10:
            raise serializers.ValidationError("Message Limit has been Exceed. You cannot insert more than 10 messages per hour.")
        else:
            return  data

    def create(self, validated_data):
        validated_data['id'] = uuid4()
        validated_data['my_user'] = self.context.get('view').request.user
        return Message.objects.create(**validated_data)

    def get_created_by(self, instance):

        result = {
            "id": self.context.get('view').request.user.id,
            "username" : self.context.get('view').request.user.first_name + ' ' + self.context.get('view').request.user.last_name,
            "email" : self.context.get('view').request.user.email_id
        }

        return result
