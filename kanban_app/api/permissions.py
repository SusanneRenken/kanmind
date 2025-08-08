from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanban_app.models import Board, Task


class IsBoardOwnerOrMember(BasePermission):
    """Allow read/update for board owner or members; delete only for owner; create for any auth user."""

    def has_permission(self, request, view):
        """Allow POST for authenticated users; otherwise defer to object check."""
        if request.method == 'POST':
            return bool(request.user and request.user.is_authenticated)
        return True

    def has_object_permission(self, request, view, obj):
        """Check membership/ownership per method semantics."""
        user = request.user
        if request.method in set(SAFE_METHODS) | {'PUT', 'PATCH'}:
            return obj.owner_id == user or obj.members.filter(pk=user.pk).exists()
        if request.method == 'DELETE':
            return obj.owner_id == user
        return False


class IsTaskOwnerOrBoardMember(BasePermission):
    """
    Create: requester must be board member/owner of provided board.
    Read/Update: board members/owner.
    Delete: task creator or board owner.
    """

    def has_permission(self, request, view):
        """For POST ensure requester belongs to the target board; else allow and defer to object check."""
        if request.method == 'POST':
            board_id = request.data.get('board')
            if not board_id:
                return False
            board = get_object_or_404(Board, pk=board_id)
            user = request.user
            return board.members.filter(pk=user.pk).exists() or board.owner_id == user
        return True

    def has_object_permission(self, request, view, obj: Task):
        """Enforce member/owner for read/update, and creator/owner for delete. Validate assignee/reviewer membership."""
        user = request.user
        is_member = obj.board.members.filter(
            pk=user.pk).exists() or obj.board.owner_id == user
        if request.method in SAFE_METHODS or request.method in ('PUT', 'PATCH'):
            if not is_member:
                return False
            for field in ('assignee_id', 'reviewer_id'):
                if field in request.data:
                    u = User.objects.filter(pk=request.data[field]).first()
                    if not u:
                        return False
                    if not (obj.board.members.filter(pk=u.pk).exists() or obj.board.owner_id == u):
                        return False
            return True
        if request.method == 'DELETE':
            return request.user == obj.created_by or obj.board.owner_id == request.user
        return False


class IsCommentOwnerOrBoardMember(BasePermission):
    """GET/POST: board members/owner of the task's board; DELETE: only the comment author."""

    def has_permission(self, request, view):
        """For list/create ensure requester is member/owner of the task's board."""
        if request.method in ('GET', 'POST'):
            task_pk = view.kwargs.get('task_pk')
            task = get_object_or_404(Task, pk=task_pk)
            user = request.user
            return task.board.members.filter(pk=user.pk).exists() or task.board.owner_id == user
        return True

    def has_object_permission(self, request, view, obj):
        """Only the author may delete; safe methods already allowed by has_permission."""
        if request.method == 'DELETE':
            return obj.author == request.user
        if request.method in SAFE_METHODS:
            return True
        return False
