from rest_framework import permissions

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class AssetPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        user = request.user

        if user.is_staff or user.is_superuser:
            return True

        if obj.owner is not None:
            return bool(user == obj.owner)
        else:
            return bool(user == obj.submitted_by)
