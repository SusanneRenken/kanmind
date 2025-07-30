from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from kanban_app.models import Board, Task, Comment
from .serializers import BoardSerializer, BoardDetailSerializer, BoardPartialUpdateSerializer, TaskSerializer, TaskPartialUpdateSerializer, CommentSerializer
from .permissions import IsOwnerOrMember

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    detail_serializer_class = BoardDetailSerializer
    partial_update_serializer_class = BoardPartialUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        qs_owner  = Board.objects.filter(owner_id=user)
        qs_member = Board.objects.filter(members=user)
        return (qs_owner | qs_member).distinct()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        if self.action == 'partial_update':
            return self.partial_update_serializer_class
        return super().get_serializer_class() 
    
    def perform_create(self, serializer):
        board = serializer.save(owner_id=self.request.user)
        member_ids = self.request.data.get('members', [])
        board.members.set(member_ids)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer   

    partial_update_serializer_class = TaskPartialUpdateSerializer

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return self.partial_update_serializer_class
        return super().get_serializer_class()

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