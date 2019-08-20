from rest_framework import serializers
from .models import Item, UserItem, Category, HistoryItem, History, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tag']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class ItemSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'title', 'tags', 'description', 'categories', 'created', 'price', 'image']


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
        fields = ['id', 'user', 'created', 'is_refunded', 'items']
