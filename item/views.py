from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from item.permissions import IsPurchase, IsSafeMethod
from rest_condition import Or, And
from .models import Item, UserItem, Category
from .serializers import ItemSerializer, UserItemSerializer, CategorySerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = (Or(IsSafeMethod, permissions.IsAdminUser, And(IsPurchase, permissions.IsAuthenticated)),)

    # detail=True /items/1/purchase
    # detail=False /items/purchase
    @action(detail=True, methods=['POST'])
    def purchase(self, request, *args, **kwargs):
        item = self.get_object()
        # item = self.queryset.get(pk=kwargs['pk']) 윗줄과 같은 의미
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

    @action(detail=False, methods=['POST'], url_path='purchase')
    @transaction.atomic()
    def purchase_items(self, request, *args, **kwargs):
        user = request.user
        items = request.data['items']

        sid = transaction.savepoint()

        for i in items:
            item = Item.objects.get(id=i['item_id'])
            count = int(i['count'])

            if item.price * count > user.point:
                transaction.savepoint_rollback(sid)
                return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
            user.point -= item.price * count
            user.save()

            try:
                user_item = UserItem.objects.get(user=user, item=item)
            except UserItem.DoesNotExist:
                user_item = UserItem(user=user, item=item)
            user_item.count += count
            user_item.save()

        transaction.savepoint_commit(sid)
        serializer = UserItemSerializer(user.items.all(), many=True)

        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True)
    def items(self, request, *args, **kwargs):
        category = self.get_object()
        # 이미지 경로가 media부터 시작함
        # serializer = ItemSerializer(category.items.all(), many=True)

        # 이미지 경로가 url임
        serializer = ItemSerializer(category.items.all(), many=True, context=self.get_serializer_context())
        return Response(serializer.data)
