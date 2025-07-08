from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics, viewsets
from kanban_app.models import Board, Task, Comment
from .serializers import BoardSerializer, BoardDetailSerializer, BoardPartialUpdateSerializer, TaskSerializer, TaskPartialUpdateSerializer, CommentSerializer

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    detail_serializer_class = BoardDetailSerializer
    patch_serializer_class = BoardPartialUpdateSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        if self.action == 'partial_update':
            return self.patch_serializer_class
        return super().get_serializer_class() 

class TaskViewSet(viewsets.ModelViewSet):    
    queryset = Task.objects.all()
    serializer_class = TaskSerializer   

    partial_update_serializer_class = TaskPartialUpdateSerializer

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return self.partial_update_serializer_class
        return super().get_serializer_class()


class AssignedTaskList(generics.ListCreateAPIView):
    pass

class ReviewingTaskList(generics.ListCreateAPIView):
    pass




class CommentsViewSet(viewsets.ModelViewSet):  
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer 

    def get_queryset(self):
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        # serializer.save(task=task, author=self.request.user) 
        serializer.save(task=task)