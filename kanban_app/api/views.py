from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from kanban_app.models import Board, Task, Comment
from .serializers import BoardSerializer, TaskSerializer, CommentSerializer


@api_view(['GET', 'POST'])
def board_list(request):
    if request.method == 'GET':
        boards = Board.objects.all()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=200)

    if request.method == 'POST':
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def board_detail(request, pk):
    if request.method == 'GET':
        board = Board.objects.get(pk=pk)
        serializer = BoardSerializer(board)
        return Response(serializer.data, status=200)
    
    if request.method == 'PUT':
        board = Board.objects.get(pk=pk)
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
    
    if request.method == 'DELETE':
        board = Board.objects.get(pk=pk)
        serializer = BoardSerializer(board)
        board.delete()
        return Response(serializer.data, status=204)


@api_view(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=200)

    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, pk):
    if request.method == 'GET':
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=200)
    
    if request.method == 'PUT':
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
    
    if request.method == 'DELETE':
        task = Task.objects.get(pk=pk)
        task.delete()
        return Response(status=204)
    

# class BoardList(generics.ListCreateAPIView):
#     pass

# class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
#     pass

class AssignedTaskList(generics.ListCreateAPIView):
    pass

class ReviewingTaskList(generics.ListCreateAPIView):
    pass

# class TaskList(generics.ListCreateAPIView):
#     pass

# class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
#     pass

class CommentsList(generics.ListCreateAPIView):
    pass

class CommentsDetail(generics.RetrieveUpdateDestroyAPIView):
    pass
