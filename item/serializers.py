from rest_framework import serializers
from .models import Item, UserItem, Category, HistoryItem, History


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'category', 'category_id', 'created', 'price', 'image']


class UserItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = UserItem
        fields = ['item', 'user', 'count']


class HistoryItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = HistoryItem
        fields = ['history', 'item', 'count']


class HistorySerializer(serializers.ModelSerializer):
    items = HistoryItemSerializer(many=True)

    class Meta:
        model = History
        fields = ['user', 'created', 'is_refunded', 'items']
