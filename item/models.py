from django.db import models
import random

from user.models import User


class Category(models.Model):
    title = models.CharField(max_length=100)


class Tag(models.Model):
    tag = models.CharField(max_length=100)


def get_item_image_path(instance, filename):
    filename = str(random.randint(10000, 100000)) + filename
    path = 'item_images/%s' % (filename)
    return path


class Item(models.Model):
    categories = models.ManyToManyField(Category, related_name='items')
    tags = models.ManyToManyField(Tag, related_name='items')
    title = models.CharField(max_length=100)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    price = models.IntegerField(default=0)
    # pip install Pillow 이미지 기능을 사용하기 위해 설치
    image = models.ImageField(upload_to=get_item_image_path)


class UserItem(models.Model):
    user = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)


class History(models.Model):
    user = models.ForeignKey(User, related_name='histories', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    is_refunded = models.BooleanField(default=False)


class HistoryItem(models.Model):
    history = models.ForeignKey(History, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)