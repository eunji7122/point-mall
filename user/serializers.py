from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    # 비밀번호는 변경할 수 없도록 write_only 속성 사용
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'point', 'password']