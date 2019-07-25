from rest_framework import serializers
from .models import Item, UserItem


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'created', 'price', 'image']


class UserItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = UserItem
        fields = ['item', 'user', 'count']