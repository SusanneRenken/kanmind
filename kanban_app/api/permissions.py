from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrMember(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method == 'DELETE':
            return obj.owner_id == user

        if request.method in SAFE_METHODS | {'PUT', 'PATCH'}:
            return (
                obj.owner_id == user or
                obj.members.filter(pk=user.pk).exists()
            )

        return False