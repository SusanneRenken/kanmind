from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import (
    BoardViewSet,
    TaskViewSet,
    CommentsViewSet,
    AssignedTaskList,
    ReviewingTaskList
)

# Main router for boards and tasks
router = routers.SimpleRouter()
router.register(r'boards', BoardViewSet)
router.register(r'tasks', TaskViewSet)

# Nested router for task comments
tasks_router = nested_routers.NestedSimpleRouter(router, r'tasks', lookup='task')
tasks_router.register(r'comments', CommentsViewSet, basename='task-comments')

urlpatterns = [
    # Custom task views for assignee and reviewer
    path('tasks/assigned-to-me/', AssignedTaskList.as_view(), name='assigned-tasks'),
    path('tasks/reviewing/', ReviewingTaskList.as_view(), name='reviewing-tasks'),

    # Standard routes from routers
    path('', include(router.urls)),
    path('', include(tasks_router.urls)),
]