from api.v1.serializers.user_serializers import UserRegisterSerializer, UserSerializer
from person.models import User
from rest_framework import status, viewsets
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRegisterViewSet(CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"message": "Registration completed successfully. Now login!"}, status=status.HTTP_200_OK
            )
        return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
