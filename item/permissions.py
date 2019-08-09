from rest_framework import permissions


class IsPurchase(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(view.action in ('purchase', 'purchase_items'))


class IsSafeMethod(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS)