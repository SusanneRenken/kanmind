from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from kanban_app.models import Board, Task, Comment
from .serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardCreateSerializer,
    BoardPartialUpdateSerializer,
    TaskSerializer,
    TaskPartialUpdateSerializer,
    CommentSerializer
)
from .permissions import (
    IsBoardOwnerOrMember,
    IsTaskOwnerOrBoardMember,
    IsCommentOwnerOrBoardMember
)


class BoardViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Kanban boards.
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]

    detail_serializer_class = BoardDetailSerializer
    partial_update_serializer_class = BoardPartialUpdateSerializer
    create_serializer_class = BoardCreateSerializer

    def get_queryset(self):
        """
        Returns boards where the current user is either owner or member.
        """
        user = self.request.user
        return Board.objects.filter(owner_id=user).union(
            Board.objects.filter(members=user)
        ).distinct()

    def get_object(self):
        """
        Retrieves a specific board instance with permission check.
        """
        obj = get_object_or_404(Board, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        """
        Returns the appropriate serializer depending on the action.
        """
        if self.action == 'retrieve':
            return self.detail_serializer_class
        if self.action == 'partial_update':
            return self.partial_update_serializer_class
        if self.action == 'create':
            return self.create_serializer_class
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """
        Creates a new board and assigns the current user as owner.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner_id=request.user)
        output = BoardSerializer(board, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class TaskViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskOwnerOrBoardMember]
    partial_update_serializer_class = TaskPartialUpdateSerializer

    def get_serializer_class(self):
        """
        Returns the appropriate serializer depending on the action.
        """
        if self.action == 'partial_update':
            return self.partial_update_serializer_class
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """
        Saves the task with the current user as the creator.
        """
        serializer.save(created_by=self.request.user)


class AssignedTaskList(generics.ListAPIView):
    """
    Lists all tasks assigned to the current user.
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTaskList(generics.ListAPIView):
    """
    Lists all tasks where the current user is reviewer.
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class CommentsViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for task comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentOwnerOrBoardMember]

    def get_queryset(self):
        """
        Returns all comments for a given task.
        """
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        """
        Creates a comment and associates it with the task and user.
        """
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        serializer.save(task=task, author=self.request.user)
