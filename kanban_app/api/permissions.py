from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.shortcuts import get_object_or_404
from kanban_app.models import Board

class IsBoardOwnerOrMember(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user and request.user.is_authenticated
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
            return board.members.filter(pk=request.user.pk).exists()
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in list(SAFE_METHODS) + ['PUT', 'PATCH']:
            if not obj.board.members.filter(pk=user.pk).exists():
                return False
            if request.method == 'PATCH' and 'board' in request.data:
                return False
            return True

        if request.method == 'DELETE':
            return obj.board.members.filter(pk=user.pk).exists()

        return False