from rest_framework import permissions

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class AllowOwnerOrAdminOrStaff(permissions.IsAuthenticated):
    def _is_staff_or_admin(self, request) -> bool:
        return request.user.is_staff or request.user.is_superuser

    def has_permission(self, request, view):
        if view.action == 'list' and not self._is_staff_or_admin(request):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.id == user.id or self._is_staff_or_admin(request):
            return True
        return False
