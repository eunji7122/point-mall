from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Item, UserItem
from .serializers import ItemSerializer, UserItemSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['POST'])
    def purchase(self, request, *args, **kwargs):
        item = self.get_object()
        user = request.user

        if item.price > user.point:
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        user.point -= item.price
        user.save()

        try:
            user_item = UserItem.objects.get(user=user, item=item)
        except UserItem.DoesNotExist:
            user_item = UserItem(user=user, item=item)
        user_item.count += 1
        user_item.save()

        serializer = UserItemSerializer(user.items.all(), many=True)
        return Response(serializer.data)