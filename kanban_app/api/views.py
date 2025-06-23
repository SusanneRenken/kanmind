from rest_framework import generics

class BoardList(generics.ListCreateAPIView):
    pass

class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    pass

class AssignedTaskList(generics.ListCreateAPIView):
    pass

class ReviewingTaskList(generics.ListCreateAPIView):
    pass

class TaskList(generics.ListCreateAPIView):
    pass

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    pass

class CommentsList(generics.ListCreateAPIView):
    pass

class CommentsDetail(generics.RetrieveUpdateDestroyAPIView):
    pass
