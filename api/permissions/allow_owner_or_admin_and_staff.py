from rest_framework import permissions

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class AllowOwnerOrAdminOrStaff(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.user_id == user.id or (user.is_staff or user.is_superuser):
            return True
        return False
