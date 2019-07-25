from django.db import models
from user.models import User

class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    price = models.IntegerField(default=0)
    # pip install Pillow 이미지 기능을 사용하기 위해 설치
    image = models.ImageField(upload_to='uploads/item_images/')


class UserItem(models.Model):
    user = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)