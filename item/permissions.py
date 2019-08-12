from rest_framework import permissions


class IsPurchase(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(view.action in ('purchase', 'purchase_items'))


# 로그인 안한 사람도 아이템을 볼 수 있게 하기 위함
class IsSafeMethod(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS)