from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from kanban_app.models import Board, Task, Comment
from .serializers import BoardSerializer, BoardDetailSerializer, BoardCreateSerializer, BoardPartialUpdateSerializer, TaskSerializer, TaskPartialUpdateSerializer, CommentSerializer
from .permissions import IsBoardOwnerOrMember, IsTaskOwnerOrBoardMember

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    create_serializer_class = BoardCreateSerializer
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]

    detail_serializer_class = BoardDetailSerializer
    partial_update_serializer_class = BoardPartialUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        qs_owner  = Board.objects.filter(owner_id=user)
        qs_member = Board.objects.filter(members=user)
        return (qs_owner | qs_member).distinct()
    
    def get_object(self):
        obj = get_object_or_404(Board, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        if self.action == 'partial_update':
            return self.partial_update_serializer_class
        if self.action == 'create':
            return self.create_serializer_class
        return super().get_serializer_class()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner_id=request.user)

        output = BoardSerializer(board, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    partial_update_serializer_class = TaskPartialUpdateSerializer
    permission_classes = [IsTaskOwnerOrBoardMember]


    def get_serializer_class(self):
        if self.action == 'partial_update':
            return self.partial_update_serializer_class
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)       

class AssignedTaskList(generics.ListAPIView):
    serializer_class = TaskSerializer  

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)

class ReviewingTaskList(generics.ListAPIView):
    serializer_class = TaskSerializer  

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)

class CommentsViewSet(viewsets.ModelViewSet):  
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer 

    def get_queryset(self):
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        serializer.save(task=task, author=self.request.user)