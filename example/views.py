from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.authentication import TokenAuthentication

from .serializer import SignInSerializer, UserSerializer, MessageSerializer
from .models import User, Message


###############
# Sign UP View
###############
class SignUpAPIView(CreateAPIView):
    serializer_class=UserSerializer
    permission_classes=[AllowAny]

    def get_serializer_context(self):
        return {'view':self}

    def perform_create(self,serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save()


##############
# Log In View
##############
class  LogInAPIView(CreateAPIView):
    serializer_class=SignInSerializer
    permission_classes=[AllowAny]

    def get_serializer_context(self):
        return {'view':self}

    def perform_create(self, serializer):

        if serializer.is_valid(raise_exception=True):
            serializer.save()

#################
# View OF Message
#################
class CreateMessageAPIView(CreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=MessageSerializer
    authentication_class=[TokenAuthentication]

    def get_serializer_context(self):
        return {'view':self}

    def perform_create(self,serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save()
