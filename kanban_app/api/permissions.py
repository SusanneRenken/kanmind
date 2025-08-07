from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from kanban_app.models import Board, Task

class IsBoardOwnerOrMember(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return bool(request.user and request.user.is_authenticated)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in set(SAFE_METHODS) | {'PUT', 'PATCH'}:
            return (
                obj.owner_id == user or
                obj.members.filter(pk=user.pk).exists()
            )
        
        if request.method == 'DELETE':
            return obj.owner_id == user

        return False
    
class IsTaskOwnerOrBoardMember(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            board_id = request.data.get('board')
            if not board_id:
                return False
            board = get_object_or_404(Board, pk=board_id)
            return (
                board.members.filter(pk=request.user.pk).exists() or
                board.owner_id == request.user
            )
        return True

    def has_object_permission(self, request, view, obj: Task):
        user = request.user

        if request.method in list(SAFE_METHODS) + ['PUT', 'PATCH']:
            if not (obj.board.members.filter(pk=user.pk).exists()
                    or obj.board.owner_id == user):
                return False

            for field, rel in (('assignee_id','assignee'),
                               ('reviewer_id','reviewer')):
                if field in request.data:
                    try:
                        u = User.objects.get(pk=request.data[field])
                    except User.DoesNotExist:
                        return False
                    if not (obj.board.members.filter(pk=u.pk).exists()
                            or obj.board.owner_id == u):
                        return False
            return True

        if request.method == 'DELETE':
            return (
                request.user == obj.created_by
                or obj.board.owner_id == request.user
            )

        return False