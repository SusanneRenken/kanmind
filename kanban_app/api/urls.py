from django.urls import path
from .views import BoardList, BoardDetail, TaskList, TaskDetail, CommentsList, CommentsDetail, AssignedTaskList, ReviewingTaskList

urlpatterns = [
    path('boards/', BoardList.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetail.as_view(), name='board-detail'),
    path('tasks/assigned-to-me/', AssignedTaskList.as_view(), name='assigned-tasks'),
    path('tasks/reviewing/', ReviewingTaskList.as_view(), name='reviewing-tasks'),
    path('tasks/', TaskList.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('tasks/<int:pk>/comments/', CommentsList.as_view(), name='task-comments-list'),
    path('tasks/<int:task_pk>/comments/<int:pk>/', CommentsDetail.as_view(), name='task-comment-detail'),
]