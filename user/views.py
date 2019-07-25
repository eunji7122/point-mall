from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from rest_framework.decorators import action
from item.serializers import UserItemSerializer
from rest_framework.response import Response


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True)
    def items(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserItemSerializer(user.items.all(), many=True)
        return Response(serializer.data)