from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from item.permissions import IsPurchase, IsSafeMethod
from rest_condition import Or, And
from .models import Item, UserItem, Category, History, HistoryItem, Tag
from .serializers import ItemSerializer, UserItemSerializer, CategorySerializer, HistorySerializer, TagSerializer
from rest_framework.views import APIView


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    # permission_classes의 값이 최종적으로 True면 구매메소드에 접근하고, False면 접근하지 않음
    permission_classes = (Or(IsSafeMethod,
                             permissions.IsAdminUser,
                             And(IsPurchase, permissions.IsAuthenticated)),
                          )

    def perform_create(self, serializer):
        item = serializer.save()
        category_ids = self.request.data['category_ids'].split(',')
        categories = Category.objects.filter(id__in=category_ids)
        item.categories.set(categories)

        tags = self.request.data['tags'].split(',')
        for tag in tags:
            tag, is_created = Tag.objects.get_or_create(tag=tag)
            item.tags.add(tag)

    def perform_update(self, serializer):
        item = serializer.save()
        category_ids = self.request.data['category_ids'].split(',')
        categories = Category.objects.filter(id__in=category_ids)
        item.categories.set(categories)

        tags = self.request.data['tags'].split(',')
        tag_list = []
        for tag in tags:
            tag, is_created = Tag.objects.get_or_create(tag=tag)
            tag_list.append(tag)
        item.tags.set(tag_list)

    @action(detail=True, methods=['POST', 'DELETE'])
    def tags(self, request, *args, **kwargs):
        item = self.get_object()
        if request.method == 'POST':
            for tag in request.data['tags']:
                tag, is_created = Tag.objects.get_or_create(tag=tag)
                item.tags.add(tag)
        elif request.method == 'DELETE':
            for tag in request.data['tags']:
                try:
                    tag = Tag.objects.get(tag=tag)
                    item.tags.remove(tag)
                except Tag.DoesNotExist:
                    pass
        return Response(self.get_serializer(item).data)

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

        history = History(user=request.user)
        history.save()
        HistoryItem(history=history, item=item, count=1).save()

        serializer = UserItemSerializer(user.items.all(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='purchase')
    @transaction.atomic()
    def purchase_items(self, request, *args, **kwargs):
        user = request.user
        items = request.data['items']

        sid = transaction.savepoint()

        history = History(user=request.user)
        history.save()

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
            HistoryItem(history=history, item=item, count=count).save()

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


class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return History.objects.filter(user=self.request.user).order_by('-id')

    @action(detail=True, methods=['POST'])
    def refund(self, request, *args, **kwargs):
        history = self.get_object()
        user = request.user

        # history에서 접근 권한이 없는 유저를 거름
        if history.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        elif history.is_refunded:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        for history_item in history.items.all():
            try:
                # 개수 차감
                user_item = UserItem.objects.get(user=user, item=history_item.item)
                user_item.count -= history_item.count

                if user_item.count > 0:
                    user_item.save()
                else:
                    user_item.delete()

                # 포인트 되돌려줌
                user.point += history_item.item.price * history_item.count
            except UserItem.DoesNotExist:
                pass
        history.is_refunded = True
        history.save()
        user.save()

        serializer = self.get_serializer(history)
        return Response(serializer.data)


class TagItems(APIView):
    def get(self, request, tag):
        items = []
        try:
            tag = Tag.objects.get(tag=tag)
            items = tag.items.all()
        except Tag.DoesNotExist:
            pass
        return Response(ItemSerializer(items, many=True, context={'request': request}).data)
