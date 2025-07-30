from django.urls import path, include
from .views import BoardViewSet, TaskViewSet, CommentsViewSet, AssignedTaskList, ReviewingTaskList
from rest_framework import routers
from rest_framework_nested import routers as nested_routers

router = routers.SimpleRouter()
router.register(r'boards', BoardViewSet)
router.register(r'tasks', TaskViewSet)

tasks_router = nested_routers.NestedSimpleRouter(router, r'tasks', lookup='task')
tasks_router.register(r'comments', CommentsViewSet, basename='task-comments')

urlpatterns = [
    path('tasks/assigned-to-me/', AssignedTaskList.as_view(), name='assigned-tasks'),
    path('tasks/reviewing/', ReviewingTaskList.as_view(), name='reviewing-tasks'),

    path('', include(router.urls)),
    path('', include(tasks_router.urls)),
]