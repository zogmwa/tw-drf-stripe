from rest_framework import permissions

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class AllowAnonymousReadsAndOwnerWrites(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        user = request.user
        if obj.user_id == user.id or (user.is_staff or user.is_superuser):
            return True

        return False
