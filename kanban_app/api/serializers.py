from rest_framework import serializers
from kanban_app.models import Board, Task, Comment

class BoardSerializer(serializers.ModelSerializer):
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']
        read_only_fields = ['id', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']

    def get_ticket_count(self, obj):
        return Task.objects.filter(board=obj).count()
    
    def get_tasks_to_do_count(self, obj):
        return Task.objects.filter(board=obj, status='todo').count()
    
    def get_tasks_high_prio_count(self, obj):
        return Task.objects.filter(board=obj, priority='high').count()
        


class TaskSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all()
    )

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority']
        read_only_fields = ['id', 'board']


   


class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField()